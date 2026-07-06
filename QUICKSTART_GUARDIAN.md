# Quick Start: memu-guardian 零成本自动维护

3 步启动，永久免费运行。

## 📋 准备工作（5 分钟）

### 1. 获取免费 API Key（任选一个）

#### 方案 A: DeepSeek (推荐)
1. 访问 https://platform.deepseek.com/
2. 注册账号（支持国内手机号）
3. 获取 API Key
4. 额度：每月 500 万 tokens（约 375 万汉字）

#### 方案 B: Google Gemini
1. 访问 https://aistudio.google.com/
2. 使用 Google 账号登录
3. 创建 API Key
4. 额度：完全免费（有 rate limit）

### 2. 设置环境变量

```bash
# DeepSeek
export DEEPSEEK_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxx'
echo 'export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc

# 或 Gemini
export GEMINI_API_KEY='xxxxxxxxxxxxxxxxxxxxxxxx'
echo 'export GEMINI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
```

## 🚀 安装（1 分钟）

### 方式 1: 一键安装（推荐）

```bash
cd ~/memu-server
./test-guardian-setup.sh    # 先测试环境
./install-guardian-opencode.sh  # 自动安装
```

安装脚本会：
✅ 检查依赖（opencode, uv）  
✅ 配置 LaunchAgent  
✅ 执行首次维护测试  
✅ 设置每日 3:00 AM 自动运行  

### 方式 2: 手动安装

```bash
cd ~/memu-server

# 1. 测试配置
./memu-guardian-opencode.sh

# 2. 安装 LaunchAgent
cp config/ai.memu.guardian.opencode.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
```

## ✅ 验证

```bash
# 查看服务状态
launchctl list | grep memu.guardian

# 应该输出类似：
# -    0    ai.memu.guardian.opencode

# 查看日志
tail -f ~/.memu/guardian.log

# 查看最新报告
ls -lh ~/.memu/reports/
cat ~/.memu/reports/guardian-*.json | jq .
```

## 📊 日常使用

### 手动触发维护
```bash
bash ~/memu-server/memu-guardian-opencode.sh
```

### 查看统计报告
```bash
# 查看最新一份
cat $(ls -t ~/.memu/reports/guardian-*.json | head -1) | jq .

# 查看所有报告
ls -lh ~/.memu/reports/

# 分析趋势（需要 jq）
for f in ~/.memu/reports/guardian-*.json; do
  echo -n "$(basename $f): "
  jq -r '.statistics.total_memories' $f
done
```

### 查看日志
```bash
# 实时日志
tail -f ~/.memu/guardian.log

# 最近 50 行
tail -50 ~/.memu/guardian.log

# 查找错误
grep ERROR ~/.memu/guardian.log
```

## 🛠️ 故障排查

### Problem 1: opencode not found
```bash
# 安装 opencode CLI
cargo install opencode-cli

# 或者使用 brew (如果有包)
brew install opencode
```

### Problem 2: API 调用失败
```bash
# 检查 key 是否设置
echo $DEEPSEEK_API_KEY
echo $GEMINI_API_KEY

# 测试 API
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

### Problem 3: MCP 连接失败
```bash
# 测试 memu MCP server
cd ~/memu
uv run python -m memu.mcp

# 应该看到 MCP 服务启动
```

### Problem 4: LaunchAgent 未运行
```bash
# 查看详细状态
launchctl print gui/$(id -u)/ai.memu.guardian.opencode

# 重启服务
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist

# 查看系统日志
log show --predicate 'subsystem contains "ai.memu"' --last 1h
```

## 📈 成本分析

### 每日维护预计 token 消耗
- 健康检查：~100 tokens
- 缓存清理：~200 tokens
- 数据库优化：~150 tokens
- 统计报告：~250 tokens
- **总计：~700 tokens/天**

### 月度成本
- 700 tokens/天 × 30 天 = **21,000 tokens/月**
- DeepSeek 免费额度：5,000,000 tokens/月
- **使用率：0.42%**（完全在免费额度内）

### 对比
- 使用 Claude Sonnet 3.5：21,000 × $3/1M = **$0.063/月**
- 使用 DeepSeek 免费：**$0/月**
- 使用 Gemini Flash：**$0/月**

## 🎯 预期效果

安装完成后，系统会：

✅ **每天 3:00 AM 自动执行维护**  
- 检查数据库健康  
- 清理过期缓存  
- 优化数据库性能  
- 生成统计报告  

✅ **保持 memu-server 高性能**  
- 数据库保持精简  
- 缓存目录不会无限增长  
- 查询速度始终最优  

✅ **完全无人值守**  
- 失败自动重试（使用 fallback model）  
- 日志自动轮转  
- 报告自动归档  

## 📚 延伸阅读

- [完整文档](GUARDIAN_FREE.md) - 详细配置和原理
- [OpenCode 配置](config/opencode-config.json) - 模型和 MCP 配置
- [System Prompt](config/guardian-system-prompt.md) - Agent 指令
- [主项目 README](README.md) - memu-server 整体介绍

---

**核心理念**：用免费模型实现零成本的 AI 运维自动化，让一人公司不再担心基础设施维护成本。
