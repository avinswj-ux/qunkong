import asyncio
import hashlib
import logging
import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from appium import webdriver
from appium.options.ios import XCUITestOptions

from app.config import Settings
from app.device_manager import Device


logger = logging.getLogger(__name__)


class AppiumOperationError(RuntimeError):
    pass


@dataclass
class DeviceSession:
    udid: str
    wda_port: int
    mjpeg_port: int
    derived_data_path: Path
    driver: webdriver.Remote | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class AppiumManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._sessions: dict[str, DeviceSession] = {}
        self._allocation_lock = asyncio.Lock()

    @staticmethod
    def _port_available(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                return False
        return True

    async def _entry_for(self, udid: str) -> DeviceSession:
        async with self._allocation_lock:
            existing = self._sessions.get(udid)
            if existing:
                return existing

            used_ports = {
                port
                for entry in self._sessions.values()
                for port in (entry.wda_port, entry.mjpeg_port)
            }
            wda_port = self.settings.wda_local_port
            while wda_port in used_ports or not self._port_available(wda_port):
                wda_port += 1

            mjpeg_port = self.settings.wda_local_port + 1000
            while mjpeg_port in used_ports or not self._port_available(mjpeg_port):
                mjpeg_port += 1

            safe_id = hashlib.sha256(udid.encode("utf-8")).hexdigest()[:16]
            entry = DeviceSession(
                udid=udid,
                wda_port=wda_port,
                mjpeg_port=mjpeg_port,
                derived_data_path=self.settings.derived_data_root / safe_id,
            )
            self._sessions[udid] = entry
            logger.info(
                "为设备分配隔离资源: udid=%s wdaLocalPort=%d mjpegServerPort=%d derivedDataPath=%s",
                udid,
                wda_port,
                mjpeg_port,
                entry.derived_data_path,
            )
            return entry

    def _options(self, device: Device, entry: DeviceSession) -> XCUITestOptions:
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.automation_name = "XCUITest"
        options.udid = device.udid
        options.device_name = device.name
        options.no_reset = True
        options.new_command_timeout = 300
        options.set_capability("appium:wdaLocalPort", entry.wda_port)
        options.set_capability("appium:mjpegServerPort", entry.mjpeg_port)
        options.set_capability("appium:derivedDataPath", str(entry.derived_data_path))
        options.set_capability("appium:showXcodeLog", True)
        options.set_capability("appium:allowProvisioningUpdates", True)
        options.set_capability("appium:allowProvisioningDeviceRegistration", True)

        if self.settings.xcode_org_id and self.settings.xcode_signing_id:
            options.set_capability("appium:xcodeOrgId", self.settings.xcode_org_id)
            options.set_capability("appium:xcodeSigningId", self.settings.xcode_signing_id)
        if self.settings.wda_bundle_id:
            options.set_capability("appium:updatedWDABundleId", self.settings.wda_bundle_id)
        return options

    @staticmethod
    def _probe(driver: webdriver.Remote) -> dict[str, Any]:
        return driver.execute_script("mobile: deviceInfo")

    def _create_or_probe(self, device: Device, entry: DeviceSession) -> dict[str, Any]:
        if entry.driver is not None:
            try:
                device_info = self._probe(entry.driver)
                logger.info("复用 Appium session: udid=%s session=%s", device.udid, entry.driver.session_id)
                return device_info
            except Exception:
                logger.exception("已有 session 已失效，将重建: udid=%s", device.udid)
                try:
                    entry.driver.quit()
                except Exception:
                    logger.exception("清理失效 session 失败: udid=%s", device.udid)
                entry.driver = None

        entry.derived_data_path.mkdir(parents=True, exist_ok=True)
        logger.info(
            "开始创建 Appium XCUITest session: udid=%s server=%s wdaLocalPort=%d",
            device.udid,
            self.settings.appium_server_url,
            entry.wda_port,
        )
        driver = webdriver.Remote(
            command_executor=self.settings.appium_server_url,
            options=self._options(device, entry),
        )
        entry.driver = driver
        device_info = self._probe(driver)
        logger.info(
            "Appium session 创建成功，WDA 可连接: udid=%s session=%s",
            device.udid,
            driver.session_id,
        )
        return device_info

    async def test_connection(self, device: Device) -> dict[str, Any]:
        entry = await self._entry_for(device.udid)
        async with entry.lock:
            try:
                device_info = await asyncio.to_thread(self._create_or_probe, device, entry)
                return {
                    "message": "连接成功，WebDriverAgent 可用",
                    "udid": device.udid,
                    "session_id": entry.driver.session_id if entry.driver else None,
                    "wda_status": "Connected",
                    "wda_local_port": entry.wda_port,
                    "mjpeg_server_port": entry.mjpeg_port,
                    "device_info": device_info,
                }
            except Exception as exc:
                logger.exception("Appium/WDA 连接失败: udid=%s", device.udid)
                raise AppiumOperationError(self._friendly_error(exc)) from exc

    def _activate_douyin(self, device: Device, entry: DeviceSession) -> tuple[str, int]:
        self._create_or_probe(device, entry)
        assert entry.driver is not None
        logger.info(
            "准备启动抖音: udid=%s bundleId=%s session=%s",
            device.udid,
            self.settings.douyin_bundle_id,
            entry.driver.session_id,
        )
        entry.driver.execute_script(
            "mobile: launchApp",
            {"bundleId": self.settings.douyin_bundle_id},
        )
        state = int(
            entry.driver.execute_script(
                "mobile: queryAppState",
                {"bundleId": self.settings.douyin_bundle_id},
            )
        )
        if state != 4:
            raise RuntimeError(f"launchApp 已返回，但应用未处于前台，当前状态码={state}")
        logger.info("抖音启动成功: udid=%s", device.udid)
        return entry.driver.session_id, state

    async def open_douyin(self, device: Device) -> dict[str, Any]:
        if not self.settings.douyin_bundle_id:
            raise AppiumOperationError("DOUYIN_BUNDLE_ID 未配置")
        entry = await self._entry_for(device.udid)
        async with entry.lock:
            try:
                session_id, state = await asyncio.to_thread(self._activate_douyin, device, entry)
                return {
                    "message": "抖音已启动",
                    "udid": device.udid,
                    "session_id": session_id,
                    "app_state": state,
                }
            except Exception as exc:
                logger.exception("启动抖音失败: udid=%s", device.udid)
                raise AppiumOperationError(self._friendly_error(exc)) from exc

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        message = str(exc).strip() or exc.__class__.__name__
        lower = message.lower()
        if "connection refused" in lower or "max retries exceeded" in lower:
            return f"无法连接 Appium Server，请确认服务已启动。原始错误：{message}"
        if "xcode" in lower and ("not found" in lower or "requires xcode" in lower):
            return f"未找到可用的完整 Xcode。原始错误：{message}"
        if "provision" in lower or "signing" in lower or "code 65" in lower:
            return f"WebDriverAgent 签名或描述文件失败，请检查 Team、证书和设备注册。原始错误：{message}"
        if "developer mode" in lower:
            return f"iPhone Developer Mode 未启用。原始错误：{message}"
        return message

    async def close_all(self) -> None:
        for entry in list(self._sessions.values()):
            async with entry.lock:
                if entry.driver is None:
                    continue
                try:
                    await asyncio.to_thread(entry.driver.quit)
                    logger.info("Appium session 已关闭: udid=%s", entry.udid)
                except Exception:
                    logger.exception("关闭 Appium session 失败: udid=%s", entry.udid)
                finally:
                    entry.driver = None
