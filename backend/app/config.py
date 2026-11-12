import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.common import BundleProfile


def _default_output_dir() -> Path:
    """Pick a writable data directory when running as a bundled app.

    Frozen Tauri apps inherit the launch cwd (usually "/" on macOS), so a
    relative "./outputs" is not writable. Keep the relative default for dev.
    """
    if not getattr(sys, "frozen", False):
        return Path("./outputs")
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "PrimeClip" / "outputs"
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(base) / "PrimeClip" / "outputs"
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "primeclip" / "outputs"


def _app_config_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "PrimeClip"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA") or str(Path.home())) / "PrimeClip"
    return Path(os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")) / "primeclip"


def _env_files() -> tuple[str, ...]:
    """Frozen builds read config from the user's app data directory."""
    if getattr(sys, "frozen", False):
        return (str(_app_config_dir() / ".env"), ".env")
    return (".env",)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files(), env_file_encoding="utf-8", extra="ignore"
    )

    claude_api_key: str = ""
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_url: str = "http://localhost:11434"
    whisper_model: str = "base"
    whisper_device: str = "auto"
    output_dir: Path = Field(default_factory=_default_output_dir)
    database_url: str = "sqlite:///./outputs/primeclip.db"
    sidecar_host: str = "127.0.0.1"
    sidecar_port: int = 8765
    ffmpeg_path: str = ""
    bundle_profile: BundleProfile = BundleProfile.LITE
    primeclip_debug: bool = False
    log_level: str = ""
    log_to_file: bool = True
    scene_threshold: float = 0.3
    scene_min_len_sec: float = 2.0
    clip_min_sec: float = 30
    clip_max_sec: float = 90
    ytdlp_path: str = ""
    import_max_duration_sec: int = 7200
    ytdlp_cookies_file: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    @property
    def logs_dir(self) -> Path:
        return self.output_dir / "logs"

    @property
    def uploads_dir(self) -> Path:
        return self.output_dir / "uploads"

    @property
    def artifacts_dir(self) -> Path:
        return self.output_dir / "artifacts"

    @property
    def clips_dir(self) -> Path:
        return self.output_dir / "clips"

    @property
    def models_dir(self) -> Path:
        return self.output_dir / "models"

    @property
    def bundled_resources_dir(self) -> Path:
        return Path(__file__).resolve().parents[3] / "resources"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    settings.clips_dir.mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    return settings
