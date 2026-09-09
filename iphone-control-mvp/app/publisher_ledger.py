"""Durable, multi-device-safe asset allocation for Douyin publishing.

This module deliberately owns *only* publishing state.  Phone interaction is
kept in a separate runner so two phones can never select the same video even
when their UI automation runs concurrently.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class LedgerError(RuntimeError):
    pass


class NoAvailableAsset(LedgerError):
    pass


@dataclass(frozen=True)
class ClaimedAsset:
    asset_id: str
    run_id: str
    device_id: str
    path: str
    metadata: dict[str, Any]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_metadata(video_path: Path) -> dict[str, Any]:
    """Read optional ``video.mp4.json`` metadata without exposing file paths."""
    sidecar = video_path.with_suffix(video_path.suffix + ".json")
    if not sidecar.exists():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerError(f"素材元数据无效：{sidecar.name}") from exc
    if not isinstance(data, dict):
        raise LedgerError(f"素材元数据必须是对象：{sidecar.name}")
    return data


class PublisherLedger:
    """SQLite-backed exclusive leasing with a cross-process transaction lock."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path, timeout=15, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    asset_id TEXT PRIMARY KEY,
                    path TEXT NOT NULL UNIQUE,
                    content_hash TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK(status IN
                        ('available', 'leased', 'prepared', 'published', 'needs_review')),
                    device_id TEXT,
                    run_id TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    leased_at TEXT,
                    published_at TEXT,
                    proof_json TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS assets_status_idx ON assets(status)")

    def _register_assets(self, conn: sqlite3.Connection, inbox: Path) -> None:
        if not inbox.is_dir():
            raise LedgerError(f"素材目录不存在：{inbox}")
        for video in sorted(inbox.glob("*.mp4")):
            content_hash = _file_hash(video)
            asset_id = content_hash[:24]
            conn.execute(
                """
                INSERT INTO assets(asset_id, path, content_hash, status, metadata_json, updated_at)
                VALUES (?, ?, ?, 'available', ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at
                WHERE assets.status='available'
                """,
                (
                    asset_id,
                    str(video.resolve()),
                    content_hash,
                    json.dumps(_load_metadata(video), ensure_ascii=False),
                    _utc_now(),
                ),
            )

    def claim_next(self, *, device_id: str, inbox: Path) -> ClaimedAsset:
        """Atomically lease exactly one never-published video for a device."""
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                self._register_assets(conn, inbox)
                row = conn.execute(
                    """
                    SELECT * FROM assets
                    WHERE status='available'
                    ORDER BY updated_at, path
                    LIMIT 1
                    """
                ).fetchone()
                if row is None:
                    raise NoAvailableAsset("没有可领取的未发布视频")
                run_id = str(uuid.uuid4())
                now = _utc_now()
                updated = conn.execute(
                    """
                    UPDATE assets
                    SET status='leased', device_id=?, run_id=?, leased_at=?, updated_at=?
                    WHERE asset_id=? AND status='available'
                    """,
                    (device_id, run_id, now, now, row["asset_id"]),
                )
                if updated.rowcount != 1:
                    raise LedgerError("素材领取冲突，请重试")
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
        return ClaimedAsset(
            asset_id=row["asset_id"],
            run_id=run_id,
            device_id=device_id,
            path=row["path"],
            metadata=json.loads(row["metadata_json"]),
        )

    def mark_prepared(self, *, run_id: str, device_id: str) -> None:
        self._transition(run_id, device_id, from_status="leased", to_status="prepared")

    def mark_needs_review(self, *, run_id: str, device_id: str, reason: str) -> None:
        self._transition(
            run_id,
            device_id,
            from_status=("leased", "prepared"),
            to_status="needs_review",
            proof={"reason": reason, "at": _utc_now()},
        )

    def mark_published(self, *, run_id: str, device_id: str, proof: dict[str, Any]) -> None:
        if not proof:
            raise LedgerError("必须提供发布成功凭据后才能标记已发布")
        self._transition(
            run_id,
            device_id,
            from_status="prepared",
            to_status="published",
            proof=proof,
        )

    def _transition(
        self,
        run_id: str,
        device_id: str,
        *,
        from_status: str | tuple[str, ...],
        to_status: str,
        proof: dict[str, Any] | None = None,
    ) -> None:
        accepted = (from_status,) if isinstance(from_status, str) else from_status
        placeholders = ",".join("?" for _ in accepted)
        now = _utc_now()
        with self._connect() as conn:
            result = conn.execute(
                f"""
                UPDATE assets
                SET status=?, updated_at=?, published_at=CASE WHEN ?='published' THEN ? ELSE published_at END,
                    proof_json=COALESCE(?, proof_json)
                WHERE run_id=? AND device_id=? AND status IN ({placeholders})
                """,
                (
                    to_status,
                    now,
                    to_status,
                    now,
                    json.dumps(proof, ensure_ascii=False) if proof else None,
                    run_id,
                    device_id,
                    *accepted,
                ),
            )
        if result.rowcount != 1:
            raise LedgerError("任务状态不匹配，拒绝覆盖其他设备或已完成任务")

    def list_assets(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT asset_id, path, status, device_id, run_id, leased_at, published_at, updated_at FROM assets ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]
