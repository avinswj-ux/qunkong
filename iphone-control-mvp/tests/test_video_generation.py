import json
from email.message import Message
from pathlib import Path

import pytest

from app.video_generation import (
    AutoDLClient,
    VideoGenerationNotConfigured,
    VideoGenerationService,
)


class FakeResponse:
    def __init__(self, body: bytes, content_type: str = "application/json"):
        self.body = body
        self.offset = 0
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self.body
        chunk = self.body[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


def test_client_requires_token() -> None:
    client = AutoDLClient(token="", opener=lambda *_args, **_kwargs: None)
    with pytest.raises(VideoGenerationNotConfigured):
        client.submit("workflow", {"prompt": "hello"})


def test_successful_task_downloads_into_publisher_inbox(tmp_path: Path) -> None:
    calls = []

    def opener(request, **_kwargs):
        calls.append((request.full_url, request.get_method()))
        if request.get_method() == "POST":
            body = {"code": "Success", "data": {"task_id": "task-1", "status": "QUEUED"}}
            return FakeResponse(json.dumps(body).encode())
        if "/result/" in request.full_url:
            body = {
                "code": "Success",
                "data": {"task_id": "task-1", "status": "SUCCESS", "results": [{"url": "https://cdn.example/video.mp4"}]},
            }
            return FakeResponse(json.dumps(body).encode())
        return FakeResponse(b"fake-mp4", "video/mp4")

    inbox = tmp_path / "inbox"
    service = VideoGenerationService(
        tmp_path / "generation.sqlite3",
        inbox,
        AutoDLClient(token="secret", opener=opener),
    )
    created = service.submit("minimax_h3_b99_001", {"prompt": "cat"})
    assert created["status"] == "QUEUED"

    completed = service.refresh("task-1")
    assert completed["status"] == "SUCCESS"
    assert Path(completed["output_path"]).read_bytes() == b"fake-mp4"
    assert json.loads((inbox / "autodl-task-1.mp4.json").read_text())["source"] == "autodl"
    assert [method for _, method in calls] == ["POST", "GET", "GET"]
