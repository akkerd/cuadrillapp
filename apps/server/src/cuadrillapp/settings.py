"""Configuración por variables de entorno."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from cuadrillapp.constants import ADMIN_GRACE_SECONDS, ROOM_IDLE_TTL_SECONDS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    web_dist_dir: Path | None = None
    render_git_commit: str = "dev"
    # None = solo el mismo origen (producción y proxy de Vite en desarrollo).
    cors_origins: list[str] | None = None

    max_rooms: int = 300
    room_creates_per_minute: int = 10
    rate_capacity: float = 40
    rate_refill_per_second: float = 20

    admin_grace_seconds: float = ADMIN_GRACE_SECONDS
    room_idle_ttl_seconds: float = ROOM_IDLE_TTL_SECONDS
    sweep_interval_seconds: float = 60

    @property
    def is_production(self) -> bool:
        return self.env == "production"
