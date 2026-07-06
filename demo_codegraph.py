#!/usr/bin/env python3
"""Demo script for memu_codegraph tool."""

import asyncio
import json
from pathlib import Path

from memu_server.tools.codegraph import memu_codegraph


async def demo():
    """Run interactive demo of codegraph functionality."""
    print("=" * 60)
    print("memu_codegraph - 项目结构分析工具演示")
    print("=" * 60)
    print()

    # Demo 1: Scan memu-server itself
    print("📊 演示 1: 扫描 memu-server 项目")
    print("-" * 60)
    
    result = await memu_codegraph(
        project_path="~/memu-server",
        save_to_memory=False,  # Don't save for demo
        force_refresh=True,
        max_depth=3
    )
    
    data = json.loads(result)
    
    if data["success"]:
        print(f"✓ 扫描完成")
        print(f"  项目名称: {data['project_name']}")
        print(f"  项目路径: {data['project_path']}")
        print(f"  内容哈希: {data['content_hash']}")
        print(f"  缓存命中: {data['cache_hit']}")
        print()
        
        # Show structure summary
        structure = data["structure"]
        children = structure.get("children", {})
        
        print(f"  顶层结构 ({len(children)} 项):")
        for name, item in sorted(children.items())[:15]:
            item_type = item.get("type", "unknown")
            if item_type == "file":
                size = item.get("size", 0)
                size_str = f"{size} bytes" if size < 10000 else f"{size // 1024} KB"
                print(f"    📄 {name} ({size_str})")
            elif item_type == "directory":
                subchildren = item.get("children", {})
                print(f"    📁 {name}/ ({len(subchildren)} 项)")
    else:
        print(f"✗ 扫描失败: {data.get('error')}")
    
    print()
    print("-" * 60)
    print()

    # Demo 2: Test caching
    print("📊 演示 2: 测试缓存机制")
    print("-" * 60)
    
    print("第一次调用（应该使用缓存）...")
    result2 = await memu_codegraph(
        project_path="~/memu-server",
        save_to_memory=False,
        force_refresh=False
    )
    
    data2 = json.loads(result2)
    print(f"  缓存命中: {data2['cache_hit']}")
    if data2['cache_hit']:
        print(f"  缓存年龄: {data2['cache_age_seconds']} 秒")
        print(f"  ✓ 缓存工作正常！")
    
    print()
    print("-" * 60)
    print()

    # Demo 3: Scan a different project
    print("📊 演示 3: 扫描其他项目（如果存在）")
    print("-" * 60)
    
    test_projects = [
        "~/memu",
        "~/workspaces/claude-projects/claude-mem",
        "~/.claude",
    ]
    
    for project_path in test_projects:
        expanded = Path(project_path).expanduser()
        if expanded.exists():
            print(f"\n扫描: {project_path}")
            result3 = await memu_codegraph(
                project_path=str(expanded),
                save_to_memory=False,
                max_depth=2
            )
            
            data3 = json.loads(result3)
            if data3["success"]:
                print(f"  ✓ 项目名称: {data3['project_name']}")
                print(f"  ✓ 内容哈希: {data3['content_hash']}")
                structure3 = data3["structure"]["children"]
                print(f"  ✓ 顶层项数: {len(structure3)}")
                break
    else:
        print("  ℹ️ 未找到测试项目")
    
    print()
    print("=" * 60)
    print("演示完成！")
    print()
    print("查看缓存文件:")
    cache_dir = Path.home() / ".memu" / "codegraph_cache"
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"  位置: {cache_dir}")
        print(f"  文件数: {len(cache_files)}")
        for f in cache_files:
            size = f.stat().st_size
            print(f"    - {f.name} ({size} bytes)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())
