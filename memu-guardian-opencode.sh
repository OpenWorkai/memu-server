#!/bin/bash
# memu-guardian - Daily maintenance agent using OpenCode CLI
# Uses free models (DeepSeek/Gemini) to avoid cost issues

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

# Verify API keys are set
if [ -z "$DEEPSEEK_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    log "⚠️  Warning: No API keys found. Set DEEPSEEK_API_KEY or GEMINI_API_KEY"
    log "   You can get free keys from:"
    log "   - DeepSeek: https://platform.deepseek.com/"
    log "   - Google AI Studio: https://aistudio.google.com/"
    exit 1
fi

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
)

# Run OpenCode with free model
log "Launching OpenCode with maintenance tasks..."

# Use opencode CLI (assuming it's available)
if command -v opencode &> /dev/null; then
    # OpenCode CLI mode
    echo "$TASKS_PROMPT" | opencode --model deepseek-chat --non-interactive >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
elif command -v openclaude &> /dev/null; then
    # OpenClaude CLI mode  
    echo "$TASKS_PROMPT" | openclaude --model gemini-2.0-flash --non-interactive >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
else
    log "❌ OpenCode/OpenClaude CLI not found"
    log "   Install: npm install -g @openai/opencode"
    exit 1
fi

if [ $EXIT_CODE -eq 0 ]; then
    log "✓ Maintenance tasks completed"
else
    log "⚠️  Some tasks may have failed (exit code: $EXIT_CODE)"
fi

# Generate summary report
REPORT_FILE="$REPORT_DIR/guardian-$(date +%Y%m%d-%H%M%S).json"

cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "exit_code": $EXIT_CODE,
  "log_file": "$LOG_FILE",
  "last_lines": $(tail -20 "$LOG_FILE" | jq -R -s -c 'split("\n")')
}
EOF

log "📊 Report saved: $REPORT_FILE"

# Cleanup old reports (keep last 30)
cd "$REPORT_DIR"
ls -t guardian-*.json | tail -n +31 | xargs rm -f 2>/dev/null || true

log "🛡️  memu-guardian completed"

exit $EXIT_CODE
EOF

log "📝 Task file created: $TASK_FILE"
log "🤖 Starting OpenCode agent with config: $CONFIG_FILE"

# Run OpenCode with the task
cd "$SCRIPT_DIR"
if opencode --config "$CONFIG_FILE" < "$TASK_FILE" >> "$LOG_FILE" 2>&1; then
    log "✅ Guardian maintenance completed successfully"
    
    # Clean up old task files (keep last 7 days)
    find "$MEMU_ROOT" -name "guardian-task-*.txt" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up old reports (keep last 30 days)
    find "$REPORT_DIR" -name "guardian-*.json" -mtime +30 -delete 2>/dev/null || true
    
    exit 0
else
    log "❌ Guardian maintenance failed. Check logs for details."
    exit 1
fi
