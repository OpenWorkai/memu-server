"""memu_codegraph - Project structure analysis and caching tool."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from memu_server import config
from memu_server.service import get_service


async def generate_project_structure(project_path: str, max_depth: int = 5) -> dict[str, Any]:
    """Generate a hierarchical project structure with file metadata.
    
    Args:
        project_path: Root path of the project
        max_depth: Maximum directory depth to traverse
        
    Returns:
        Dictionary containing project structure and metadata
    """
    project_root = Path(project_path).expanduser().resolve()
    
    if not project_root.exists():
        return {"error": f"Project path does not exist: {project_path}"}
    
    # Patterns to exclude
    exclude_patterns = {
        ".git", ".svn", ".hg",
        "node_modules", ".venv", "venv", "__pycache__",
        ".cache", "dist", "build", "target",
        ".pytest_cache", ".mypy_cache", ".tox",
        ".DS_Store", "*.pyc", "*.pyo", "*.so", "*.dylib",
    }
    
    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded."""
        name = path.name
        # Exact match
        if name in exclude_patterns:
            return True
        # Pattern match
        for pattern in exclude_patterns:
            if "*" in pattern and path.match(pattern):
                return True
        return False
    
    def scan_directory(dir_path: Path, current_depth: int = 0) -> dict[str, Any]:
        """Recursively scan directory structure."""
        if current_depth > max_depth or should_exclude(dir_path):
            return {"truncated": True}
        
        result = {
            "path": str(dir_path.relative_to(project_root)),
            "type": "directory",
            "children": {},
        }
        
        try:
            for item in sorted(dir_path.iterdir()):
                if should_exclude(item):
                    continue
                
                if item.is_file():
                    stat = item.stat()
                    result["children"][item.name] = {
                        "type": "file",
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "extension": item.suffix,
                    }
                elif item.is_dir():
                    result["children"][item.name] = scan_directory(item, current_depth + 1)
        except PermissionError:
            result["error"] = "Permission denied"
        
        return result
    
    structure = scan_directory(project_root)
    
    # Add project metadata
    metadata = {
        "project_name": project_root.name,
        "project_path": str(project_root),
        "generated_at": datetime.now().isoformat(),
        "max_depth": max_depth,
    }
    
    # Calculate content hash for change detection
    structure_json = json.dumps(structure, sort_keys=True)
    content_hash = hashlib.sha256(structure_json.encode()).hexdigest()[:16]
    metadata["content_hash"] = content_hash
    
    return {
        "metadata": metadata,
        "structure": structure,
    }


async def get_cached_codegraph(project_path: str, force_refresh: bool = False) -> dict[str, Any]:
    """Get cached codeGraph or generate new one if needed.
    
    Args:
        project_path: Root path of the project
        force_refresh: Force regeneration even if cache exists
        
    Returns:
        Project codeGraph with caching info
    """
    project_root = Path(project_path).expanduser().resolve()
    
    # Cache directory in memu data folder
    cache_dir = Path(config.DB_PATH).parent / "codegraph_cache"
    cache_dir.mkdir(exist_ok=True)
    
    # Cache file name based on project path hash
    cache_key = hashlib.sha256(str(project_root).encode()).hexdigest()[:16]
    cache_file = cache_dir / f"{cache_key}.json"
    
    # Check if cache exists and is valid
    if not force_refresh and cache_file.exists():
        try:
            with open(cache_file) as f:
                cached_data = json.load(f)
            
            # Verify project path matches
            if cached_data.get("metadata", {}).get("project_path") == str(project_root):
                # Quick check: if project root's mtime hasn't changed much, use cache
                project_mtime = project_root.stat().st_mtime
                cached_time = datetime.fromisoformat(
                    cached_data["metadata"]["generated_at"]
                ).timestamp()
                
                # Cache is valid if less than 1 hour old or project unchanged
                age_seconds = datetime.now().timestamp() - cached_time
                if age_seconds < 3600 or abs(project_mtime - cached_time) < 60:
                    cached_data["cache_hit"] = True
                    cached_data["cache_age_seconds"] = int(age_seconds)
                    return cached_data
        except (json.JSONDecodeError, KeyError, OSError):
            pass  # Invalid cache, regenerate
    
    # Generate new codeGraph
    codegraph = await generate_project_structure(str(project_root))
    codegraph["cache_hit"] = False
    codegraph["cache_file"] = str(cache_file)
    
    # Save to cache
    try:
        with open(cache_file, "w") as f:
            json.dump(codegraph, f, indent=2)
    except OSError as e:
        codegraph["cache_error"] = str(e)
    
    return codegraph


