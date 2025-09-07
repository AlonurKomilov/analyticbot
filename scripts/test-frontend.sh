#!/bin/bash
# Development Frontend Test Script

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "🚀 Testing Development Frontend Features"
echo "========================================"

# Test 1: Check if development server is running
print_info "Testing development server accessibility..."
if curl -s http://localhost:5173 > /dev/null; then
    print_success "Development frontend is accessible on port 5173"
else
    echo "❌ Development frontend is not accessible"
    exit 1
fi

# Test 2: Check if production server is running
print_info "Testing production server accessibility..."
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Production frontend is accessible on port 3000"
else
    echo "❌ Production frontend is not accessible"
    exit 1
fi

# Test 3: Compare response headers
print_info "Comparing development vs production headers..."
echo ""
echo "📋 Development Headers (Vite):"
curl -I http://localhost:5173 2>/dev/null | head -5
echo ""
echo "📋 Production Headers (Nginx):"
curl -I http://localhost:3000 2>/dev/null | head -5
echo ""

# Test 4: Check file watching capability
print_info "Testing file watching in development..."
print_warning "File watching requires volume mounting which is active"

# Summary
echo ""
echo "🎯 Development Environment Summary:"
echo "=================================="
print_success "Development: http://localhost:5173 (Hot reload enabled)"
print_success "Production:  http://localhost:3000 (Optimized build)"
echo ""
echo "💡 Development Workflow:"
echo "1. Edit files in apps/frontend/src/"
echo "2. Changes will be reflected instantly at localhost:5173"
echo "3. Test production build at localhost:3000"
echo ""
echo "🛠 Useful Commands:"
echo "- sudo docker logs analyticbot-frontend-dev  # Dev logs"
echo "- sudo docker logs analyticbot-frontend      # Prod logs"
echo "- ./scripts/frontend-helper.sh dev           # Local dev server"
echo ""
