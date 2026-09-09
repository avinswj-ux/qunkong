#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -d .venv ]]; then
  echo "缺少 .venv，请先执行：python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "缺少 .env，请先执行：cp .env.example .env，然后填写 XCODE_ORG_ID。"
  exit 1
fi

set -a
source .env
set +a

APPIUM_SERVER_URL="${APPIUM_SERVER_URL:-http://127.0.0.1:4723}"
APPIUM_STATUS_URL="${APPIUM_SERVER_URL%/}/status"
APPIUM_PID=""

cleanup() {
  if [[ -n "$APPIUM_PID" ]]; then
    kill "$APPIUM_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if ! curl --silent --fail "$APPIUM_STATUS_URL" >/dev/null 2>&1; then
  if ! command -v appium >/dev/null 2>&1; then
    echo "找不到 appium，请执行：npm install --global appium"
    exit 1
  fi
  if [[ "$APPIUM_SERVER_URL" != "http://127.0.0.1:4723" && "$APPIUM_SERVER_URL" != "http://localhost:4723" ]]; then
    echo "自定义 APPIUM_SERVER_URL 当前不可访问，请先单独启动对应的 Appium Server。"
    exit 1
  fi
  appium --address 127.0.0.1 --port 4723 >.appium.log 2>&1 &
  APPIUM_PID=$!
  for _ in {1..30}; do
    curl --silent --fail "$APPIUM_STATUS_URL" >/dev/null 2>&1 && break
    sleep 1
  done
  if ! curl --silent --fail "$APPIUM_STATUS_URL" >/dev/null 2>&1; then
    echo "Appium 启动失败，请查看 $PROJECT_DIR/.appium.log"
    exit 1
  fi
fi

.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
