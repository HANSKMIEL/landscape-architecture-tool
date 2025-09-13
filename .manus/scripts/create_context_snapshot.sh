#!/bin/bash
# 📸 Manus Context Snapshot Creator

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SNAPSHOT_NAME="session_${TIMESTAMP}"

echo "🔄 Creating Manus context snapshot: $SNAPSHOT_NAME"

# Create snapshot
tar -czf ".manus/context/${SNAPSHOT_NAME}.tar.gz" .manus/reports/ .manus/TASK_CONTINUATION.md

echo "✅ Context snapshot created: ${SNAPSHOT_NAME}.tar.gz"
