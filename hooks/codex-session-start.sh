#!/bin/sh
# Codex "SessionStart" hook — injects long-term memory context into AGENTS.md.
#
# Fetches a Markdown summary from memu and writes it into the
# <!-- OMX:RUNTIME:START --> block in ~/.codex/AGENTS.md so that
# Codex sees the memory context at the start of every session.

AGENTS_MD="$HOME/.codex/AGENTS.md"

CONTEXT=$(python3 -c "
import asyncio, sys, os
sys.path.insert(0, os.path.expanduser('~/memu-server/src'))
from memu_server.tools.context import memu_context
print(asyncio.run(memu_context()))
" 2>/dev/null)

if [ -z "$CONTEXT" ] || [ "$CONTEXT" = "<!-- memu: no memory found -->" ]; then
  exit 0
fi

if [ ! -f "$AGENTS_MD" ]; then
  exit 0
fi

# Replace content between OMX:RUNTIME markers (or append if markers absent)
python3 -c "
import re, sys, os

agents_path = os.path.expanduser('~/.codex/AGENTS.md')
with open(agents_path, 'r', encoding='utf-8') as f:
    content = f.read()

context = '''$CONTEXT'''

START = '<!-- OMX:RUNTIME:START -->'
END   = '<!-- OMX:RUNTIME:END -->'

block = f'{START}\n{context}\n{END}'

if START in content and END in content:
    updated = re.sub(
        re.escape(START) + r'.*?' + re.escape(END),
        block,
        content,
        flags=re.DOTALL,
    )
else:
    updated = content + '\n\n' + block + '\n'

with open(agents_path, 'w', encoding='utf-8') as f:
    f.write(updated)
" 2>/dev/null

exit 0
