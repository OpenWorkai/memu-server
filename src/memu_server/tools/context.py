"""memu_context MCP tool — return a Markdown summary for injection into system prompts."""

from __future__ import annotations

import json

from memu_server.service import get_service


async def memu_context(user_id: str | None = None) -> str:
    """Return a Markdown-formatted memory context summary.

    Designed to be injected at the top of a system prompt so that the AI
    tool has immediate access to long-term user preferences, active projects,
    and recent decisions.

    Args:
        user_id: User identifier (defaults to MEMU_USER_ID env var).

    Returns:
        Markdown string ready for injection into a system prompt.
    """
    from memu_server.config import DEFAULT_USER_ID

    uid = user_id or DEFAULT_USER_ID
    service = get_service()

    result = await service.list_memory_categories(where={"user_id": uid})
    categories = result.get("categories", [])

    if not categories:
        return "<!-- memu: no memory found -->"

    lines: list[str] = ["## Long-term Memory Context (from memu)\n"]
    for cat in categories:
        name = cat.get("name", "unknown")
        summary = cat.get("summary", "").strip()
        if summary:
            lines.append(f"### {name}\n{summary}\n")

    return "\n".join(lines)
