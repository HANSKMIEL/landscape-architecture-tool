#!/bin/bash
# 🗃️ Manus Reports Archive Manager

DATE_PREFIX=$(date +%Y%m%d)
echo "🗃️ Manus Reports Archive Manager"

# List current reports
echo "📋 Current active reports:"
for file in .manus/reports/*.md; do
    if [ -f "$file" ]; then
        echo "  📄 $(basename "$file")"
    fi
done

echo "✅ Archive management ready!"
