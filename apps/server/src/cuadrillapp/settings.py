"""Configuration from environment variables."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    web_dist_dir: Path | None = None
    render_git_commit: str = "dev"

    @property
    def is_production(self) -> bool:
        return self.env == "production"
