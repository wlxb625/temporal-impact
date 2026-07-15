"""Runtime configuration for the local, read-only sidecar."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path


def default_database_url() -> str:
    """Return the configured SQLite URL without creating a database yet."""
    configured_url = getenv("TEMPORAL_IMPACT_DB_URL")
    if configured_url:
        return configured_url
    database_path = Path.home() / ".temporal-impact" / "temporal_impact.db"
    return f"sqlite:///{database_path.as_posix()}"


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings supported by v0.1."""

    database_url: str = default_database_url()
    max_depth: int = int(getenv("TEMPORAL_IMPACT_MAX_DEPTH", "3"))
    host: str = getenv("TEMPORAL_IMPACT_HOST", "127.0.0.1")
    port: int = int(getenv("TEMPORAL_IMPACT_PORT", "8765"))
