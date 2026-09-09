"""Per-device, versioned UI calibration used by the custom publisher."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CalibrationError(RuntimeError):
    pass


class CalibrationStore:
    def __init__(self, root: Path):
        self.root = root

    def path_for(self, udid: str) -> Path:
        return self.root / f"{udid}.json"

    def load(self, udid: str) -> dict[str, Any]:
        path = self.path_for(udid)
        if not path.exists():
            raise CalibrationError(f"设备 {udid} 尚未校准：{path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CalibrationError(f"校准文件无效：{path}") from exc
        if payload.get("device_id") != udid:
            raise CalibrationError("校准文件的设备 ID 不匹配")
        if not isinstance(payload.get("steps"), list):
            raise CalibrationError("校准文件缺少 steps 数组")
        return payload
