#!/bin/bash
# AnalyticBot Full Stack Validation Script
# Comprehensive testing of all system components

echo "🧪 AnalyticBot Full Stack Validation"
echo "===================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}🔍 Testing: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  WARN: $1${NC}"
}

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_test "$test_name"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command" >/dev/null 2>&1; then
        print_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_fail "$test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo ""
echo "🔧 System Component Tests"
echo "========================="

# API Tests
run_test "API Health Endpoint" "curl -f -s http://localhost:8000/health"
run_test "API Documentation" "curl -f -s http://localhost:8000/docs | grep -q 'swagger'"
run_test "API CORS Headers" "curl -f -s -I http://localhost:8000/health | grep -i 'access-control'"

# Frontend Tests  
run_test "Frontend Homepage" "curl -f -s http://localhost:3000 | grep -q 'html'"
run_test "Frontend Assets" "curl -f -s http://localhost:3000 | grep -q 'vite'"

# Database Tests
run_test "Database File Exists" "test -f data/analytics.db"
run_test "Database Connection" ".venv/bin/python -c 'import sqlite3; sqlite3.connect(\"data/analytics.db\").close()'"

# Python Environment Tests
run_test "Virtual Environment" "test -d .venv && test -f .venv/bin/python"
run_test "Required Packages" ".venv/bin/python -c 'import fastapi, aiogram, uvicorn, sqlalchemy'"

echo ""
echo "🚀 Integration Tests"
echo "===================="

# API Integration
if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
    API_RESPONSE=$(curl -s http://localhost:8000/health)
    if echo "$API_RESPONSE" | grep -q '"status":"ok"'; then
        print_pass "API returning correct health status"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_fail "API health check format incorrect"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
fi

# Configuration Tests
print_test "Configuration Loading"
TESTS_RUN=$((TESTS_RUN + 1))
if DATABASE_URL="sqlite:///data/analytics.db" ADMIN_IDS="8034732332" .venv/bin/python -c "from config.settings import settings; assert settings.DATABASE_URL" 2>/dev/null; then
    print_pass "Configuration Loading"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_fail "Configuration Loading"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Architecture Tests
print_test "Clean Architecture Structure"
TESTS_RUN=$((TESTS_RUN + 1))
if [ -d "apps" ] && [ -d "core" ] && [ -d "infra" ] && [ -d "config" ]; then
    print_pass "Clean Architecture Structure"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_fail "Clean Architecture Structure"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "📦 Infrastructure Tests"
echo "======================="

# Docker Tests
if command -v docker >/dev/null 2>&1; then
    run_test "Docker Available" "docker --version"
    run_test "Docker Compose File" "test -f docker-compose.yml"
    run_test "Dockerfile Present" "test -f docker/Dockerfile"
else
    print_warn "Docker not available - skipping Docker tests"
fi

# Node.js Tests
if command -v node >/dev/null 2>&1; then
    run_test "Node.js Available" "node --version"
    run_test "NPM Available" "npm --version"
    run_test "Frontend Dependencies" "test -f apps/frontend/package.json && test -d apps/frontend/node_modules"
else
    print_warn "Node.js not available - frontend tests limited"
fi

echo ""
echo "🔐 Security & Production Readiness"
echo "==================================="

run_test "Requirements Files" "test -f requirements.txt && test -f requirements.prod.txt"
run_test "Environment Template" "test -f .env.example"
run_test "Security Modules" "test -d core/security_engine"
run_test "Monitoring Setup" "test -d infra/monitoring"

echo ""
echo "📊 Test Results Summary"
echo "======================="

echo "Total Tests Run: $TESTS_RUN"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

PASS_RATE=$((TESTS_PASSED * 100 / TESTS_RUN))
echo "Pass Rate: ${PASS_RATE}%"

echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Full stack is operational!${NC}"
    exit 0
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠️  Most tests passed ($PASS_RATE% pass rate). System is mostly operational.${NC}"
    exit 0
else
    echo -e "${RED}❌ Multiple test failures. System needs attention.${NC}"
    exit 1
fi
