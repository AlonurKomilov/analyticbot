#!/bin/bash
# Code Quality Check Script

echo "🔍 AnalyticBot Code Quality Check"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo -e "${BLUE}📦 Activating virtual environment...${NC}"
    source .venv/bin/activate
    echo ""
else
    echo -e "${YELLOW}⚠️  Virtual environment not found. Using system Python.${NC}"
    echo ""
fi

# Check if tools are installed
echo "📦 Checking installed tools..."
echo ""

check_tool() {
    if command -v "$1" &> /dev/null || python -m "$1" --version &> /dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is NOT installed${NC}"
        return 1
    fi
}

check_tool "mypy"
check_tool "flake8"
check_tool "ruff"
check_tool "black"
check_tool "pre-commit"

echo ""
echo "🏗️  Checking Architecture..."
echo ""

# Run custom import guard
if [ -f "scripts/guard_imports.py" ]; then
    echo "Running architecture guard..."
    python3 scripts/guard_imports.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ No architectural violations${NC}"
    else
        echo -e "${YELLOW}⚠️  Architectural violations found (see above)${NC}"
    fi
else
    echo -e "${RED}❌ guard_imports.py not found${NC}"
fi

echo ""
echo "📊 Summary"
echo "=================================="
echo "Review the output above for details."
echo ""
echo "To install missing tools:"
echo "  pip install mypy flake8 ruff black pre-commit import-linter"
echo ""
echo "To see full audit report:"
echo "  cat CODE_QUALITY_TOOLS_AUDIT.md"
