#!/bin/bash
# Install memu-guardian as a daily scheduled task

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="$SCRIPT_DIR/config/ai.memu.guardian.plist"
INSTALL_PATH="$HOME/Library/LaunchAgents/ai.memu.guardian.plist"

echo "🛡️  Installing memu-guardian..."

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set"
    echo "   The agent will run but some features may not work"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Copy plist file
cp "$PLIST_FILE" "$INSTALL_PATH"

# Replace API key if provided
if [ -n "$OPENAI_API_KEY" ]; then
    # Use sed to replace the placeholder
    sed -i '' "s/REPLACE_WITH_YOUR_API_KEY/$OPENAI_API_KEY/g" "$INSTALL_PATH"
    echo "✓ API key configured"
fi

# Load the agent
launchctl unload "$INSTALL_PATH" 2>/dev/null || true
launchctl load "$INSTALL_PATH"

echo "✓ memu-guardian installed"
echo ""
echo "Configuration:"
echo "  - Runs daily at 3:00 AM"
echo "  - Logs: ~/.memu/guardian*.log"
echo "  - Reports: ~/.memu/reports/"
echo ""
echo "Manual run:"
echo "  cd ~/memu-server && uv run python memu-guardian.py"
echo ""
echo "Uninstall:"
echo "  launchctl unload $INSTALL_PATH"
echo "  rm $INSTALL_PATH"
