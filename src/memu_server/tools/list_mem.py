"""memu_list MCP tool — browse memory categories and items."""

from __future__ import annotations

import json

from memu_server.service import get_service


async def memu_list(
    user_id: str | None = None,
    category: str | None = None,
) -> str:
    """List memory categories (and optionally items within a category).

    Args:
        user_id: User identifier (defaults to MEMU_USER_ID env var).
        category: If provided, list items within this category name.
                  If omitted, list all top-level categories.

    Returns:
        JSON string with categories or items.
    """
    from memu_server.config import DEFAULT_USER_ID

    uid = user_id or DEFAULT_USER_ID
    service = get_service()

    if category:
        result = await service.list_memory_items(
            where={"user_id": uid, "category_name": category},
        )
        items = result.get("items", [])
        trimmed = [
            {
                "id": item.get("id"),
                "summary": item.get("summary"),
                "memory_type": item.get("memory_type"),
            }
            for item in items
        ]
        return json.dumps({"category": category, "items": trimmed}, ensure_ascii=False)
    else:
        result = await service.list_memory_categories(where={"user_id": uid})
        cats = result.get("categories", [])
        trimmed = [
            {
                "name": c.get("name"),
                "description": c.get("description"),
                "item_count": c.get("item_count", 0),
            }
            for c in cats
        ]
        return json.dumps({"categories": trimmed}, ensure_ascii=False)
