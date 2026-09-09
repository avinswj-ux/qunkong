import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse

from app.appium_manager import AppiumManager, AppiumOperationError
from app.config import get_settings
from app.device_manager import DeviceDiscoveryError, DeviceManager
from app.publisher_ledger import LedgerError, NoAvailableAsset, PublisherLedger
from app.video_generation import AutoDLClient, VideoGenerationError, VideoGenerationService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
device_manager = DeviceManager()
appium_manager = AppiumManager(get_settings())
publisher_ledger = PublisherLedger(get_settings().publisher_database)
settings = get_settings()
video_generation = VideoGenerationService(
    settings.video_generation_database,
    settings.publisher_inbox,
    AutoDLClient(
        token=settings.autodl_comfyui_token,
        base_url=settings.autodl_base_url,
        timeout=settings.autodl_request_timeout_seconds,
    ),
)


class ClaimRequest(BaseModel):
    device_id: str = Field(min_length=1)


class RunRequest(BaseModel):
    device_id: str = Field(min_length=1)


class ReviewRequest(RunRequest):
    reason: str = Field(min_length=1)


class PublishProof(RunRequest):
    proof: dict = Field(min_length=1)


class VideoGenerationRequest(BaseModel):
    workflow_id: str = Field(min_length=1, max_length=128)
    parameters: dict = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("iPhone Control MVP 启动")
    try:
        device_manager.list_devices()
    except DeviceDiscoveryError:
        logger.exception("启动时设备发现失败")
    yield
    await appium_manager.close_all()


app = FastAPI(title="iPhone Control MVP", lifespan=lifespan)


@app.get("/api/video-generation/tasks")
async def video_generation_tasks() -> dict:
    return {"tasks": video_generation.list()}


@app.post("/api/video-generation/tasks")
async def create_video_generation_task(request: VideoGenerationRequest) -> dict:
    try:
        task = video_generation.submit(request.workflow_id, request.parameters)
        return {"success": True, "task": task}
    except VideoGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/video-generation/tasks/{task_id}")
async def get_video_generation_task(task_id: str, refresh: bool = False) -> dict:
    try:
        task = video_generation.refresh(task_id) if refresh else video_generation.get(task_id)
        return {"task": task}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="生成任务不存在") from exc
    except VideoGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/devices")
async def devices() -> dict:
    try:
        items = device_manager.list_devices()
        return {"devices": [item.to_dict() for item in items]}
    except DeviceDiscoveryError as exc:
        logger.exception("设备发现失败")
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/devices/{udid}/test")
async def test_connection(udid: str) -> dict:
    try:
        device = device_manager.require_online(udid)
        return {"success": True, **await appium_manager.test_connection(device)}
    except DeviceDiscoveryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppiumOperationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/devices/{udid}/open-douyin")
async def open_douyin(udid: str) -> dict:
    try:
        device = device_manager.require_online(udid)
        return {"success": True, **await appium_manager.open_douyin(device)}
    except DeviceDiscoveryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AppiumOperationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/publisher/assets")
async def publisher_assets() -> dict:
    return {"assets": publisher_ledger.list_assets()}


@app.post("/api/publisher/claim")
async def publisher_claim(request: ClaimRequest) -> dict:
    """Lease a video.  The SQLite transaction prevents cross-device duplicates."""
    try:
        device_manager.require_online(request.device_id)
        claim = publisher_ledger.claim_next(
            device_id=request.device_id,
            inbox=get_settings().publisher_inbox,
        )
        return {"success": True, **claim.__dict__, "mode": "calibration"}
    except NoAvailableAsset as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (DeviceDiscoveryError, LedgerError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/publisher/{run_id}/prepared")
async def publisher_prepared(run_id: str, request: RunRequest) -> dict:
    try:
        publisher_ledger.mark_prepared(run_id=run_id, device_id=request.device_id)
        return {"success": True, "run_id": run_id, "status": "prepared"}
    except LedgerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/publisher/{run_id}/needs-review")
async def publisher_needs_review(run_id: str, request: ReviewRequest) -> dict:
    try:
        publisher_ledger.mark_needs_review(
            run_id=run_id,
            device_id=request.device_id,
            reason=request.reason,
        )
        return {"success": True, "run_id": run_id, "status": "needs_review"}
    except LedgerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/publisher/{run_id}/published")
async def publisher_published(run_id: str, request: PublishProof) -> dict:
    """Only call after the calibrated runner has observed the success screen."""
    try:
        publisher_ledger.mark_published(
            run_id=run_id,
            device_id=request.device_id,
            proof=request.proof,
        )
        return {"success": True, "run_id": run_id, "status": "published"}
    except LedgerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
