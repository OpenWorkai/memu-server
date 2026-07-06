#!/usr/bin/env python3
"""memu-guardian - Daily maintenance agent for memu-server.

This agent runs periodic tasks to keep the memory system healthy:
- Health checks and status monitoring
- Cache cleanup and optimization
- Memory consolidation and summarization
- Usage statistics and reporting
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Configuration
MEMU_ROOT = Path.home() / ".memu"
DB_PATH = MEMU_ROOT / "unified.db"
CACHE_DIR = MEMU_ROOT / "codegraph_cache"
REPORTS_DIR = MEMU_ROOT / "reports"
LOG_FILE = MEMU_ROOT / "guardian.log"

# Maintenance settings
MAX_CACHE_AGE_DAYS = 7  # Remove caches older than 7 days
MAX_CACHE_SIZE_MB = 100  # Remove old caches if total size exceeds this
VACUUM_THRESHOLD_MB = 50  # Run VACUUM if DB is larger than this


def log(message: str, level: str = "INFO") -> None:
    """Write log message to file and console."""
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    print(log_entry)
    
    # Append to log file
    try:
        MEMU_ROOT.mkdir(exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Warning: Failed to write log: {e}")


class MemuGuardian:
    """Daily maintenance agent for memu-server."""
    
    def __init__(self):
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "tasks_completed": [],
            "tasks_failed": [],
            "warnings": [],
        }
    
    async def run_all_tasks(self) -> dict[str, Any]:
        """Run all maintenance tasks."""
        log("🛡️  memu-guardian started")
        
        tasks = [
            ("health_check", self.health_check),
            ("cache_cleanup", self.cleanup_old_caches),
            ("database_maintenance", self.maintain_database),
            ("generate_stats", self.generate_statistics),
            ("memory_consolidation", self.consolidate_memories),
        ]
        
        for task_name, task_func in tasks:
            try:
                log(f"Running task: {task_name}")
                await task_func()
                self.stats["tasks_completed"].append(task_name)
                log(f"✓ Task completed: {task_name}")
            except Exception as e:
                log(f"✗ Task failed: {task_name} - {e}", "ERROR")
                self.stats["tasks_failed"].append({"task": task_name, "error": str(e)})
        
        # Generate final report
        report = await self.generate_report()
        
        log(f"🛡️  memu-guardian completed: {len(self.stats['tasks_completed'])} tasks")
        
        return report
    
    async def health_check(self) -> None:
        """Check system health and component status."""
        log("Performing health check...")
        
        # Check database
        if not DB_PATH.exists():
            self.stats["warnings"].append("Database does not exist yet")
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                self.stats["warnings"].append("Database has no tables")
            
            # Get record counts
            for table in ["memory_items", "memory_categories", "resources"]:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    log(f"  {table}: {count} records")
            
            conn.close()
            
        except Exception as e:
            self.stats["warnings"].append(f"Database health check failed: {e}")
        
        # Check cache directory
        if CACHE_DIR.exists():
            cache_files = list(CACHE_DIR.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            log(f"  Cache: {len(cache_files)} files, {total_size // 1024} KB")
        else:
            log("  Cache directory does not exist yet")
    
    async def cleanup_old_caches(self) -> None:
        """Remove old or excessive cache files."""
        if not CACHE_DIR.exists():
            log("Cache directory does not exist, skipping cleanup")
            return
        
        cache_files = list(CACHE_DIR.glob("*.json"))
        if not cache_files:
            log("No cache files to clean up")
            return
        
        now = datetime.now()
        removed_count = 0
        freed_bytes = 0
        
        # Remove files older than MAX_CACHE_AGE_DAYS
        for cache_file in cache_files:
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days > MAX_CACHE_AGE_DAYS:
                size = cache_file.stat().st_size
                cache_file.unlink()
                removed_count += 1
                freed_bytes += size
                log(f"  Removed old cache: {cache_file.name} (age: {age_days} days)")
        
        # Check total cache size
        remaining_files = list(CACHE_DIR.glob("*.json"))
        total_size_mb = sum(f.stat().st_size for f in remaining_files) / (1024 * 1024)
        
        if total_size_mb > MAX_CACHE_SIZE_MB:
            # Remove oldest files until under threshold
            sorted_files = sorted(remaining_files, key=lambda f: f.stat().st_mtime)
            
            while total_size_mb > MAX_CACHE_SIZE_MB and sorted_files:
                oldest = sorted_files.pop(0)
                size = oldest.stat().st_size
                oldest.unlink()
                removed_count += 1
                freed_bytes += size
                total_size_mb -= size / (1024 * 1024)
                log(f"  Removed for size limit: {oldest.name}")
        
        if removed_count > 0:
            log(f"Cache cleanup: removed {removed_count} files, freed {freed_bytes // 1024} KB")
        else:
            log("No cache files needed cleanup")
    
    async def maintain_database(self) -> None:
        """Perform database maintenance tasks."""
        if not DB_PATH.exists():
            log("Database does not exist, skipping maintenance")
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get database size
            db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
            log(f"Database size: {db_size_mb:.2f} MB")
            
            # Run VACUUM if database is large
            if db_size_mb > VACUUM_THRESHOLD_MB:
                log("Running VACUUM to optimize database...")
                cursor.execute("VACUUM")
                new_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
                saved_mb = db_size_mb - new_size_mb
                log(f"VACUUM completed: saved {saved_mb:.2f} MB")
            
            # Analyze tables for query optimization
            cursor.execute("ANALYZE")
            log("Database analysis completed")
            
            conn.close()
            
        except Exception as e:
            raise Exception(f"Database maintenance failed: {e}")
    
    async def generate_statistics(self) -> dict[str, Any]:
        """Generate usage statistics."""
        if not DB_PATH.exists():
            log("Database does not exist, skipping statistics")
            return {}
        
        stats = {}
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            # Count records in each table
            for table in tables:
                if not table.endswith("_fts") and not table.startswith("sqlite_"):
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Memory items by type
            if "memory_items" in tables:
                cursor.execute(
                    "SELECT memory_type, COUNT(*) FROM memory_items GROUP BY memory_type"
                )
                stats["memory_by_type"] = dict(cursor.fetchall())
            
            # Recent activity (last 7 days)
            if "memory_items" in tables:
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute(
                    f"SELECT COUNT(*) FROM memory_items WHERE created_at > '{week_ago}'"
                )
                stats["memories_last_week"] = cursor.fetchone()[0]
            
            conn.close()
            
            log("Statistics generated:")
            for key, value in stats.items():
                log(f"  {key}: {value}")
            
            return stats
            
        except Exception as e:
            self.stats["warnings"].append(f"Statistics generation failed: {e}")
            return {}
    
    async def consolidate_memories(self) -> None:
        """Consolidate and deduplicate memories (future implementation)."""
        log("Memory consolidation: Not yet implemented")
        # TODO: Implement memory consolidation logic
        # - Find duplicate or similar memories
        # - Merge related memories
        # - Update reinforcement counts
    
    async def generate_report(self) -> dict[str, Any]:
        """Generate maintenance report."""
        REPORTS_DIR.mkdir(exist_ok=True)
        
        report = {
            "guardian_run": self.stats,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Save report to file
        report_file = REPORTS_DIR / f"guardian-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        log(f"Report saved: {report_file}")
        
        # Keep only last 30 reports
        reports = sorted(REPORTS_DIR.glob("guardian-*.json"))
        if len(reports) > 30:
            for old_report in reports[:-30]:
                old_report.unlink()
                log(f"  Removed old report: {old_report.name}")
        
        return report


async def main():
    """Main entry point."""
    guardian = MemuGuardian()
    
    try:
        report = await guardian.run_all_tasks()
        
        # Print summary
        print()
        print("=" * 60)
        print("📊 Maintenance Summary")
        print("=" * 60)
        print(f"Tasks completed: {len(report['guardian_run']['tasks_completed'])}")
        print(f"Tasks failed: {len(report['guardian_run']['tasks_failed'])}")
        print(f"Warnings: {len(report['guardian_run']['warnings'])}")
        
        if report['guardian_run']['tasks_failed']:
            print("\n❌ Failed tasks:")
            for task in report['guardian_run']['tasks_failed']:
                print(f"  - {task['task']}: {task['error']}")
        
        if report['guardian_run']['warnings']:
            print("\n⚠️  Warnings:")
            for warning in report['guardian_run']['warnings']:
                print(f"  - {warning}")
        
        print("=" * 60)
        
        # Exit code
        return 0 if not report['guardian_run']['tasks_failed'] else 1
        
    except Exception as e:
        log(f"Guardian run failed: {e}", "ERROR")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
