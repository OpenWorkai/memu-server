# 🎉 memu-server 已开源！

## 📦 仓库信息

- **GitHub URL**: https://github.com/OpenWorkai/memu-server
- **开源协议**: MIT License
- **组织**: OpenWorkai
- **主分支**: main

## 📊 项目统计

- **文件数量**: 37 个
- **代码行数**: 6,140 行
- **主要语言**: Python 3.13+
- **协议标准**: MCP (Model Context Protocol)

## 🎯 核心功能

### 统一记忆系统
- ✅ 所有 AI 工具共享一个数据库 (`~/.memu/unified.db`)
- ✅ MCP Server 实现（Claude/Codex/CodeBuddy/Gemini/OpenCode）
- ✅ 自动会话归档（通过 hooks）
- ✅ 语义检索（向量搜索 + LLM 排序）
- ✅ 跨工具记忆同步

### 零成本自动维护（Guardian）
- ✅ 使用 DeepSeek/Gemini 免费模型
- ✅ 每天 3:00 AM 自动执行
- ✅ 健康检查、缓存清理、数据库优化
- ✅ 月度成本：$0（使用率仅 0.42%）

### codegraph 支持
- ✅ 自动生成项目代码结构
- ✅ 智能缓存机制
- ✅ 增量更新
- ✅ 跨工具共享

## 📚 文档结构

### 快速开始
- **START_HERE.md** - 3 分钟快速入门
- **QUICKSTART.md** - 基础安装指南
- **QUICKSTART_GUARDIAN.md** - Guardian 详细步骤
- **README.md** - 完整项目文档

### 深度文档
- **GUARDIAN_FREE.md** - 零成本运维完整文档
- **docs/GUARDIAN_FILES.md** - 文件结构说明
- **docs/CODEGRAPH.md** - 代码图工具文档
- **DELIVERY.md** - 交付物清单

## 🚀 使用方式

### 克隆仓库
```bash
git clone https://github.com/OpenWorkai/memu-server.git
cd memu-server
```

### 安装依赖
```bash
uv sync
```

### 配置环境
```bash
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY
```

### 验证安装
```bash
uv run python verify.py
```

### 安装 Guardian（可选）
```bash
# 获取免费 API key (DeepSeek 或 Gemini)
export DEEPSEEK_API_KEY='sk-xxx'

# 一键安装
./install-guardian-opencode.sh
```

## 🎁 项目亮点

### 1. 完全开源
- MIT License（最宽松的开源协议）
- 完整的源代码和文档
- 无隐藏依赖或付费墙

### 2. 生产就绪
- 完整的错误处理
- 详细的日志记录
- 自动化测试脚本

### 3. 文档完善
- 3 层文档（快速入门 → 详细指南 → 完整文档）
- 每个功能都有示例代码
- 完整的故障排查指南

### 4. 一人公司友好
- 零成本运维（使用免费模型）
- 零维护负担（LaunchAgent 自动化）
- 零学习成本（详细文档和示例）

### 5. 可扩展性
- 模块化设计
- 易于添加新的 MCP 工具
- 支持自定义 hooks

## 📈 下一步

### 立即使用
```bash
# 克隆并开始
git clone https://github.com/OpenWorkai/memu-server.git
cd memu-server
cat START_HERE.md
```

### 贡献代码
欢迎提交 PR！参考 [README.md](https://github.com/OpenWorkai/memu-server#-贡献) 的贡献指南。

### 反馈问题
在 GitHub 提交 Issue: https://github.com/OpenWorkai/memu-server/issues

### Star 项目
如果对你有帮助，欢迎 Star ⭐️

## 🌟 技术栈

- **语言**: Python 3.13+
- **包管理**: uv
- **记忆框架**: memu
- **MCP 实现**: FastMCP
- **AI 模型**: 
  - 主模型: DeepSeek (免费)
  - 备用: Gemini 2.0 Flash (免费)
- **自动化**: LaunchAgent (macOS)
- **数据库**: SQLite

## 💡 适用场景

✅ AI 工具重度用户（Claude/Codex/CodeBuddy 等）  
✅ 需要跨工具记忆同步  
✅ 希望零成本运维 AI 基础设施  
✅ 学习 MCP 协议和 AI Agent 开发  
✅ 一人公司自动化实践  

## 🎓 学习价值

本项目是以下技术的完整实践案例：

1. **MCP 协议** - 标准的 AI 工具通信协议
2. **AI 记忆系统** - 如何构建持久化记忆
3. **零成本运维** - 使用免费模型做自动化
4. **OpenCode + MCP** - 最新的 AI Agent 技术栈
5. **一人公司自动化** - 从需要团队到一人可管理

## 📞 联系方式

- **GitHub**: [@Myking1983](https://github.com/Myking1983)
- **Email**: myking.phone@gmail.com
- **Organization**: [OpenWorkai](https://github.com/OpenWorkai)

---

## 🎊 里程碑

- ✅ 2026-07-06: 项目开源发布
- ✅ 37 个文件，6,140 行代码
- ✅ 完整的文档体系
- ✅ 零成本运维方案
- ✅ 生产就绪状态

---

**⭐️ 如果这个项目对你有帮助，欢迎 Star！**

https://github.com/OpenWorkai/memu-server
