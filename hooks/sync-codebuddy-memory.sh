#!/bin/sh
# Sync memu long-term memory context into CodeBuddy's MEMORY.md index.
#
# Run manually or via cron: e.g. every 30 minutes while working.
# Example cron entry:
#   */30 * * * * /bin/sh ~/memu-server/hooks/sync-codebuddy-memory.sh

MEMORY_DIR="$HOME/.codebuddy/projects/Users-myking/memory"
MEMORY_FILE="$MEMORY_DIR/memu-context.md"

mkdir -p "$MEMORY_DIR"

CONTEXT=$(python3 -c "
import asyncio, sys, os
sys.path.insert(0, os.path.expanduser('~/memu-server/src'))
from memu_server.tools.context import memu_context
print(asyncio.run(memu_context()))
" 2>/dev/null)

if [ -z "$CONTEXT" ] || [ "$CONTEXT" = "<!-- memu: no memory found -->" ]; then
  exit 0
fi

# Write the context snapshot with a timestamp header
printf '---\nname: memu-context\ndescription: Long-term memory context synced from memu unified database\ntype: user\n---\n\n%s\n\n_(Last synced: %s)_\n' \
  "$CONTEXT" "$(date '+%Y-%m-%d %H:%M')" > "$MEMORY_FILE"

# Ensure MEMORY.md index has an entry for this file
MEMORY_INDEX="$MEMORY_DIR/MEMORY.md"
if [ -f "$MEMORY_INDEX" ]; then
  if ! grep -q "memu-context.md" "$MEMORY_INDEX"; then
    printf '\n- [memu-context](memu-context.md) — Long-term memory context from unified memu database\n' >> "$MEMORY_INDEX"
  fi
else
  printf '- [memu-context](memu-context.md) — Long-term memory context from unified memu database\n' > "$MEMORY_INDEX"
fi

exit 0
