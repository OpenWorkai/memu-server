# memu-server - 统一 AI 记忆系统

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://spec.modelcontextprotocol.io/)

基于 **[memu](https://github.com/mem-u/memu)** 记忆框架，为 Claude / Codex / CodeBuddy / Gemini / OpenCode 提供统一的记忆存储和检索服务。

---

## ⚡️ 3 分钟快速开始

**→ [START_HERE.md](START_HERE.md)** ← 零成本自动维护，永久免费运行

---

## 🛡️ 自动维护（NEW）

**[零成本守护者：OpenCode + 免费模型](GUARDIAN_FREE.md)** - 使用 DeepSeek/Gemini 免费额度实现每日自动维护。无 API 成本，无需人工干预。

## 🎯 核心特性

- **一个数据库**: 所有 AI 工具共享 `~/.memu/unified.db`，无数据孤岛
- **一个 MCP Server**: 统一的 MCP 协议接口
- **自动记忆**: 通过 Hook 自动归档会话摘要
- **语义检索**: 支持向量检索和 LLM 排序
- **跨工具同步**: Claude 学习的知识，Codex 也能感知

## 📦 安装

### 1. 安装依赖

```bash
cd ~/memu-server
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY
```

### 3. 验证安装

```bash
uv run python verify.py
```

## 🔧 工具集成

### Claude Code

已自动配置：
- ✅ MCP Server 已注册（`~/.claude/settings.json`）
- ✅ Stop Hook 已配置（会话结束自动归档）

**使用方式**：
- 在对话中可直接调用 `memu_memorize` / `memu_retrieve` / `memu_context` 工具

### Codex

配置文件：`~/.codex/hooks.json`（已自动修改）

Hook 脚本：
- `~/memu-server/hooks/codex-session-start.sh`
- `~/memu-server/hooks/codex-stop.sh`

### CodeBuddy

已自动配置：
- ✅ MCP Server 已注册（`~/.codebuddy/settings.json`）

**同步脚本**：
```bash
~/memu-server/hooks/sync-codebuddy-memory.sh
```

## 🛠️ MCP 工具

### memu_memorize

写入新记忆（自动提取结构化信息）。

**参数**：
- `text`: 要记忆的文本内容
- `source`: 来源标识（claude/codex/codebuddy）
- `user_id`: 用户 ID（默认 "myking"）

### memu_retrieve

检索相关记忆。

**参数**：
- `query`: 检索查询文本
- `user_id`: 用户 ID
- `top_k`: 返回结果数量（默认 5）

### memu_context

生成 Markdown 格式的上下文摘要。

**参数**：
- `user_id`: 用户 ID

### memu_list

浏览记忆分类和条目。

**参数**：
- `user_id`: 用户 ID
- `category`: 可选，筛选特定分类

## 📊 数据库结构

`~/.memu/unified.db` 使用 memu 原生 schema：

| 表名 | 内容 |
|------|------|
| resources | 原始输入（对话文本、来源工具、时间戳） |
| memory_items | 提取的结构化记忆 |
| memory_categories | 自动分类 |
| category_items | 关联关系 |

## 🚀 启动

### 作为 stdio server（自动）

已在各工具的 settings.json 中配置：
```json
{
  "mcpServers": {
    "memu": {
      "command": "uv",
      "args": ["run", "--project", "/Users/myking/memu-server", "memu-server"]
    }
  }
}
```

### 手动测试

```bash
cd ~/memu-server
OPENAI_API_KEY=your-key uv run memu-server
```

## 🔍 故障排查

### MCP Server 无法启动

```bash
cd ~/memu-server && uv sync
echo $OPENAI_API_KEY
uv run python verify.py
```

### Hook 脚本不执行

```bash
chmod +x ~/memu-server/hooks/*.sh
echo '{"summary":"test"}' | ~/memu-server/hooks/claude-stop.sh
```

## 📚 相关文档

- [memu 官方文档](https://github.com/mem-u/memu)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [MCP 协议规范](https://spec.modelcontextprotocol.io/)

## 🔍 memu_codegraph - 项目结构分析

### 功能

自动生成和缓存项目代码结构（codeGraph）：

- ✅ **一次生成，多次复用** - 智能缓存机制
- ✅ **增量更新** - 自动检测文件变化
- ✅ **结构化存储** - 保存到 memu 记忆系统
- ✅ **跨工具共享** - 所有 AI 工具可访问

### 使用示例

```bash
# 在 Claude Code 中
请用 memu_codegraph 分析 ~/memu-server 的项目结构
```

**参数**：
- `project_path`: 项目根目录（必填）
- `force_refresh`: 强制重新生成（默认 false）
- `save_to_memory`: 保存到记忆系统（默认 true）
- `max_depth`: 最大目录深度（默认 5）

**返回结构**：
```json
{
  "success": true,
  "project_name": "memu-server",
  "content_hash": "c25cd9c75b632495",
  "cache_hit": false,
  "structure": {...},
  "memory_saved": true
}
```

### 缓存机制

- **缓存位置**: `~/.memu/codegraph_cache/`
- **缓存策略**: 1小时内或项目未修改时使用缓存
- **自动刷新**: 检测到文件变化自动更新

详细文档：[docs/CODEGRAPH.md](docs/CODEGRAPH.md)


## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

```bash
# 克隆仓库
git clone https://github.com/Myking1983/memu-server.git
cd memu-server

# 安装依赖
uv sync

# 运行测试
uv run python verify.py

# 测试 Guardian（需要设置 DEEPSEEK_API_KEY 或 GEMINI_API_KEY）
./test-guardian-setup.sh
```

## 📝 License

本项目采用 [MIT License](LICENSE) 开源。

## 🙏 致谢

- [memu](https://github.com/mem-u/memu) - 强大的 AI 记忆框架
- [FastMCP](https://github.com/jlowin/fastmcp) - 简洁的 MCP 服务器实现
- [OpenCode](https://github.com/simonw/opencode) - 优秀的 AI Agent CLI

## 📬 联系方式

- GitHub: [@Myking1983](https://github.com/Myking1983)
- Email: myking.phone@gmail.com

---

**⭐️ 如果这个项目对你有帮助，欢迎 Star！**
