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

# Step 2: Check API keys
echo "Step 2: Checking API keys..."

if [ -z "$DEEPSEEK_API_KEY" ] && [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  No API keys found in environment."
    echo ""
    echo "You need at least one free API key:"
    echo "  - DeepSeek (Free): https://platform.deepseek.com/"
    echo "  - Google Gemini (Free): https://aistudio.google.com/"
    echo "  - OpenRouter (Free models): https://openrouter.ai/"
    echo ""
    echo "After getting a key, run:"
    echo "  export DEEPSEEK_API_KEY='sk-xxx'"
    echo "  # or"
    echo "  export GEMINI_API_KEY='xxx'"
    echo "  # or"
    echo "  export OPENROUTER_API_KEY='sk-or-xxx'"
    echo ""
    
    read -p "Do you want to set a key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        read -p "Choose provider (1=DeepSeek, 2=Gemini, 3=OpenRouter): " provider
        
        if [ "$provider" = "1" ]; then
            read -p "Enter DeepSeek API key: " key
            export DEEPSEEK_API_KEY="$key"
            echo "export DEEPSEEK_API_KEY='$key'" >> ~/.zshrc
            FINAL_KEY="$key"
            KEY_VAR="DEEPSEEK_API_KEY"
        elif [ "$provider" = "2" ]; then
            read -p "Enter Gemini API key: " key
            export GEMINI_API_KEY="$key"
            echo "export GEMINI_API_KEY='$key'" >> ~/.zshrc
            FINAL_KEY="$key"
            KEY_VAR="GEMINI_API_KEY"
        elif [ "$provider" = "3" ]; then
            read -p "Enter OpenRouter API key: " key
            export OPENROUTER_API_KEY="$key"
            echo "export OPENROUTER_API_KEY='$key'" >> ~/.zshrc
            FINAL_KEY="$key"
            KEY_VAR="OPENROUTER_API_KEY"
        else
            echo "Invalid choice. Exiting."
            exit 1
        fi
        
        echo "✅ Key saved to ~/.zshrc"
    else
        exit 1
    fi
else
    if [ -n "$DEEPSEEK_API_KEY" ]; then
        FINAL_KEY="$DEEPSEEK_API_KEY"
        KEY_VAR="DEEPSEEK_API_KEY"
        echo "✅ Found DEEPSEEK_API_KEY"
    elif [ -n "$GEMINI_API_KEY" ]; then
        FINAL_KEY="$GEMINI_API_KEY"
        KEY_VAR="GEMINI_API_KEY"
        echo "✅ Found GEMINI_API_KEY"
    elif [ -n "$OPENROUTER_API_KEY" ]; then
        FINAL_KEY="$OPENROUTER_API_KEY"
        KEY_VAR="OPENROUTER_API_KEY"
        echo "✅ Found OPENROUTER_API_KEY"
    fi
fi
echo ""

# Step 3: Update plist with actual API key
echo "Step 3: Configuring LaunchAgent..."

cp "$PLIST_FILE" "$PLIST_FILE.tmp"

if [ "$KEY_VAR" = "DEEPSEEK_API_KEY" ]; then
    sed -i '' "s|REPLACE_WITH_YOUR_OPENROUTER_KEY|$FINAL_KEY|g" "$PLIST_FILE.tmp"
    sed -i '' "s|<key>OPENROUTER_API_KEY</key>|<key>DEEPSEEK_API_KEY</key>|g" "$PLIST_FILE.tmp"
elif [ "$KEY_VAR" = "GEMINI_API_KEY" ]; then
    sed -i '' "s|REPLACE_WITH_YOUR_OPENROUTER_KEY|$FINAL_KEY|g" "$PLIST_FILE.tmp"
    sed -i '' "s|<key>OPENROUTER_API_KEY</key>|<key>GEMINI_API_KEY</key>|g" "$PLIST_FILE.tmp"
else
    sed -i '' "s|REPLACE_WITH_YOUR_OPENROUTER_KEY|$FINAL_KEY|g" "$PLIST_FILE.tmp"
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_FILE.tmp" "$INSTALL_PATH"
rm "$PLIST_FILE.tmp"

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

bash "$SCRIPT_DIR/memu-guardian-opencode.sh"

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
