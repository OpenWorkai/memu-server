# memu-guardian: 零成本 AI 运维

**3 步开始，永久免费。**

---

## 🚀 开始

### 1️⃣ 获取免费 API Key（2 分钟）

**DeepSeek** (推荐，国内可用)  
→ https://platform.deepseek.com/  
→ 每月 500 万 tokens 免费

**或 Google Gemini**  
→ https://aistudio.google.com/  
→ 完全免费（有 rate limit）

### 2️⃣ 设置环境变量（1 分钟）

```bash
# DeepSeek
export DEEPSEEK_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxx'
echo 'export DEEPSEEK_API_KEY="sk-xxx"' >> ~/.zshrc

# 或 Gemini  
export GEMINI_API_KEY='xxxxxxxxxxxxxxxxxxxxxxxx'
echo 'export GEMINI_API_KEY="xxx"' >> ~/.zshrc
```

### 3️⃣ 一键安装（1 分钟）

```bash
cd ~/memu-server
./install-guardian-opencode.sh
```

✅ 完成！系统会每天 3:00 AM 自动维护。

---

## 📊 它在做什么？

每天自动：
- ✅ 检查数据库健康
- ✅ 清理过期缓存（7 天以上）
- ✅ 优化数据库（如需要）
- ✅ 生成统计报告

**成本**: $0/月（使用免费模型，每天消耗 ~700 tokens）

---

## 🛠️ 常用命令

```bash
# 手动执行维护
bash ~/memu-server/memu-guardian-opencode.sh

# 查看日志
tail -f ~/.memu/guardian.log

# 查看报告
cat $(ls -t ~/.memu/reports/guardian-*.json | head -1) | jq .

# 查看服务状态
launchctl list | grep memu.guardian
```

---

## 📚 详细文档

- **快速开始** → [QUICKSTART_GUARDIAN.md](QUICKSTART_GUARDIAN.md)
- **完整文档** → [GUARDIAN_FREE.md](GUARDIAN_FREE.md)
- **文件结构** → [docs/GUARDIAN_FILES.md](docs/GUARDIAN_FILES.md)

---

## 🎯 适用场景

✅ 个人项目的零成本运维  
✅ 一人公司的基础设施维护  
✅ AI 记忆系统的自动化管理  
✅ 学习 OpenCode + MCP 的最佳实践  

---

**核心理念**: 用免费 AI 模型做运维，让一人公司不再为基础设施发愁。
