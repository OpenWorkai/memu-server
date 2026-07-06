#!/usr/bin/env python3
"""Verify memu-server installation and generate status report."""

import asyncio
import os
import sys
from pathlib import Path


async def main():
    """Run verification checks and generate report."""
    print("=" * 60)
    print("memu-server 统一记忆系统 - 验证报告")
    print("=" * 60)
    print()

    # Check 1: Project structure
    print("📂 项目结构检查")
    project_root = Path(__file__).parent
    required_files = [
        "pyproject.toml",
        "src/memu_server/__init__.py",
        "src/memu_server/main.py",
        "src/memu_server/service.py",
        "src/memu_server/config.py",
        "src/memu_server/tools/memorize.py",
        "src/memu_server/tools/retrieve.py",
        "src/memu_server/tools/context.py",
        "src/memu_server/tools/list_mem.py",
        "hooks/claude-stop.sh",
        "hooks/codex-stop.sh",
        "hooks/codex-session-start.sh",
        "hooks/sync-codebuddy-memory.sh",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        status = "✓" if full_path.exists() else "✗"
        if not full_path.exists():
            all_exist = False
        print(f"  {status} {file_path}")
    
    print()

    # Check 2: Environment
    print("🔧 环境配置检查")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"  ✓ OPENAI_API_KEY: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("  ✗ OPENAI_API_KEY 未设置")
    print()

    # Check 3: MCP server
    print("🚀 MCP Server 检查")
    try:
        from memu_server.main import mcp
        tools = await mcp.list_tools()
        print(f"  ✓ MCP server 加载成功")
        print(f"  ✓ 注册工具 ({len(tools)}): {[t.name for t in tools]}")
        
        # Check for new codegraph tool
        if any(t.name == 'memu_codegraph' for t in tools):
            print(f"  ✓ memu_codegraph 工具已启用")
    except Exception as e:
        print(f"  ✗ MCP server 加载失败: {e}")
        all_exist = False
    print()

    # Check 4: Database path
    print("💾 数据库配置检查")
    db_path = Path.home() / ".memu" / "unified.db"
    cache_dir = Path.home() / ".memu" / "codegraph_cache"
    
    print(f"  数据库路径: {db_path}")
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"  ✓ 数据库已存在 ({size} bytes)")
    else:
        print(f"  ℹ️ 数据库将在首次使用时创建")
    
    print(f"  缓存目录: {cache_dir}")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"  ✓ 缓存目录存在 ({len(cache_files)} 个缓存文件)")
    else:
        print(f"  ℹ️ 缓存目录将自动创建")
    print()

    # Check 5: Hook scripts
    print("🔗 Hook 脚本检查")
    hook_scripts = [
        project_root / "hooks" / "claude-stop.sh",
        project_root / "hooks" / "codex-stop.sh",
        project_root / "hooks" / "codex-session-start.sh",
        project_root / "hooks" / "sync-codebuddy-memory.sh",
    ]
    
    for script in hook_scripts:
        if script.exists():
            is_executable = os.access(script, os.X_OK)
            status = "✓" if is_executable else "⚠️"
            perm = "可执行" if is_executable else "不可执行"
            print(f"  {status} {script.name} ({perm})")
        else:
            print(f"  ✗ {script.name} (不存在)")
    print()

    # Check 6: Tool configurations
    print("⚙️  工具配置检查")
    
    claude_settings = Path.home() / ".claude" / "settings.json"
    if claude_settings.exists():
        import json
        with open(claude_settings) as f:
            settings = json.load(f)
        has_mcp = "mcpServers" in settings and "memu" in settings.get("mcpServers", {})
        has_hook = False
        if "hooks" in settings and "Stop" in settings["hooks"]:
            for matcher in settings["hooks"]["Stop"]:
                for hook in matcher.get("hooks", []):
                    if "memu-server" in hook.get("command", ""):
                        has_hook = True
                        break
        
        print(f"  Claude:")
        print(f"    {'✓' if has_mcp else '✗'} MCP Server 已注册")
        print(f"    {'✓' if has_hook else '✗'} Stop Hook 已配置")
    else:
        print(f"  ⚠️  Claude settings.json 不存在")
    
    codex_hooks = Path.home() / ".codex" / "hooks.json"
    if codex_hooks.exists():
        import json
        with open(codex_hooks) as f:
            hooks = json.load(f)
        has_start = False
        has_stop = False
        
        for matcher in hooks.get("SessionStart", []):
            for hook in matcher.get("hooks", []):
                if "memu-server" in hook.get("command", ""):
                    has_start = True
        
        for matcher in hooks.get("Stop", []):
            for hook in matcher.get("hooks", []):
                if "memu-server" in hook.get("command", ""):
                    has_stop = True
        
        print(f"  Codex:")
        print(f"    {'✓' if has_start else '✗'} SessionStart Hook 已配置")
        print(f"    {'✓' if has_stop else '✗'} Stop Hook 已配置")
    else:
        print(f"  ⚠️  Codex hooks.json 不存在")
    
    codebuddy_settings = Path.home() / ".codebuddy" / "settings.json"
    if codebuddy_settings.exists():
        import json
        with open(codebuddy_settings) as f:
            settings = json.load(f)
        has_mcp = "mcpServers" in settings and "memu" in settings.get("mcpServers", {})
        print(f"  CodeBuddy:")
        print(f"    {'✓' if has_mcp else '✗'} MCP Server 已注册")
    else:
        print(f"  ⚠️  CodeBuddy settings.json 不存在")
    
    print()

    # Summary
    print("=" * 60)
    if all_exist:
        print("✅ 所有核心组件验证通过")
        print()
        print("下一步:")
        print("  1. 确保 OPENAI_API_KEY 已设置")
        print("  2. 重启 Claude Code / Codex / CodeBuddy")
        print("  3. 在任一工具中测试 memu_memorize / memu_retrieve")
    else:
        print("⚠️  部分组件需要配置")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
