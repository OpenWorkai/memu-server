# 🎉 好消息：无需额外配置！

## ✅ 检测到现有配置

你的本机已经配置好了：

- ✅ **OpenCode CLI**: `/opt/homebrew/bin/opencode`
- ✅ **OPENROUTER_API_KEY**: 已设置（支持免费模型）
- ✅ **uv**: 已安装

Guardian 系统已自动配置使用你现有的 OpenRouter API Key！

## 🚀 立即使用

### 方式 1: 一键安装（推荐）

```bash
cd ~/memu-server
./install-guardian-opencode.sh
```

安装脚本会：
- ✅ 检测到你的 OPENROUTER_API_KEY
- ✅ 配置 LaunchAgent
- ✅ 执行首次维护测试

### 方式 2: 手动测试

```bash
cd ~/memu-server
./memu-guardian-opencode.sh
```

立即运行一次维护任务，查看效果。

## 🎯 使用的免费模型

Guardian 已配置使用 OpenRouter 的免费模型：

1. **主模型**: `google/gemini-2.0-flash-exp:free`
2. **备用 1**: `meta-llama/llama-3.3-70b-instruct:free`
3. **备用 2**: `qwen/qwen-2.5-72b-instruct:free`

这些模型**完全免费**，无需额外付费！

## 💰 成本分析

- **API Key**: 你已有的 OPENROUTER_API_KEY（无需新申请）
- **模型费用**: $0（使用免费模型）
- **月度成本**: $0

## 📊 配置文件位置

所有配置已更新为使用 OpenRouter：

- `config/opencode-config.json` - 模型配置
- `config/ai.memu.guardian.opencode.plist` - LaunchAgent
- `config/guardian-system-prompt.md` - Agent 指令

## 🔍 验证配置

运行测试脚本，确认所有配置正常：

```bash
cd ~/memu-server
./test-guardian-setup.sh
```

应该看到：
```
✅ All checks passed!
```

## 📝 下一步

### 立即安装
```bash
cd ~/memu-server
./install-guardian-opencode.sh
```

### 查看日志
```bash
tail -f ~/.memu/guardian.log
```

### 查看报告
```bash
cat ~/.memu/reports/guardian-*.json | jq .
```

## 💡 为什么选择 OpenRouter？

1. **你已经有了** - 无需新申请 API Key
2. **多个免费模型** - Gemini 2.0 Flash、Llama 3.3、Qwen 2.5
3. **自动 fallback** - 一个失败自动切换下一个
4. **统一管理** - 所有模型用同一个 API Key

## ❓ 常见问题

### Q: 需要新申请 API Key 吗？
**A: 不需要！** Guardian 会直接使用你现有的 `OPENROUTER_API_KEY`。

### Q: 免费模型够用吗？
**A: 完全够用！** 每天维护任务约 700 tokens，Gemini 2.0 Flash 完全免费。

### Q: 如果想换其他模型？
**A: 编辑 `config/opencode-config.json`**，改成任何 OpenRouter 支持的模型。

### Q: 会不会产生费用？
**A: 不会！** 配置的都是 `:free` 后缀的免费模型。

---

**准备好了！直接运行安装脚本即可。** 🚀

```bash
cd ~/memu-server && ./install-guardian-opencode.sh
```
