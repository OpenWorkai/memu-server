#!/bin/sh
# Claude "Stop" hook — archives the session summary into the unified memu database.
# Triggered when a Claude Code session ends.
#
# Claude sends a JSON payload to stdin, e.g.:
# {"session_id":"...", "summary":"...", "transcript":[...]}

PAYLOAD=$(cat)
if [ -z "$PAYLOAD" ]; then
  exit 0
fi

SUMMARY=$(printf '%s' "$PAYLOAD" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    # Try 'summary' field first, fall back to last user message
    text = d.get('summary') or ''
    if not text:
        msgs = d.get('transcript', d.get('messages', []))
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get('role') == 'user':
                text = m.get('content', '')
                break
    print(text.strip())
except Exception:
    pass
" 2>/dev/null)

if [ -z "$SUMMARY" ]; then
  exit 0
fi

uv run --project "$HOME/memu-server" memu-server-memorize \
  --text "$SUMMARY" --source "claude" 2>/dev/null || \
python3 -c "
import asyncio, sys, os
sys.path.insert(0, '$HOME/memu-server/src')
from memu_server.tools.memorize import memu_memorize
asyncio.run(memu_memorize(text='''$SUMMARY''', source='claude'))
" 2>/dev/null

exit 0
