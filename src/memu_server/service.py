"""Singleton memu MemoryService backed by the unified SQLite database."""

from __future__ import annotations

import os
from pathlib import Path

from memu import MemoryService

from . import config

_service: MemoryService | None = None


def get_service() -> MemoryService:
    """Return (or lazily create) the shared MemoryService instance.
    
    Uses simplified initialization matching memu examples.
    """
    global _service
    if _service is None:
        # Ensure the database directory exists
        db_path = Path(config.DB_PATH).expanduser()
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize service with simple dict-based config (matching example_1)
        _service = MemoryService(
            llm_profiles={
                "default": {
                    "api_key": config.LLM_API_KEY,
                    "chat_model": config.LLM_CHAT_MODEL,
                },
            },
            database_config={
                "backend": "sqlite",
                "path": str(db_path),
            },
        )
    return _service
