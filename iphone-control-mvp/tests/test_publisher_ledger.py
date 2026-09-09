from pathlib import Path

import pytest

from app.publisher_ledger import NoAvailableAsset, PublisherLedger


def test_claim_is_exclusive_and_published_assets_never_reappear(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "one.mp4").write_bytes(b"video-one")
    (inbox / "two.mp4").write_bytes(b"video-two")
    ledger = PublisherLedger(tmp_path / "publisher.sqlite3")

    first = ledger.claim_next(device_id="device-a", inbox=inbox)
    second = ledger.claim_next(device_id="device-b", inbox=inbox)
    assert first.asset_id != second.asset_id

    ledger.mark_prepared(run_id=first.run_id, device_id="device-a")
    ledger.mark_published(
        run_id=first.run_id,
        device_id="device-a",
        proof={"success_screen": "published"},
    )
    with pytest.raises(NoAvailableAsset):
        ledger.claim_next(device_id="device-c", inbox=inbox)


def test_review_state_is_not_released_to_another_device(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "one.mp4").write_bytes(b"video-one")
    ledger = PublisherLedger(tmp_path / "publisher.sqlite3")
    claimed = ledger.claim_next(device_id="device-a", inbox=inbox)
    ledger.mark_needs_review(
        run_id=claimed.run_id,
        device_id="device-a",
        reason="publish screen did not confirm success",
    )
    with pytest.raises(NoAvailableAsset):
        ledger.claim_next(device_id="device-b", inbox=inbox)
