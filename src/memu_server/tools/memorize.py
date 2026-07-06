"""memu_memorize MCP tool — write raw text into the unified memory database."""

from __future__ import annotations

import json
import os
import tempfile

from memu_server.service import get_service


async def memu_memorize(
    text: str,
    source: str = "unknown",
    user_id: str | None = None,
) -> str:
    """Store text in the unified memory database.

    memu extracts structured memory items (facts, preferences, skills, etc.)
    from the raw text and deduplicates them automatically.

    Args:
        text: Raw text to memorize (conversation snippet, session summary, note, etc.)
        source: Which tool produced this text — "claude", "codex", "codebuddy", etc.
        user_id: User identifier (defaults to MEMU_USER_ID env var).

    Returns:
        JSON string with extracted item count and categories.
    """
    from memu_server.config import DEFAULT_USER_ID

    uid = user_id or DEFAULT_USER_ID
    service = get_service()

    # memu.memorize requires a file URL; write text to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as f:
        # Wrap as a single-turn conversation so memu recognises the modality
        conv = [{"role": "user", "content": f"[source:{source}] {text}"}]
        json.dump(conv, f, ensure_ascii=False)
        tmp_path = f.name

    try:
        result = await service.memorize(
            resource_url=tmp_path,
            modality="conversation",
            user={"user_id": uid},
        )
    finally:
        os.unlink(tmp_path)

    items = result.get("items", [])
    categories = [c.get("name") for c in result.get("categories", [])]
    return json.dumps(
        {"status": "ok", "items_extracted": len(items), "categories": categories},
        ensure_ascii=False,
    )
