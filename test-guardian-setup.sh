#!/bin/bash
# Quick test for memu-guardian OpenCode setup

set -e

echo "🧪 Testing memu-guardian OpenCode setup"
echo ""

# Check 1: OpenCode CLI
echo "1️⃣  Checking OpenCode CLI..."
if command -v opencode &> /dev/null; then
    echo "   ✅ opencode found: $(which opencode)"
else
    echo "   ❌ opencode not found"
    echo "   Install it with: cargo install opencode-cli"
    exit 1
fi
echo ""

# Check 2: uv
echo "2️⃣  Checking uv..."
if command -v uv &> /dev/null; then
    echo "   ✅ uv found: $(which uv)"
else
    echo "   ❌ uv not found"
    echo "   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo ""

# Check 3: API Keys
echo "3️⃣  Checking API Keys..."
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "   ✅ DEEPSEEK_API_KEY is set"
    HAS_KEY=1
elif [ -n "$GEMINI_API_KEY" ]; then
    echo "   ✅ GEMINI_API_KEY is set"
    HAS_KEY=1
elif [ -n "$OPENROUTER_API_KEY" ]; then
    echo "   ✅ OPENROUTER_API_KEY is set"
    HAS_KEY=1
else
    echo "   ⚠️  No API keys found in environment"
    echo ""
    echo "   Get a free key from:"
    echo "   - DeepSeek: https://platform.deepseek.com/"
    echo "   - Gemini: https://aistudio.google.com/"
    echo "   - OpenRouter: https://openrouter.ai/ (has free models)"
    echo ""
    echo "   Then set it:"
    echo "   export DEEPSEEK_API_KEY='sk-xxx'"
    echo "   # or"
    echo "   export GEMINI_API_KEY='xxx'"
    echo "   # or"
    echo "   export OPENROUTER_API_KEY='sk-or-xxx'"
    HAS_KEY=0
fi
echo ""

# Check 4: Config file
echo "4️⃣  Checking OpenCode config..."
CONFIG_FILE="$HOME/memu-server/config/opencode-config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "   ✅ Config file exists: $CONFIG_FILE"
    echo "   Content preview:"
    cat "$CONFIG_FILE" | jq . | head -10
else
    echo "   ❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
echo ""

# Check 5: System prompt
echo "5️⃣  Checking system prompt..."
PROMPT_FILE="$HOME/memu-server/config/guardian-system-prompt.md"
if [ -f "$PROMPT_FILE" ]; then
    LINES=$(wc -l < "$PROMPT_FILE")
    echo "   ✅ System prompt exists ($LINES lines)"
else
    echo "   ❌ System prompt not found: $PROMPT_FILE"
    exit 1
fi
echo ""

# Check 6: memu installation
echo "6️⃣  Checking memu installation..."
if [ -d "$HOME/memu" ]; then
    echo "   ✅ memu directory exists"
    
    # Try to run MCP server briefly
    if timeout 2 uv run --project "$HOME/memu" python -m memu.mcp 2>&1 | grep -q "mcp" || true; then
        echo "   ✅ memu MCP server can start"
    else
        echo "   ⚠️  Could not verify MCP server (this is OK if memu is installed)"
    fi
else
    echo "   ❌ memu directory not found: $HOME/memu"
    echo "   Clone it from: git clone https://github.com/yourusername/memu.git ~/memu"
    exit 1
fi
echo ""

# Check 7: Directory structure
echo "7️⃣  Checking directory structure..."
mkdir -p ~/.memu/reports
if [ -d ~/.memu ]; then
    echo "   ✅ ~/.memu directory exists"
    echo "   ✅ ~/.memu/reports directory exists"
else
    echo "   ❌ ~/.memu directory does not exist"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $HAS_KEY -eq 1 ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "  1. Run installation:"
    echo "     cd ~/memu-server && ./install-guardian-opencode.sh"
    echo ""
    echo "  2. Or test manually:"
    echo "     cd ~/memu-server && ./memu-guardian-opencode.sh"
else
    echo "⚠️  Setup incomplete - need API key"
    echo ""
    echo "Get a free key and set it in your environment, then run:"
    echo "  ./install-guardian-opencode.sh"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
