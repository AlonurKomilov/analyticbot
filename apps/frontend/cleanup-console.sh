#!/bin/bash

# Script to clean up console.log statements in React components
# Replace development console.logs with proper logging or remove them

echo "🧹 Cleaning up console.log statements..."

# Find all console.log statements
echo "Found console.log statements in:"
grep -r "console\.log" /home/alonur/analyticbot/apps/frontend/src --include="*.jsx" --include="*.js" | wc -l

# Create a list of files with console.log
FILES_WITH_CONSOLE=$(grep -r "console\.log" /home/alonur/analyticbot/apps/frontend/src --include="*.jsx" --include="*.js" -l)

echo "Files to clean:"
echo "$FILES_WITH_CONSOLE"

# For each file, show the console.log statements
for file in $FILES_WITH_CONSOLE; do
  echo "=== $file ==="
  grep -n "console\.log" "$file"
  echo ""
done