"""Configuration for memu-server.

Values are read from environment variables with sensible defaults.
"""

from __future__ import annotations

import os

# Path to the unified SQLite database shared by all AI tools
DB_PATH: str = os.environ.get(
    "MEMU_DB_PATH",
    os.path.expanduser("~/.memu/unified.db"),
)

# Blob/resource storage directory
BLOB_DIR: str = os.environ.get(
    "MEMU_BLOB_DIR",
    os.path.expanduser("~/.memu/resources"),
)

# Default user identifier
DEFAULT_USER_ID: str = os.environ.get("MEMU_USER_ID", "myking")

# LLM configuration — reads from standard env vars used by other tools
LLM_BASE_URL: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
LLM_CHAT_MODEL: str = os.environ.get("MEMU_CHAT_MODEL", "gpt-4o-mini")
LLM_EMBED_MODEL: str = os.environ.get("MEMU_EMBED_MODEL", "text-embedding-3-small")
