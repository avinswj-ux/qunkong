"""Submit, poll, and download the three approved M-001 MiniMax H3 concepts."""

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


PROMPT_FILE = Path("/Users/apple/Desktop/角色资产/M-001-MiniMax-H3三版15秒成品提示词-v1.md")
IDENTITY_IMAGE = Path("/Users/apple/Desktop/角色资产/M-001-face-anchor-approved.png")
OUTFIT_IMAGE = Path("/Users/apple/Desktop/角色资产/M-001-new-four-outfits-board.jpg")
OUTPUT_DIR = Path("/Users/apple/Desktop/抖音成片")
DATABASE = PROJECT / "data/video_generation.sqlite3"
WORKFLOW_ID = "minimax_h3_lightx2v_v5_15s"
POLL_SECONDS = 20
TIMEOUT_SECONDS = 40 * 60

SLUGS = {
    "影子比本人更会穿": "m001-shadow-stylist-minimax-h3.mp4",
    "电梯穿搭盲盒": "m001-elevator-outfit-box-minimax-h3.mp4",
    "自拍照片抢走本人": "m001-instant-photo-double-minimax-h3.mp4",
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


def parse_prompts(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    global_anchor_match = re.search(
        r"## 全局身份与外观锚点\s*(.*?)(?=\n---\n\n# 版本)", text, re.S
    )
    global_anchor = global_anchor_match.group(1).strip() if global_anchor_match else ""
    sections = re.findall(r"# 版本[一二三]｜([^\n]+)(.*?)(?=\n---\n\n# 版本|\Z)", text, re.S)
    prompts: list[tuple[str, str]] = []
    for raw_title, body in sections:
        title = raw_title.strip()
        prompt_match = re.search(r"## H3成品生成提示词\s*```text\s*(.*?)\s*```", body, re.S)
        negative_match = re.search(r"## 禁止项\s*(.*?)(?=\n---|\Z)", body, re.S)
        if not prompt_match:
            raise RuntimeError(f"未找到成品提示词：{title}")
        negative = negative_match.group(1).strip() if negative_match else ""
        prompt = (
            "【全局身份与外观锚点】\n"
            + global_anchor
            + "\n\n【本片时间轴与执行指令】\n"
            + prompt_match.group(1).strip()
            + "\n\n【强制禁止项】\n"
            + negative
        )
        prompts.append((title, prompt))
    if [title for title, _ in prompts] != list(SLUGS):
        raise RuntimeError(f"三版脚本标题不匹配：{[title for title, _ in prompts]}")
    return prompts


def update_named_output(task_id: str, named_output: Path) -> None:
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            "UPDATE video_generation_tasks SET output_path=? WHERE task_id=?",
            (str(named_output.resolve()), task_id),
        )


def main() -> int:
    env = load_env(PROJECT / ".env")
    token = env.get("AUTODL_COMFYUI_TOKEN", "")
    if not token:
        raise RuntimeError("AUTODL_COMFYUI_TOKEN 未配置")

    client = AutoDLClient(
        token=token,
        base_url=env.get("AUTODL_BASE_URL", "https://autodl.art"),
        timeout=180,
    )
    service = VideoGenerationService(DATABASE, OUTPUT_DIR, client)
    references = {
        "ref_image_0": data_uri(IDENTITY_IMAGE),
        "ref_image_1": data_uri(OUTFIT_IMAGE),
    }

    submitted: list[dict[str, str]] = []
    for title, prompt in parse_prompts(PROMPT_FILE):
        payload = {
            "prompt": prompt,
            "duration": 15,
            "resolution": "768p竖",
            **references,
        }
        task = service.submit(WORKFLOW_ID, payload)
        task_id = task["task_id"]
        submitted.append({"title": title, "task_id": task_id, "file": SLUGS[title]})
        print(json.dumps({"event": "submitted", **submitted[-1]}, ensure_ascii=False), flush=True)

    started = time.monotonic()
    pending = {item["task_id"]: item for item in submitted}
    while pending:
        if time.monotonic() - started > TIMEOUT_SECONDS:
            print(json.dumps({"event": "timeout", "pending": list(pending)}, ensure_ascii=False), flush=True)
            return 2
        for task_id, item in list(pending.items()):
            task = service.refresh(task_id)
            status = task["status"]
            print(
                json.dumps(
                    {"event": "status", "title": item["title"], "task_id": task_id, "status": status},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            if status == "SUCCESS":
                generated = Path(task["output_path"])
                named = OUTPUT_DIR / item["file"]
                if named.exists():
                    named.unlink()
                try:
                    os.link(generated, named)
                except OSError:
                    shutil.copy2(generated, named)
                update_named_output(task_id, named)
                print(
                    json.dumps(
                        {"event": "downloaded", "title": item["title"], "task_id": task_id, "path": str(named)},
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                pending.pop(task_id)
            elif status == "FAILED":
                print(
                    json.dumps(
                        {"event": "failed", "title": item["title"], "task_id": task_id, "error": task.get("error")},
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                pending.pop(task_id)
        if pending:
            time.sleep(POLL_SECONDS)

    print(json.dumps({"event": "complete", "tasks": submitted}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
