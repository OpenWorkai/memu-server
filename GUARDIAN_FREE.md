# memu-guardian with OpenCode + Free Models

零成本的 memu-server 自动维护方案。

## 🎯 方案特点

✅ **零 API 成本** - 使用 DeepSeek/Gemini 免费额度  
✅ **完全自动化** - LaunchAgent 定时执行  
✅ **MCP 原生支持** - 通过 stdio 直接访问 memu-server  
✅ **容错设计** - 失败自动降级，不会中断维护  

## 🚀 快速开始

### 1. 获取免费 API Key（任选一个）

**DeepSeek (推荐)**  
- 访问 https://platform.deepseek.com/
- 注册后获取 API Key
- 每月免费 500 万 tokens

**Google Gemini**  
- 访问 https://aistudio.google.com/
- 获取 API Key
- Gemini 2.0 Flash 完全免费

### 2. 安装

```bash
cd ~/memu-server
./install-guardian-opencode.sh
```

安装脚本会：
- 检查依赖（opencode, uv）
- 配置 API Key
- 安装 LaunchAgent
- 执行首次维护测试

### 3. 验证

```bash
# 查看服务状态
launchctl list | grep memu.guardian

# 查看日志
tail -f ~/.memu/guardian.log

# 查看最新报告
cat ~/.memu/reports/guardian-*.json | jq .
```

## 📋 维护任务

Guardian 每天凌晨 3:00 自动执行：

1. **健康检查**
   - 数据库文件存在性和大小
   - 缓存目录状态
   - MCP 服务可用性

2. **缓存清理**
   - 删除 7 天以上的 codegraph 缓存
   - 如果总大小超过 100MB，清理最旧的文件

3. **数据库优化**
   - 如果数据库 > 50MB，运行 VACUUM
   - 重建索引提升查询性能

4. **统计报告**
   - 总记忆数和分类统计
   - 最近 7 天新增记忆
   - 缓存命中率分析
   - 保存 JSON 格式报告

## 🛠️ 配置文件

### OpenCode 配置
`config/opencode-config.json`
```json
{
  "model": {
    "provider": "deepseek",
    "name": "deepseek-chat"
  },
  "fallback_models": [
    {"provider": "google", "name": "gemini-2.0-flash-exp"}
  ],
  "mcp_servers": {
    "memu": {
      "command": "uv",
      "args": ["run", "--project", "/Users/myking/memu", "python", "-m", "memu.mcp"]
    }
  }
}
```

### System Prompt
`config/guardian-system-prompt.md`

包含完整的维护指南和最佳实践。

### LaunchAgent
`~/Library/LaunchAgents/ai.memu.guardian.opencode.plist`

定时任务配置，每天 3:00 AM 执行。

## 🔧 手动操作

### 立即执行维护
```bash
bash ~/memu-server/memu-guardian-opencode.sh
```

### 重启服务
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
```

### 卸载
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
rm ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
```

## 📊 报告示例

```json
{
  "timestamp": "2026-07-06T03:00:15-04:00",
  "health_check": {
    "database_exists": true,
    "database_size_mb": 5.2,
    "cache_files_count": 3,
    "cache_size_mb": 0.15
  },
  "maintenance": {
    "caches_cleaned": 1,
    "database_vacuumed": false,
    "freed_space_mb": 0.05
  },
  "statistics": {
    "total_memories": 150,
    "memories_by_type": {
      "knowledge": 80,
      "profile": 20,
      "event": 30,
      "behavior": 20
    },
    "new_memories_last_week": 15
  },
  "warnings": [],
  "errors": []
}
```

## 💡 为什么选择免费模型？

1. **DeepSeek-Chat**
   - 每月 500 万 tokens 免费额度
   - 质量接近 GPT-4
   - 维护任务完全够用

2. **Gemini 2.0 Flash**
   - 完全免费（有 rate limit）
   - 速度极快
   - 作为 fallback 保证可用性

3. **成本对比**
   - Claude Sonnet 3.5: $3/M tokens 输入
   - DeepSeek: 免费（前 500 万）
   - Gemini Flash: 免费

对于日常维护任务（每天 ~1k tokens），免费额度永远用不完。

## 🔒 安全性

- API Key 存储在 LaunchAgent 环境变量中
- 日志自动轮转（保留 30 天）
- 只读取必要的数据库信息
- 不会删除任何记忆数据（只清理缓存）

## 🐛 故障排查

### OpenCode 未找到
```bash
cargo install opencode-cli
```

### API Key 无效
检查环境变量：
```bash
echo $DEEPSEEK_API_KEY
echo $GEMINI_API_KEY
```

### MCP 连接失败
测试 memu MCP 服务：
```bash
cd ~/memu
uv run python -m memu.mcp
```

### LaunchAgent 未运行
查看系统日志：
```bash
log show --predicate 'subsystem contains "ai.memu.guardian"' --last 1h
```

## 📝 日志位置

- 主日志：`~/.memu/guardian.log`
- stdout：`~/.memu/guardian-opencode-stdout.log`
- stderr：`~/.memu/guardian-opencode-stderr.log`
- 报告：`~/.memu/reports/guardian-YYYYMMDD-HHMMSS.json`

---

**核心理念**：用免费模型实现零成本的 AI 运维自动化。
