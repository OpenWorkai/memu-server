"""memu_retrieve MCP tool — semantic search over the unified memory database."""

from __future__ import annotations

import json

from memu_server.service import get_service


async def memu_retrieve(
    query: str,
    user_id: str | None = None,
    top_k: int = 5,
) -> str:
    """Retrieve relevant memories using semantic search.

    Args:
        query: Natural-language search query.
        user_id: User identifier (defaults to MEMU_USER_ID env var).
        top_k: Maximum number of memory items to return.

    Returns:
        JSON string containing matched memory items with their summaries.
    """
    from memu_server.config import DEFAULT_USER_ID

    uid = user_id or DEFAULT_USER_ID
    service = get_service()

    result = await service.retrieve(
        queries=[{"role": "user", "content": query}],
        where={"user_id": uid},
    )

    # Normalise the response into a clean list
    items = result.get("items", [])
    trimmed = [
        {
            "id": item.get("id"),
            "summary": item.get("summary"),
            "memory_type": item.get("memory_type"),
            "category": item.get("category_name"),
        }
        for item in items[:top_k]
    ]

    return json.dumps({"query": query, "results": trimmed}, ensure_ascii=False)
