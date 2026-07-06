# memu-guardian 文件结构

零成本自动维护系统的完整文件清单。

## 📁 核心文件

### 🚀 启动脚本
```
memu-guardian-opencode.sh           # OpenCode + 免费模型版本（推荐）
memu-guardian.py                    # Python + OpenAI 版本（需付费 API）
```

### 📦 安装脚本
```
install-guardian-opencode.sh        # 一键安装 OpenCode 版本
install-guardian.sh                 # 一键安装 Python 版本
test-guardian-setup.sh              # 环境检测和测试脚本
```

### 📖 文档
```
QUICKSTART_GUARDIAN.md             # ⭐️ 快速开始指南（从这里开始）
GUARDIAN_FREE.md                   # 完整文档和配置说明
README.md                          # 主项目文档（已添加 Guardian 入口）
```

### ⚙️ 配置文件
```
config/
├── opencode-config.json                    # OpenCode 配置（模型、MCP）
├── guardian-system-prompt.md              # Agent 系统提示词
├── ai.memu.guardian.opencode.plist        # LaunchAgent (OpenCode)
├── ai.memu.guardian.plist                 # LaunchAgent (Python)
└── .env.guardian.example                  # API Key 示例
```

## 🎯 使用流程

### 首次安装
```bash
cd ~/memu-server

# 1. 查看快速开始指南
cat QUICKSTART_GUARDIAN.md

# 2. 获取免费 API Key（DeepSeek 或 Gemini）
#    见 QUICKSTART_GUARDIAN.md

# 3. 设置环境变量
export DEEPSEEK_API_KEY='sk-xxx'

# 4. 测试环境
./test-guardian-setup.sh

# 5. 一键安装
./install-guardian-opencode.sh
```

### 日常使用
```bash
# 手动触发维护
bash ~/memu-server/memu-guardian-opencode.sh

# 查看日志
tail -f ~/.memu/guardian.log

# 查看报告
cat ~/.memu/reports/guardian-*.json | jq .

# 查看服务状态
launchctl list | grep memu.guardian
```

## 🔄 自动化流程

```
┌─────────────────────────────────────────────────┐
│  每天 3:00 AM (LaunchAgent 触发)                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  memu-guardian-opencode.sh 启动                 │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  OpenCode CLI 加载配置                          │
│  - DeepSeek API (主)                            │
│  - Gemini API (备用)                            │
│  - MCP Server (memu)                            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  执行维护任务 (system prompt 指引)              │
│  1. 健康检查 (数据库/缓存/MCP)                  │
│  2. 清理缓存 (删除 7 天以上)                    │
│  3. 优化数据库 (VACUUM if > 50MB)               │
│  4. 生成报告 (JSON 格式)                        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  输出结果                                        │
│  - guardian.log (操作日志)                      │
│  - reports/guardian-*.json (统计报告)           │
└─────────────────────────────────────────────────┘
```

## 📂 运行时文件

Guardian 运行时会在 `~/.memu/` 创建以下文件：

```
~/.memu/
├── unified.db                              # memu 数据库（只读/优化）
├── codegraph_cache/                        # 代码图缓存（会清理）
├── guardian.log                            # 主日志
├── guardian-opencode-stdout.log            # stdout
├── guardian-opencode-stderr.log            # stderr
├── guardian-task-*.txt                     # 任务文件（临时，7天自动删除）
└── reports/
    └── guardian-YYYYMMDD-HHMMSS.json       # 统计报告（30天自动删除）
```

## 🔑 API Key 管理

### 方式 1: 环境变量（推荐）
```bash
# 在 ~/.zshrc 中添加
export DEEPSEEK_API_KEY='sk-xxx'
export GEMINI_API_KEY='xxx'
```

### 方式 2: .env 文件
```bash
# 复制模板
cp .env.guardian.example .env.guardian

# 编辑并填入 key
vim .env.guardian

# 加载到环境
source .env.guardian
```

### 方式 3: LaunchAgent 直接配置
```bash
# 编辑 plist 文件
vim ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist

# 在 EnvironmentVariables 部分直接填入 key
```

## 🎛️ 配置调整

### 修改执行时间
编辑 `~/Library/LaunchAgents/ai.memu.guardian.opencode.plist`:
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>3</integer>    <!-- 改为你想要的小时 -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

重新加载：
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.memu.guardian.opencode.plist
```

### 修改维护策略
编辑 `config/guardian-system-prompt.md`:
- 缓存清理阈值（默认 7 天）
- 数据库优化阈值（默认 50MB）
- 报告保留时长（默认 30 天）

### 切换模型
编辑 `config/opencode-config.json`:
```json
{
  "model": {
    "provider": "google",           // 改为 gemini
    "name": "gemini-2.0-flash-exp"
  }
}
```

## 🆚 版本对比

|              | OpenCode 版本 (推荐)    | Python 版本          |
|--------------|-------------------------|----------------------|
| **成本**     | 免费 (DeepSeek/Gemini)  | 付费 (OpenAI)        |
| **配置**     | opencode-config.json    | 代码内硬编码         |
| **MCP**      | 原生支持 (stdio)        | 需要 HTTP 端口       |
| **依赖**     | opencode CLI            | Python + OpenAI SDK  |
| **扩展性**   | 易于添加新工具          | 需要修改代码         |
| **推荐场景** | 日常自动维护（零成本）  | 需要更复杂的逻辑     |

## 💡 开发和调试

### 本地测试
```bash
# 干跑（不实际执行，查看生成的任务）
cat ~/.memu/guardian-task-*.txt

# 手动运行 OpenCode
cd ~/memu-server
opencode --config config/opencode-config.json

# 然后粘贴任务描述
```

### 修改 System Prompt
```bash
vim config/guardian-system-prompt.md

# 立即测试（不等 cron）
bash memu-guardian-opencode.sh
```

### 查看 OpenCode 日志
```bash
# LaunchAgent 的输出
tail -f ~/.memu/guardian-opencode-stdout.log
tail -f ~/.memu/guardian-opencode-stderr.log

# Guardian 主日志
tail -f ~/.memu/guardian.log
```

## 🔐 安全建议

1. **不要将 API Key 提交到 Git**
   ```bash
   # .gitignore 中已包含
   .env.guardian
   config/*.plist
   ```

2. **定期轮换 API Key**
   ```bash
   # DeepSeek: https://platform.deepseek.com/api_keys
   # Gemini: https://aistudio.google.com/apikey
   ```

3. **监控 API 使用量**
   - DeepSeek: https://platform.deepseek.com/usage
   - Gemini: https://aistudio.google.com/quota

4. **限制 LaunchAgent 权限**
   - Guardian 只读取数据库
   - 只清理缓存，不删除记忆数据
   - 日志和报告自动轮转

## 📞 获取帮助

遇到问题？按顺序检查：

1. **运行测试脚本**
   ```bash
   ./test-guardian-setup.sh
   ```

2. **查看日志**
   ```bash
   tail -50 ~/.memu/guardian.log
   ```

3. **手动执行**
   ```bash
   bash memu-guardian-opencode.sh
   ```

4. **查看文档**
   - [快速开始](QUICKSTART_GUARDIAN.md)
   - [完整文档](GUARDIAN_FREE.md)

---

**项目目标**：让 memu-server 永远保持健康，零成本，零运维负担。
