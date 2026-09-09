import logging
import shutil
import subprocess
from dataclasses import asdict, dataclass


logger = logging.getLogger(__name__)


class DeviceDiscoveryError(RuntimeError):
    pass


@dataclass(frozen=True)
class Device:
    udid: str
    name: str
    status: str = "Online"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class DeviceManager:
    def _run(self, command: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
        logger.debug("Running device command: %s", command)
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    def list_devices(self) -> list[Device]:
        if not shutil.which("idevice_id"):
            raise DeviceDiscoveryError(
                "未找到 idevice_id。请先执行：brew install libimobiledevice"
            )

        try:
            result = self._run(["idevice_id", "-l"])
        except subprocess.TimeoutExpired as exc:
            raise DeviceDiscoveryError("读取 iPhone 列表超时") from exc

        if result.returncode != 0:
            raise DeviceDiscoveryError(
                f"idevice_id 执行失败：{result.stderr.strip() or result.stdout.strip()}"
            )

        udids = sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
        devices = [Device(udid=udid, name=self._device_name(udid)) for udid in udids]
        logger.info(
            "当前发现 %d 台设备: %s",
            len(devices),
            [{"name": item.name, "udid": item.udid} for item in devices],
        )
        return devices

    def _device_name(self, udid: str) -> str:
        if not shutil.which("ideviceinfo"):
            return "iPhone"

        try:
            result = self._run(["ideviceinfo", "-u", udid, "-k", "DeviceName"])
        except subprocess.TimeoutExpired:
            logger.warning("读取设备名称超时: udid=%s", udid)
            return "iPhone"

        name = result.stdout.strip()
        if result.returncode == 0 and name:
            return name

        logger.warning(
            "无法读取设备名称: udid=%s stderr=%s",
            udid,
            result.stderr.strip(),
        )
        return "iPhone"

    def require_online(self, udid: str) -> Device:
        for device in self.list_devices():
            if device.udid == udid:
                return device
        raise DeviceDiscoveryError(f"设备当前不在线或未受信任：{udid}")
