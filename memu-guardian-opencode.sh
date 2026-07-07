#!/bin/bash
# memu-guardian - Daily maintenance agent using OpenCode CLI
# Uses free models (DeepSeek/Gemini/OpenRouter) to avoid cost issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMU_ROOT="$HOME/.memu"
LOG_FILE="$MEMU_ROOT/guardian.log"
REPORT_DIR="$MEMU_ROOT/reports"
CONFIG_FILE="$SCRIPT_DIR/config/opencode-config.json"

# Ensure directories exist
mkdir -p "$MEMU_ROOT" "$REPORT_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🛡️  memu-guardian started (OpenCode + Free Models)"

# Check if OpenCode is available
if ! command -v opencode &> /dev/null; then
    log "❌ Error: opencode CLI not found. Install it first."
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    log "❌ Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

log "Using OpenCode built-in free models (no API key needed)"

# Create maintenance task prompt
TASK_FILE="$MEMU_ROOT/guardian-task-$(date +%Y%m%d-%H%M%S).txt"
cat > "$TASK_FILE" << 'EOF'
执行 memu-server 的日常维护任务，生成完整的维护报告。

请按照 system prompt 中的指引完成所有任务：
1. 健康检查（数据库、缓存、MCP 服务）
2. 清理过期缓存（7天以上）
3. 数据库优化（如果需要）
4. 统计分析（生成 JSON 报告）

最后输出维护完成的总结。
- 每个任务记录日志到 ~/.memu/guardian.log
- 生成 JSON 格式的最终报告
- 如果遇到错误，记录但继续执行后续任务

开始执行任务。
EOF

log "📝 Task file created: $TASK_FILE"
log "🤖 Starting OpenCode agent with free model..."

# Run OpenCode with the task using built-in free models
cd "$SCRIPT_DIR"

# Read task content
TASK_CONTENT=$(cat "$TASK_FILE")

# Try OpenCode built-in free models in order
MODELS=(
    "Big Pickle OpenCode Zen"
    "DeepSeek V4 Flash Free OpenCode Zen"
    "North Mini Code Free OpenCode Zen"
    "Nemotron 3 Ultra Free"
    "MiMo V2.5 Free"
)

SUCCESS=0
for MODEL in "${MODELS[@]}"; do
    log "Trying model: $MODEL"
    if opencode run --model "$MODEL" --auto "$TASK_CONTENT" >> "$LOG_FILE" 2>&1; then
        log "✅ Guardian maintenance completed successfully with $MODEL"
        SUCCESS=1
        break
    else
        log "⚠️  Model $MODEL failed, trying next..."
    fi
done

if [ $SUCCESS -eq 1 ]; then
    # Clean up old task files (keep last 7 days)
    find "$MEMU_ROOT" -name "guardian-task-*.txt" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up old reports (keep last 30 days)
    find "$REPORT_DIR" -name "guardian-*.json" -mtime +30 -delete 2>/dev/null || true
    
    exit 0
else
    log "❌ All models failed. Guardian maintenance failed."
    exit 1
fi
