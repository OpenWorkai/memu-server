"""memu-server — unified AI memory MCP server.

Exposes 5 MCP tools backed by a single SQLite database:
  - memu_memorize  : write raw text, memu extracts structured memories
  - memu_retrieve  : semantic search over stored memories
  - memu_context   : Markdown summary for system-prompt injection
  - memu_list      : browse categories and items
  - memu_codegraph : generate and cache project structure (codeGraph)
"""

from __future__ import annotations

from fastmcp import FastMCP

from .tools import memu_codegraph, memu_context, memu_list, memu_memorize, memu_retrieve

mcp = FastMCP(
    "memu-unified",
    instructions=(
        "Unified long-term memory for all AI tools. "
        "Use memu_retrieve to recall relevant facts before answering. "
        "Use memu_memorize to store important decisions or user preferences. "
        "Use memu_codegraph to analyze and cache project structures."
    ),
)

mcp.tool()(memu_memorize)
mcp.tool()(memu_retrieve)
mcp.tool()(memu_context)
mcp.tool()(memu_list)
mcp.tool()(memu_codegraph)


def main() -> None:
    """Entry point — runs in stdio mode (required for MCP clients)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
