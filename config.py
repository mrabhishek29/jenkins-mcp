"""Configuration loader for the Jenkins MCP server."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class JenkinsConfig(BaseModel):
    enabled: bool = True
    base_url: str
    username: str
    password: str

    @field_validator("base_url")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: str = "logs"

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(sorted(allowed))}")
        return v_upper


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 9100


class Config(BaseModel):
    jenkins: Optional[JenkinsConfig] = None
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    @classmethod
    def load(cls, path: Path | str | None = None) -> "Config":
        if path is None:
            path = Path("config.yaml")
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {path}\n"
                "Copy config.example.yaml to config.yaml and fill in your credentials."
            )

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data:
            raise ValueError(f"Config file is empty: {path}")

        return cls(**data)
