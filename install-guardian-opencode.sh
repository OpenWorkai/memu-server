#!/bin/bash
# Install memu-guardian with OpenCode + Free Models

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/config/ai.memu.guardian.opencode.plist"
INSTALL_PATH="$HOME/Library/LaunchAgents/ai.memu.guardian.opencode.plist"

echo "🛡️  Installing memu-guardian (OpenCode Edition)"
echo ""

# Step 1: Check dependencies
echo "Step 1: Checking dependencies..."

if ! command -v opencode &> /dev/null; then
    echo "❌ opencode CLI not found."
    echo ""
    echo "Install it with:"
    echo "  cargo install opencode-cli"
    echo ""
    exit 1
fi

if ! command -v uv &> /dev/null; then
    echo "❌ uv not found."
    echo ""
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Dependencies OK"
echo ""

# Step 2: Info about free models
echo "Step 2: Using OpenCode built-in free models..."
echo "✅ No API key needed! Using:"
echo "   - Big Pickle OpenCode Zen"
echo "   - DeepSeek V4 Flash Free"
echo "   - North Mini Code Free"
echo "   - Nemotron 3 Ultra Free"
echo "   - MiMo V2.5 Free"
echo ""

# Step 3: Install LaunchAgent
echo "Step 3: Installing LaunchAgent..."

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_FILE" "$INSTALL_PATH"

echo "✅ LaunchAgent configured"
echo ""

# Step 4: Load LaunchAgent
echo "Step 4: Loading LaunchAgent..."

launchctl bootout gui/$(id -u) "$INSTALL_PATH" 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$INSTALL_PATH"

echo "✅ LaunchAgent loaded"
echo ""

# Step 5: Test run
echo "Step 5: Running test maintenance..."
echo ""

bash "$SCRIPT_DIR/memu-guardian-simple.sh"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "The guardian will run daily at 3:00 AM."
echo ""
echo "Manual run:"
echo "  bash ~/memu-server/memu-guardian-opencode.sh"
echo ""
echo "Check status:"
echo "  launchctl list | grep memu.guardian"
echo ""
echo "View logs:"
echo "  tail -f ~/.memu/guardian.log"
echo ""
