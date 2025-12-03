#!/bin/bash
#
# Smart Console Logger Replacement Script
#
# Intelligently replaces console.* calls with appropriate logger instances
# based on file context and location
#

set -e

FRONTEND_DIR="/home/abcdeveloper/projects/analyticbot/apps/frontend"
cd "$FRONTEND_DIR"

# High-priority files to process (excluding already completed)
HIGH_PRIORITY_FILES=(
    "src/store/slices/posts/usePostStore.ts:storeLogger"
    "src/store/slices/channels/useChannelStore.ts:storeLogger"
    "src/features/ai-services/api/aiServicesAPI.ts:apiLogger"
    "src/validation/apiValidators.ts:apiLogger"
    "src/utils/offlineStorage.ts:storeLogger"
    "src/utils/initializeApp.ts:uiLogger"
    "src/utils/codeSplitting.tsx:uiLogger"
    "src/utils/componentPerformance.tsx:uiLogger"
    "src/utils/performanceMonitor.tsx:uiLogger"
    "src/shared/components/feedback/EnhancedErrorBoundary.tsx:uiLogger"
)

echo "=== Smart Console Logger Replacement ==="
echo ""
echo "Processing high-priority files..."
echo ""

processed=0
failed=0

for entry in "${HIGH_PRIORITY_FILES[@]}"; do
    IFS=':' read -r file logger <<< "$entry"

    if [ ! -f "$file" ]; then
        echo "⚠️  SKIP: $file (not found)"
        continue
    fi

    # Check if file already has logger
    if grep -q "from.*utils/logger" "$file" 2>/dev/null; then
        echo "✓ SKIP: $file (logger already imported)"
        continue
    fi

    # Count console calls
    count=$(grep -c "console\." "$file" 2>/dev/null || echo 0)

    if [ "$count" -eq 0 ]; then
        echo "✓ SKIP: $file (no console calls)"
        continue
    fi

    echo "Processing: $file ($count console calls, using $logger)"

    # Calculate relative path to logger
    depth=$(echo "$file" | grep -o "/" | wc -l)
    depth=$((depth - 2)) # src/file.ts = 1 level, src/dir/file.ts = 2 levels

    import_path=""
    for ((i=0; i<depth; i++)); do
        import_path="../${import_path}"
    done
    import_path="${import_path}utils/logger"

    # Create backup
    cp "$file" "${file}.bak"

    # Find first import line to insert after
    first_import=$(grep -n "^import " "$file" | head -1 | cut -d: -f1)

    if [ -z "$first_import" ]; then
        echo "  ⚠️  No import found, skipping"
        rm "${file}.bak"
        ((failed++))
        continue
    fi

    # Add logger import
    sed -i "${first_import}a import { ${logger} } from '${import_path}';" "$file"

    # Replace console calls
    sed -i "s/console\.log(/${logger}.log(/g" "$file"
    sed -i "s/console\.error(/${logger}.error(/g" "$file"
    sed -i "s/console\.warn(/${logger}.warn(/g" "$file"
    sed -i "s/console\.info(/${logger}.info(/g" "$file"
    sed -i "s/console\.debug(/${logger}.debug(/g" "$file"

    # Check result
    new_count=$(grep -c "console\." "$file" 2>/dev/null || echo 0)
    replaced=$((count - new_count))

    if [ "$replaced" -gt 0 ]; then
        echo "  ✓ Replaced $replaced console calls"
        rm "${file}.bak"
        ((processed++))
    else
        echo "  ✗ Failed to replace"
        mv "${file}.bak" "$file"
        ((failed++))
    fi

    echo ""
done

echo ""
echo "=== Summary ==="
echo "✓ Processed: $processed files"
echo "✗ Failed: $failed files"
echo ""

# Check remaining
remaining=$(grep -r "console\." --include="*.tsx" --include="*.ts" src/ 2>/dev/null | \
    grep -v "node_modules" | grep -v "archive" | grep -v "__mocks__" | \
    grep -v "__tests__" | grep -v ".bak" | wc -l)

echo "Remaining console calls: $remaining"
echo ""

if [ "$remaining" -lt 100 ]; then
    echo "🎉 Good progress! Remaining files:"
    grep -r "console\." --include="*.tsx" --include="*.ts" src/ 2>/dev/null | \
        grep -v "node_modules" | grep -v "archive" | grep -v "__mocks__" | \
        grep -v "__tests__" | cut -d: -f1 | sort | uniq -c | sort -rn | head -20
fi

echo ""
echo "✓ Done!"
