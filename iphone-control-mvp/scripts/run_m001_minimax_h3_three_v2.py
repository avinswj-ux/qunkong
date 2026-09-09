"""Run the three M-001 MiniMax H3 V2 prompts with focused negative constraints."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path


PROJECT = Path("/Users/apple/Documents/ChatGPT/群控/iphone-control-mvp")
sys.path.insert(0, str(PROJECT))

from app.video_generation import AutoDLClient, VideoGenerationService


PROMPT_FILE = Path("/Users/apple/Desktop/角色资产/M-001-MiniMax-H3三版15秒成品提示词-v2-强负面约束.md")
REF_DIR = Path("/Users/apple/Desktop/角色资产/M-001-h3-v2-refs")
OUTPUT_DIR = Path("/Users/apple/Desktop/抖音成片")
DATABASE = PROJECT / "data/video_generation.sqlite3"
WORKFLOW_ID = "minimax_h3_lightx2v_v5_15s"
POLL_SECONDS = 20
TIMEOUT_SECONDS = 40 * 60

CONFIG = {
    "影子扫描换装 V2": {
        "file": "m001-shadow-stylist-minimax-h3-v2.mp4",
        "refs": ["identity-front.png", "outfit-a-garment-only.jpg", "outfit-b.jpg"],
    },
    "电梯门遮挡换装 V2": {
        "file": "m001-elevator-outfit-box-minimax-h3-v2.mp4",
        "refs": ["identity-front.png", "outfit-a-garment-only.jpg", "outfit-b.jpg", "outfit-c.jpg", "outfit-d.jpg"],
    },
    "相纸遮镜换装 V2": {
        "file": "m001-instant-photo-double-minimax-h3-v2.mp4",
        "refs": ["identity-front.png", "outfit-d.jpg", "outfit-b.jpg"],
    },
}


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def parse_prompts() -> dict[str, str]:
    text = PROMPT_FILE.read_text(encoding="utf-8")
    found = re.findall(r"## 版本[一二三]｜([^\n]+)\s*```text\s*(.*?)\s*```", text, re.S)
    prompts = {title.strip(): prompt.strip() for title, prompt in found}
    if list(prompts) != list(CONFIG):
        raise RuntimeError(f"V2 提示词标题不匹配：{list(prompts)}")
    return prompts


def set_named_output(task_id: str, path: Path) -> None:
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            "UPDATE video_generation_tasks SET output_path=? WHERE task_id=?",
            (str(path.resolve()), task_id),
        )


def main() -> int:
    env = load_env(PROJECT / ".env")
    client = AutoDLClient(
        token=env.get("AUTODL_COMFYUI_TOKEN", ""),
        base_url=env.get("AUTODL_BASE_URL", "https://autodl.art"),
        timeout=180,
    )
    service = VideoGenerationService(DATABASE, OUTPUT_DIR, client)
    prompts = parse_prompts()
    submitted: list[dict[str, str]] = []

    for title, prompt in prompts.items():
        refs = CONFIG[title]["refs"]
        payload: dict[str, object] = {"prompt": prompt, "duration": 15, "resolution": "768p竖"}
        for index, filename in enumerate(refs):
            payload[f"ref_image_{index}"] = data_uri(REF_DIR / filename)
        task = service.submit(WORKFLOW_ID, payload)
        item = {"title": title, "task_id": task["task_id"], "file": str(CONFIG[title]["file"])}
        submitted.append(item)
        print(json.dumps({"event": "submitted", **item}, ensure_ascii=False), flush=True)

    pending = {item["task_id"]: item for item in submitted}
    started = time.monotonic()
    while pending:
        if time.monotonic() - started > TIMEOUT_SECONDS:
            print(json.dumps({"event": "timeout", "pending": list(pending)}, ensure_ascii=False), flush=True)
            return 2
        for task_id, item in list(pending.items()):
            task = service.refresh(task_id)
            status = task["status"]
            print(json.dumps({"event": "status", "title": item["title"], "task_id": task_id, "status": status}, ensure_ascii=False), flush=True)
            if status == "SUCCESS":
                source = Path(task["output_path"])
                named = OUTPUT_DIR / item["file"]
                if named.exists():
                    named.unlink()
                try:
                    os.link(source, named)
                except OSError:
                    shutil.copy2(source, named)
                set_named_output(task_id, named)
                print(json.dumps({"event": "downloaded", "title": item["title"], "task_id": task_id, "path": str(named)}, ensure_ascii=False), flush=True)
                pending.pop(task_id)
            elif status == "FAILED":
                print(json.dumps({"event": "failed", "title": item["title"], "task_id": task_id, "error": task.get("error")}, ensure_ascii=False), flush=True)
                pending.pop(task_id)
        if pending:
            time.sleep(POLL_SECONDS)

    print(json.dumps({"event": "complete", "tasks": submitted}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
