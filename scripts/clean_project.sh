#!/bin/bash

# =============================================================================
# Python Project Cleaner Script
# =============================================================================
# This script removes all cache files, temporary files, and build artifacts
# from your Python project to keep it clean and fresh.
# =============================================================================

set -e  # Exit on error

PROJECT_ROOT="/home/abcdeveloper/projects/analyticbot"
cd "$PROJECT_ROOT"

echo "🧹 Starting project cleanup..."
echo "================================"

# Counter for removed items
REMOVED_COUNT=0

# =============================================================================
# 1. Remove Python cache files and directories
# =============================================================================
echo "📦 Removing Python cache files..."

# Remove __pycache__ directories (excluding .venv)
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name "__pycache__" -not -path "*/.venv/*" -print0 2>/dev/null)

# Remove .pyc files (excluding .venv)
PYC_COUNT=$(find "$PROJECT_ROOT" -type f -name "*.pyc" -not -path "*/.venv/*" 2>/dev/null | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    echo "  - Removing $PYC_COUNT .pyc files..."
    find "$PROJECT_ROOT" -type f -name "*.pyc" -not -path "*/.venv/*" -delete 2>/dev/null
    REMOVED_COUNT=$((REMOVED_COUNT + PYC_COUNT))
fi

# Remove .pyo files (excluding .venv)
PYO_COUNT=$(find "$PROJECT_ROOT" -type f -name "*.pyo" -not -path "*/.venv/*" 2>/dev/null | wc -l)
if [ "$PYO_COUNT" -gt 0 ]; then
    echo "  - Removing $PYO_COUNT .pyo files..."
    find "$PROJECT_ROOT" -type f -name "*.pyo" -not -path "*/.venv/*" -delete 2>/dev/null
    REMOVED_COUNT=$((REMOVED_COUNT + PYO_COUNT))
fi

# =============================================================================
# 2. Remove pytest cache
# =============================================================================
echo "🧪 Removing pytest cache..."

if [ -d "$PROJECT_ROOT/.pytest_cache" ]; then
    echo "  - Removing .pytest_cache"
    rm -rf "$PROJECT_ROOT/.pytest_cache"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

if [ -d "$PROJECT_ROOT/apps/.pytest_cache" ]; then
    echo "  - Removing apps/.pytest_cache"
    rm -rf "$PROJECT_ROOT/apps/.pytest_cache"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

# Find and remove all .pytest_cache directories
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name ".pytest_cache" -not -path "*/.venv/*" -print0 2>/dev/null)

# =============================================================================
# 3. Remove mypy cache
# =============================================================================
echo "🔍 Removing mypy cache..."

if [ -d "$PROJECT_ROOT/.mypy_cache" ]; then
    echo "  - Removing .mypy_cache"
    rm -rf "$PROJECT_ROOT/.mypy_cache"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name ".mypy_cache" -not -path "*/.venv/*" -print0 2>/dev/null)

# =============================================================================
# 4. Remove coverage files
# =============================================================================
echo "📊 Removing coverage files..."

if [ -d "$PROJECT_ROOT/htmlcov" ]; then
    echo "  - Removing htmlcov/"
    rm -rf "$PROJECT_ROOT/htmlcov"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

if [ -f "$PROJECT_ROOT/.coverage" ]; then
    echo "  - Removing .coverage"
    rm -f "$PROJECT_ROOT/.coverage"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

if [ -f "$PROJECT_ROOT/coverage.json" ]; then
    echo "  - Removing coverage.json"
    rm -f "$PROJECT_ROOT/coverage.json"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

# =============================================================================
# 5. Remove build artifacts
# =============================================================================
echo "🏗️  Removing build artifacts..."

# Remove dist directories
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name "dist" -not -path "*/.venv/*" -not -path "*/node_modules/*" -print0 2>/dev/null)

# Remove build directories
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name "build" -not -path "*/.venv/*" -not -path "*/node_modules/*" -print0 2>/dev/null)

# Remove .egg-info directories
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name "*.egg-info" -not -path "*/.venv/*" -print0 2>/dev/null)

# Remove .eggs directories
while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name ".eggs" -not -path "*/.venv/*" -print0 2>/dev/null)

# =============================================================================
# 6. Remove Ruff cache
# =============================================================================
echo "🔧 Removing Ruff cache..."

if [ -d "$PROJECT_ROOT/.ruff_cache" ]; then
    echo "  - Removing .ruff_cache"
    rm -rf "$PROJECT_ROOT/.ruff_cache"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

# =============================================================================
# 7. Remove IPython/Jupyter cache
# =============================================================================
echo "📓 Removing Jupyter/IPython cache..."

while IFS= read -r -d '' dir; do
    echo "  - Removing: $dir"
    rm -rf "$dir"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done < <(find "$PROJECT_ROOT" -type d -name ".ipynb_checkpoints" -not -path "*/.venv/*" -print0 2>/dev/null)

# =============================================================================
# 8. Remove temporary files
# =============================================================================
echo "🗑️  Removing temporary files..."

# Remove .DS_Store (macOS)
DS_STORE_COUNT=$(find "$PROJECT_ROOT" -type f -name ".DS_Store" -not -path "*/.venv/*" 2>/dev/null | wc -l)
if [ "$DS_STORE_COUNT" -gt 0 ]; then
    echo "  - Removing $DS_STORE_COUNT .DS_Store files..."
    find "$PROJECT_ROOT" -type f -name ".DS_Store" -not -path "*/.venv/*" -delete 2>/dev/null
    REMOVED_COUNT=$((REMOVED_COUNT + DS_STORE_COUNT))
fi

# Remove Thumbs.db (Windows)
THUMBS_COUNT=$(find "$PROJECT_ROOT" -type f -name "Thumbs.db" -not -path "*/.venv/*" 2>/dev/null | wc -l)
if [ "$THUMBS_COUNT" -gt 0 ]; then
    echo "  - Removing $THUMBS_COUNT Thumbs.db files..."
    find "$PROJECT_ROOT" -type f -name "Thumbs.db" -not -path "*/.venv/*" -delete 2>/dev/null
    REMOVED_COUNT=$((REMOVED_COUNT + THUMBS_COUNT))
fi

# Remove .log files in root and logs directory (keep the directory structure)
LOG_COUNT=$(find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.log" 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo "  - Removing $LOG_COUNT .log files from root..."
    find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.log" -delete 2>/dev/null
    REMOVED_COUNT=$((REMOVED_COUNT + LOG_COUNT))
fi

# =============================================================================
# 9. Remove session files (Telegram session files in root)
# =============================================================================
echo "🔐 Cleaning session files..."

SESSION_COUNT=$(find "$PROJECT_ROOT" -maxdepth 1 -type f -name "*.session" 2>/dev/null | wc -l)
if [ "$SESSION_COUNT" -gt 0 ]; then
    echo "  ⚠️  Found $SESSION_COUNT .session files in root directory"
    echo "  ℹ️  Session files are kept for safety (contain auth data)"
    echo "  ℹ️  Remove manually if needed: rm *.session"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "================================"
echo "✅ Cleanup complete!"
echo "📊 Removed $REMOVED_COUNT items"
echo "================================"
echo ""
echo "Your project is now clean! 🎉"
echo ""
echo "To keep your project clean, you can:"
echo "  1. Add this script to your workflow"
echo "  2. Run it before committing: ./clean_project.sh"
echo "  3. Add a git pre-commit hook"
echo ""
