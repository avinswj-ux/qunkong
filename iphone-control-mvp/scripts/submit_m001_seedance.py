import json
import os
from pathlib import Path
from urllib import error, request


ROOT = Path("/Users/apple/Desktop/M-001-Imagine-分镜与提示词-重制版")
PACKAGE = ROOT / "03-视频生视频母版" / "M-001-Seedance2-提交包.md"
VIDEO1 = Path("/Users/apple/Downloads/M-001-Imagine-final-H3-hybrid-720x1280 (1).mp4")
IMAGE1 = ROOT / "03-视频生视频母版" / "M-001-银色四滚筒UI母版-v2.png"
ENDPOINT = "https://www.autodl.art/api/v1/ark/v3/contents/generations/tasks"


def load_prompt() -> str:
    text = PACKAGE.read_text(encoding="utf-8")
    return text.split("## 最终提示词", 1)[1].split("## 参数", 1)[0].strip()


token = os.environ["AUTODL_ARK_TOKEN"]
payload = {
    "model": "doubao-seedance-2-0-260128",
    "content": [
        {"type": "text", "text": load_prompt()},
        {
            "type": "video_url",
            "video_url": {"url": "https://litter.catbox.moe/jijh3n.mp4"},
            "role": "reference_video",
        },
        {
            "type": "image_url",
            "image_url": {"url": "https://litter.catbox.moe/ytps6x.png"},
            "role": "reference_image",
        },
        {
            "type": "image_url",
            "image_url": {"url": "https://litter.catbox.moe/i9c5kv.png"},
            "role": "reference_image",
        },
        {
            "type": "image_url",
            "image_url": {"url": "https://litter.catbox.moe/1vq4rt.png"},
            "role": "reference_image",
        },
        {
            "type": "image_url",
            "image_url": {"url": "https://litter.catbox.moe/8a32mt.png"},
            "role": "reference_image",
        },
    ],
    "duration": 15,
    "ratio": "9:16",
    "resolution": "720p",
    "generate_audio": False,
    "watermark": False,
}

body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = request.Request(
    ENDPOINT,
    data=body,
    method="POST",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    },
)

try:
    with request.urlopen(req, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
except error.HTTPError as exc:
    result = {
        "http_status": exc.code,
        "body": exc.read().decode("utf-8", errors="replace"),
    }

print(json.dumps(result, ensure_ascii=False))
