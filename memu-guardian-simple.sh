#!/bin/bash
# memu-guardian - Daily maintenance using shell scripts
# No AI needed, just direct system maintenance

set -e

MEMU_ROOT="$HOME/.memu"
LOG_FILE="$MEMU_ROOT/guardian.log"
REPORT_DIR="$MEMU_ROOT/reports"
DB_FILE="$MEMU_ROOT/unified.db"
CACHE_DIR="$MEMU_ROOT/codegraph_cache"

# Ensure directories exist
mkdir -p "$MEMU_ROOT" "$REPORT_DIR" "$CACHE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🛡️  memu-guardian started (Shell Script Mode)"

# Task 1: Health Check
log "📋 Task 1: Health Check"
DB_EXISTS=false
DB_SIZE_MB=0
CACHE_COUNT=0
CACHE_SIZE_MB=0

if [ -f "$DB_FILE" ]; then
    DB_EXISTS=true
    DB_SIZE_BYTES=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE" 2>/dev/null)
    DB_SIZE_MB=$(echo "scale=2; $DB_SIZE_BYTES / 1024 / 1024" | bc)
    log "  ✅ Database exists: $DB_SIZE_MB MB"
else
    log "  ⚠️  Database not found"
fi

if [ -d "$CACHE_DIR" ]; then
    CACHE_COUNT=$(find "$CACHE_DIR" -name "*.json" | wc -l | tr -d ' ')
    if [ "$CACHE_COUNT" -gt 0 ]; then
        CACHE_SIZE_BYTES=$(du -s "$CACHE_DIR" | awk '{print $1}')
        CACHE_SIZE_MB=$(echo "scale=2; $CACHE_SIZE_BYTES / 1024" | bc)
        log "  ✅ Cache: $CACHE_COUNT files ($CACHE_SIZE_MB MB)"
    else
        log "  ℹ️  Cache is empty"
    fi
else
    log "  ⚠️  Cache directory not found"
fi

# Task 2: Clean old caches (> 7 days)
log "📋 Task 2: Cache Cleanup"
OLD_CACHES=$(find "$CACHE_DIR" -name "*.json" -mtime +7 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_CACHES" -gt 0 ]; then
    find "$CACHE_DIR" -name "*.json" -mtime +7 -delete 2>/dev/null || true
    log "  ✅ Cleaned $OLD_CACHES old cache files"
else
    log "  ℹ️  No old caches to clean"
fi

# Task 3: Database Optimization
log "📋 Task 3: Database Optimization"
if [ -f "$DB_FILE" ] && [ "$DB_SIZE_BYTES" -gt 52428800 ]; then  # > 50MB
    log "  🔧 Database > 50MB, running VACUUM..."
    sqlite3 "$DB_FILE" "VACUUM; ANALYZE;" 2>&1 | tee -a "$LOG_FILE"
    NEW_SIZE_BYTES=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE" 2>/dev/null)
    NEW_SIZE_MB=$(echo "scale=2; $NEW_SIZE_BYTES / 1024 / 1024" | bc)
    SAVED_MB=$(echo "scale=2; ($DB_SIZE_BYTES - $NEW_SIZE_BYTES) / 1024 / 1024" | bc)
    log "  ✅ Database optimized: $DB_SIZE_MB MB → $NEW_SIZE_MB MB (saved $SAVED_MB MB)"
    DB_VACUUMED=true
else
    log "  ℹ️  Database optimization not needed (size OK)"
    DB_VACUUMED=false
fi

# Task 4: Statistics
log "📋 Task 4: Statistics"
TOTAL_MEMORIES=0
NEW_LAST_WEEK=0

if [ -f "$DB_FILE" ]; then
    TOTAL_MEMORIES=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM memory_items" 2>/dev/null || echo "0")
    NEW_LAST_WEEK=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM memory_items WHERE created_at > datetime('now', '-7 days')" 2>/dev/null || echo "0")
    log "  📊 Total memories: $TOTAL_MEMORIES"
    log "  📊 New (last 7 days): $NEW_LAST_WEEK"
fi

# Task 5: Generate Report
REPORT_FILE="$REPORT_DIR/guardian-$(date +%Y%m%d-%H%M%S).json"
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "health_check": {
    "database_exists": $DB_EXISTS,
    "database_size_mb": $DB_SIZE_MB,
    "cache_files_count": $CACHE_COUNT,
    "cache_size_mb": $CACHE_SIZE_MB
  },
  "maintenance": {
    "caches_cleaned": $OLD_CACHES,
    "database_vacuumed": $DB_VACUUMED
  },
  "statistics": {
    "total_memories": $TOTAL_MEMORIES,
    "new_memories_last_week": $NEW_LAST_WEEK
  },
  "warnings": [],
  "errors": []
}
EOF

log "  ✅ Report saved: $REPORT_FILE"

# Cleanup old reports (keep last 30 days)
OLD_REPORTS=$(find "$REPORT_DIR" -name "guardian-*.json" -mtime +30 2>/dev/null | wc -l | tr -d ' ')
if [ "$OLD_REPORTS" -gt 0 ]; then
    find "$REPORT_DIR" -name "guardian-*.json" -mtime +30 -delete 2>/dev/null || true
    log "  ✅ Cleaned $OLD_REPORTS old reports"
fi

log "🎉 Guardian maintenance completed successfully!"
exit 0
