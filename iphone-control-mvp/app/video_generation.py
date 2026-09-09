"""AutoDL.Art ComfyUI video generation adapter and durable task ledger."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import urllib.error
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse


class VideoGenerationError(RuntimeError):
    pass


class VideoGenerationNotConfigured(VideoGenerationError):
    pass


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


class AutoDLClient:
    def __init__(
        self,
        *,
        token: str,
        base_url: str = "https://autodl.art",
        timeout: float = 30.0,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ):
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._opener = opener

    def _json_request(self, request: urllib.request.Request) -> dict[str, Any]:
        if not self.token:
            raise VideoGenerationNotConfigured("未配置 AUTODL_COMFYUI_TOKEN")
        try:
            with self._opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise VideoGenerationError(f"AutoDL 请求失败：{exc}") from exc
        if not isinstance(payload, dict) or payload.get("code") != "Success":
            message = payload.get("msg") if isinstance(payload, dict) else "响应格式无效"
            raise VideoGenerationError(f"AutoDL 返回错误：{message or payload}")
        return payload

    def submit(self, workflow_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if not workflow_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for char in workflow_id):
            raise VideoGenerationError("workflow_id 格式无效")
        body = json.dumps(parameters, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/v1/comfyui/comfyui_workflow/{workflow_id}",
            data=body,
            method="POST",
            headers={"Authorization": self.token, "Content-Type": "application/json"},
        )
        return self._json_request(request)["data"]

    def query(self, task_id: str) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.base_url}/api/v1/comfyui/comfyui_workflow/result/{task_id}",
            headers={"Authorization": self.token, "Content-Type": "application/json"},
        )
        return self._json_request(request)["data"]

    def download(self, url: str, destination: Path) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise VideoGenerationError("AutoDL 结果地址不是有效的 HTTPS URL")
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": "iphone-control-mvp/1.0"})
        temp_path: Path | None = None
        try:
            with self._opener(request, timeout=max(self.timeout, 120.0)) as response:
                content_type = response.headers.get_content_type()
                if content_type not in {"video/mp4", "application/octet-stream"}:
                    raise VideoGenerationError(f"AutoDL 结果不是 MP4：{content_type}")
                with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
                    temp_path = Path(handle.name)
                    while chunk := response.read(1024 * 1024):
                        handle.write(chunk)
            os.replace(temp_path, destination)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise VideoGenerationError(f"下载生成视频失败：{exc}") from exc
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()


class VideoGenerationService:
    def __init__(self, database_path: Path, inbox: Path, client: AutoDLClient):
        self.database_path = database_path
        self.inbox = inbox
        self.client = client
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS video_generation_tasks (
                    task_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    result_json TEXT NOT NULL DEFAULT '[]',
                    output_path TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def submit(self, workflow_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
        data = self.client.submit(workflow_id, parameters)
        task_id = str(data.get("task_id", ""))
        if not task_id:
            raise VideoGenerationError("AutoDL 未返回 task_id")
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO video_generation_tasks VALUES (?, ?, ?, ?, '[]', NULL, NULL, ?, ?)",
                (task_id, workflow_id, data.get("status", "QUEUED"), json.dumps(parameters, ensure_ascii=False), now, now),
            )
        return self.get(task_id)

    def refresh(self, task_id: str) -> dict[str, Any]:
        self.get(task_id)
        data = self.client.query(task_id)
        status = str(data.get("status", "UNKNOWN"))
        results = data.get("results") or []
        output_path = None
        error = data.get("message") if status == "FAILED" else None
        if status == "SUCCESS":
            video_url = self._find_video_url(results)
            if not video_url:
                raise VideoGenerationError("任务成功，但 results 中没有视频 URL")
            output = self.inbox / f"autodl-{task_id}.mp4"
            if not output.exists():
                self.client.download(video_url, output)
            output_path = str(output.resolve())
            sidecar = output.with_suffix(output.suffix + ".json")
            sidecar.write_text(json.dumps({"source": "autodl", "task_id": task_id}, ensure_ascii=False, indent=2), encoding="utf-8")
        with self._connect() as conn:
            conn.execute(
                "UPDATE video_generation_tasks SET status=?, result_json=?, output_path=?, error=?, updated_at=? WHERE task_id=?",
                (status, json.dumps(results, ensure_ascii=False), output_path, error, _utc_now(), task_id),
            )
        return self.get(task_id)

    @staticmethod
    def _find_video_url(value: Any) -> str | None:
        if isinstance(value, str) and value.startswith("https://") and (".mp4" in value.lower() or "video" in value.lower()):
            return value
        if isinstance(value, list):
            return next((found for item in value if (found := VideoGenerationService._find_video_url(item))), None)
        if isinstance(value, dict):
            return next((found for item in value.values() if (found := VideoGenerationService._find_video_url(item))), None)
        return None

    def get(self, task_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM video_generation_tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(task_id)
        item = dict(row)
        item["parameters"] = json.loads(item.pop("parameters_json"))
        item["results"] = json.loads(item.pop("result_json"))
        return item

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT task_id FROM video_generation_tasks ORDER BY created_at DESC").fetchall()
        return [self.get(row["task_id"]) for row in rows]
