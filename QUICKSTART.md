# memu-server 快速入门

## 🚀 5 分钟上手

### 1. 设置 API Key

```bash
export OPENAI_API_KEY=sk-your-key-here
```

### 2. 验证安装

```bash
cd ~/memu-server
uv run python verify.py
```

### 3. 重启 AI 工具

- 重启 Claude Code
- 重启 Codex（如果使用）
- 重启 CodeBuddy（如果使用）

### 4. 测试记忆功能

在 Claude Code 中输入：

```
请帮我记住：今天完成了 memu 统一记忆系统的部署
```

Claude 会自动调用 `memu_memorize` 工具。

### 5. 检索记忆

```
查询我刚才记住的内容
```

Claude 会调用 `memu_retrieve` 工具返回结果。

## 📝 4 个核心工具

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `memu_memorize` | 写入记忆 | 手动记录重要信息 |
| `memu_retrieve` | 检索记忆 | 查询历史知识 |
| `memu_context` | 生成摘要 | 会话开始时获取上下文 |
| `memu_list` | 浏览分类 | 查看记忆组织结构 |

## 🔧 常用命令

```bash
# 查看数据库
sqlite3 ~/.memu/unified.db "SELECT COUNT(*) FROM memory_items"

# 手动触发同步（CodeBuddy）
~/memu-server/hooks/sync-codebuddy-memory.sh

# 重新初始化数据库
rm ~/.memu/unified.db

# 查看日志
tail -f ~/.memu/logs/memu-server.log  # (如果配置了日志)
```

## ❓ 问题？

查看完整文档：
- `~/memu-server/README.md` - 使用文档
- `~/Documents/memu-unified-memory-deployment-report.md` - 部署报告

运行验证脚本：
```bash
cd ~/memu-server && uv run python verify.py
```
