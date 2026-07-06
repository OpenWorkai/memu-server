#!/bin/sh
# Codex "Stop" hook — archives session summary into the unified memu database.

PAYLOAD=$(cat)
if [ -z "$PAYLOAD" ]; then
  exit 0
fi

SUMMARY=$(printf '%s' "$PAYLOAD" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    text = d.get('summary') or d.get('message') or ''
    if not text:
        msgs = d.get('transcript', d.get('messages', []))
        for m in reversed(msgs):
            if isinstance(m, dict) and m.get('role') == 'user':
                content = m.get('content', '')
                if isinstance(content, list):
                    content = ' '.join(c.get('text','') for c in content if isinstance(c, dict))
                text = content
                break
    print(str(text).strip()[:2000])
except Exception:
    pass
" 2>/dev/null)

if [ -z "$SUMMARY" ]; then
  exit 0
fi

python3 -c "
import asyncio, sys, os
sys.path.insert(0, os.path.expanduser('~/memu-server/src'))
from memu_server.tools.memorize import memu_memorize
asyncio.run(memu_memorize(text='''$SUMMARY''', source='codex'))
" 2>/dev/null

exit 0
