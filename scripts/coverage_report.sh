#!/bin/bash
# Coverage Report Generator
# Created: Oct 20, 2025
# Purpose: Generate and display comprehensive coverage reports

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 AnalyticBot Test Coverage Report${NC}"
echo "========================================="
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if pytest-cov is installed
if ! python -c "import pytest_cov" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} pytest-cov not installed. Installing..."
    pip install pytest-cov
fi

# Run tests with coverage
echo ""
echo -e "${BLUE}Running tests with coverage...${NC}"
echo ""

PYTHONPATH=. pytest \
    --cov=apps \
    --cov=core \
    --cov=infra \
    --cov-report=term-missing:skip-covered \
    --cov-report=html:htmlcov \
    --cov-report=json:coverage.json \
    --cov-branch \
    -v

# Display summary
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}✓${NC} Coverage reports generated:"
echo ""
echo "  📄 Terminal: See above"
echo "  🌐 HTML: htmlcov/index.html"
echo "  📊 JSON: coverage.json"
echo ""

# Check if HTML report exists and offer to open it
if [ -f "htmlcov/index.html" ]; then
    echo -e "${YELLOW}Tip:${NC} View detailed HTML report with:"
    echo "  xdg-open htmlcov/index.html  # Linux"
    echo "  open htmlcov/index.html      # macOS"
    echo ""
fi

# Display coverage highlights
if [ -f "coverage.json" ]; then
    echo -e "${BLUE}Coverage Highlights:${NC}"
    python3 << 'EOF'
import json
import sys

try:
    with open("coverage.json") as f:
        data = json.load(f)
    
    total = data["totals"]
    percent = total["percent_covered"]
    
    # Determine color based on coverage
    if percent >= 80:
        color = "\033[0;32m"  # Green
        icon = "🟢"
    elif percent >= 60:
        color = "\033[1;33m"  # Yellow
        icon = "🟡"
    else:
        color = "\033[0;31m"  # Red
        icon = "🔴"
    
    print(f"  {icon} Overall Coverage: {color}{percent:.2f}%\033[0m")
    print(f"  📝 Lines Covered: {total['covered_lines']}/{total['num_statements']}")
    print(f"  🌿 Branches Covered: {total['covered_branches']}/{total['num_branches']}")
    print()
    
    # Top 5 best covered files
    files = []
    for file, stats in data["files"].items():
        if "test" not in file.lower():
            files.append((file, stats["summary"]["percent_covered"]))
    
    files.sort(key=lambda x: x[1], reverse=True)
    
    if files:
        print("  🏆 Top 5 Best Covered:")
        for file, cov in files[:5]:
            short_file = file.replace(data.get("meta", {}).get("cwd", ""), "").lstrip("/")
            if len(short_file) > 50:
                short_file = "..." + short_file[-47:]
            print(f"    {cov:6.2f}% - {short_file}")
    
    print()
    
    # Bottom 5 least covered files (excluding 0%)
    files_low = [f for f in files if f[1] > 0]
    files_low.sort(key=lambda x: x[1])
    
    if files_low:
        print("  ⚠️  Bottom 5 Need Improvement:")
        for file, cov in files_low[:5]:
            short_file = file.replace(data.get("meta", {}).get("cwd", ""), "").lstrip("/")
            if len(short_file) > 50:
                short_file = "..." + short_file[-47:]
            print(f"    {cov:6.2f}% - {short_file}")

except Exception as e:
    print(f"Could not parse coverage.json: {e}", file=sys.stderr)
EOF
fi

echo ""
echo -e "${GREEN}✓${NC} Coverage report complete!"
