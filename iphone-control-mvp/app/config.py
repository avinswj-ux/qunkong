from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    appium_server_url: str = "http://127.0.0.1:4723"
    douyin_bundle_id: str = "com.ss.iphone.ugc.Aweme"
    xcode_org_id: str = ""
    xcode_signing_id: str = "Apple Development"
    wda_local_port: int = 8100
    wda_bundle_id: str = ""
    derived_data_root: Path = PROJECT_ROOT / ".derived-data"
    publisher_inbox: Path = Path("/Users/apple/Desktop/素材/inbox")
    publisher_database: Path = PROJECT_ROOT / "data" / "publisher.sqlite3"
    calibration_root: Path = PROJECT_ROOT / "calibrations"
    autodl_base_url: str = "https://autodl.art"
    autodl_comfyui_token: str = ""
    autodl_request_timeout_seconds: float = 30.0
    video_generation_database: Path = PROJECT_ROOT / "data" / "video_generation.sqlite3"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