async def save_codegraph_to_memory(
    project_path: str, codegraph: dict[str, Any], user_id: str
):
    """Save codeGraph as a memory item in memu.
    
    Args:
        project_path: Project path
        codegraph: Generated codeGraph data
        user_id: User ID for memory storage
    """
    service = get_service()
    
    # Format as markdown for better LLM understanding
    metadata = codegraph.get("metadata", {})
    structure = codegraph.get("structure", {})
    
    def format_tree(node: dict[str, Any], prefix: str = "", is_last: bool = True) -> list[str]:
        """Format structure as tree view."""
        lines = []
        
        if node.get("type") == "directory":
            children = node.get("children", {})
            items = sorted(children.items())
            
            for i, (name, child) in enumerate(items):
                is_last_child = i == len(items) - 1
                connector = "└── " if is_last_child else "├── "
                
                if child.get("type") == "file":
                    size = child.get("size", 0)
                    size_str = f" ({size} bytes)" if size < 10000 else f" ({size // 1024} KB)"
                    lines.append(f"{prefix}{connector}{name}{size_str}")
                elif child.get("type") == "directory":
                    lines.append(f"{prefix}{connector}{name}/")
                    extension = "    " if is_last_child else "│   "
                    lines.extend(format_tree(child, prefix + extension, is_last_child))
        
        return lines
    
    tree_lines = format_tree(structure)
    tree_text = "\n".join(tree_lines[:200])  # Limit to first 200 lines
    
    memory_text = f"""# Project Structure: {metadata.get('project_name', 'Unknown')}

**Path**: {metadata.get('project_path', '')}
**Generated**: {metadata.get('generated_at', '')}
**Hash**: {metadata.get('content_hash', '')}

## Directory Tree

```
{tree_text}
```

## Summary

This is a cached codeGraph for project `{metadata.get('project_name', '')}`.
Cache can be retrieved with project path or name.
"""
    
    # Store in memu with special memory type
    result = await service.memorize(
        resource_url=f"codegraph://{project_path}",
        modality="document",
        user={"user_id": user_id},
    )
    
    return result


# FastMCP tool function
async def memu_codegraph(
    project_path: str,
    user_id: str = "myking",
    force_refresh: bool = False,
    save_to_memory: bool = True,
    max_depth: int = 5,
) -> str:
    """Generate and cache project codeGraph structure.
    
    Args:
        project_path: Root path of the project to analyze
        user_id: User ID for memory storage
        force_refresh: Force regeneration even if cache exists
        save_to_memory: Save codeGraph to memu memory
        max_depth: Maximum directory depth to traverse
        
    Returns:
        JSON string with codeGraph and status info
    """
    try:
        # Get or generate codeGraph
        codegraph = await get_cached_codegraph(project_path, force_refresh)
        
        # Save to memory if requested
        if save_to_memory and "error" not in codegraph:
            memory_result = await save_codegraph_to_memory(project_path, codegraph, user_id)
            codegraph["memory_saved"] = True
            codegraph["memory_items_created"] = len(memory_result.memory_items)
        
        # Format response
        metadata = codegraph.get("metadata", {})
        response = {
            "success": True,
            "project_name": metadata.get("project_name"),
            "project_path": metadata.get("project_path"),
            "content_hash": metadata.get("content_hash"),
            "cache_hit": codegraph.get("cache_hit", False),
            "cache_age_seconds": codegraph.get("cache_age_seconds"),
            "generated_at": metadata.get("generated_at"),
            "structure": codegraph.get("structure"),
            "memory_saved": codegraph.get("memory_saved", False),
        }
        
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "project_path": project_path,
        }, indent=2)
