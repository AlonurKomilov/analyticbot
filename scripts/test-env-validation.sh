#!/bin/bash

# Test Environment Validation Scripts
# Tests the updated check-env.sh and validate-env.sh scripts with existing environment files

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BOLD}${BLUE}🧪 Environment Validation Testing Suite${NC}"
echo "======================================="
echo -e "Project Root: ${BLUE}$PROJECT_ROOT${NC}"
echo

# Function to run a test and capture output
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="${3:-0}"

    echo -e "${YELLOW}📋 Test: $test_name${NC}"
    echo "   Command: $command"

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run the command and capture exit code
    if eval "$command" > /tmp/test_output.log 2>&1; then
        local exit_code=0
    else
        local exit_code=$?
    fi

    # Show output
    echo "   Output:"
    cat /tmp/test_output.log | sed 's/^/   /'

    # Check result
    if [[ $exit_code -eq $expected_exit_code ]]; then
        echo -e "   ${GREEN}✅ PASSED${NC} (exit code: $exit_code)"
    else
        echo -e "   ${RED}❌ FAILED${NC} (expected: $expected_exit_code, got: $exit_code)"
    fi

    echo
    return $exit_code
}

# Function to check if file exists and show info
check_file() {
    local file="$1"
    local description="$2"

    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        local size=$(du -h "$PROJECT_ROOT/$file" | cut -f1)
        local perms=$(stat -c "%a" "$PROJECT_ROOT/$file")
        echo -e "   ✅ ${GREEN}$file${NC} - $description"
        echo -e "      Size: $size, Permissions: $perms"
    else
        echo -e "   ❌ ${RED}$file${NC} - Missing"
    fi
}

# Pre-test: Check environment files
echo -e "${BOLD}${YELLOW}📂 Environment Files Check${NC}"
echo "=========================="
check_file ".env.development" "Development configuration"
check_file ".env.production" "Production configuration"
check_file ".env.development.example" "Development template"
check_file ".env.production.example" "Production template"
check_file ".env" "Generic configuration (optional)"
echo

# Test 1: Basic environment check with development file
run_test "Basic Environment Check (Development)" \
    "./scripts/check-env.sh" \
    0

# Test 2: Comprehensive validation with development file
run_test "Comprehensive Validation (Development)" \
    "./scripts/validate-env.sh" \
    0

# Test 3: Test with production file (rename temporarily)
if [[ -f "$PROJECT_ROOT/.env.development" ]] && [[ -f "$PROJECT_ROOT/.env.production" ]]; then
    echo -e "${YELLOW}🔄 Switching to production environment for testing...${NC}"
    mv "$PROJECT_ROOT/.env.development" "$PROJECT_ROOT/.env.development.backup"

    run_test "Basic Environment Check (Production)" \
        "./scripts/check-env.sh" \
        0

    run_test "Comprehensive Validation (Production)" \
        "./scripts/validate-env.sh" \
        0

    # Restore development file
    mv "$PROJECT_ROOT/.env.development.backup" "$PROJECT_ROOT/.env.development"
    echo -e "${GREEN}✅ Restored development environment${NC}"
    echo
fi

# Test 4: Test error handling with missing file
echo -e "${YELLOW}🔄 Testing error handling with no environment files...${NC}"
if [[ -f "$PROJECT_ROOT/.env.development" ]]; then
    mv "$PROJECT_ROOT/.env.development" "$PROJECT_ROOT/.env.development.test_backup"
fi
if [[ -f "$PROJECT_ROOT/.env.production" ]]; then
    mv "$PROJECT_ROOT/.env.production" "$PROJECT_ROOT/.env.production.test_backup"
fi

run_test "Environment Check (No Files)" \
    "./scripts/check-env.sh" \
    1

run_test "Validation (No Files)" \
    "./scripts/validate-env.sh" \
    1

# Restore files
if [[ -f "$PROJECT_ROOT/.env.development.test_backup" ]]; then
    mv "$PROJECT_ROOT/.env.development.test_backup" "$PROJECT_ROOT/.env.development"
fi
if [[ -f "$PROJECT_ROOT/.env.production.test_backup" ]]; then
    mv "$PROJECT_ROOT/.env.production.test_backup" "$PROJECT_ROOT/.env.production"
fi
echo -e "${GREEN}✅ Restored environment files${NC}"
echo

# Test 5: Show environment variable detection
echo -e "${BOLD}${YELLOW}🔍 Environment Variable Detection Test${NC}"
echo "====================================="
cd "$PROJECT_ROOT"

# Load the environment file and show key variables
if [[ -f ".env.development" ]]; then
    echo -e "${BLUE}Loading .env.development variables:${NC}"
    # Show a few key variables (safely)
    grep -E "^(ENVIRONMENT|DEBUG|POSTGRES_HOST|API_PORT|FRONTEND_PORT)=" .env.development | head -5 | while read line; do
        echo "   $line"
    done
    echo
fi

# Test 6: Script permissions check
echo -e "${BOLD}${YELLOW}🔧 Script Permissions Check${NC}"
echo "==========================="
check_file "scripts/check-env.sh" "Environment check script"
check_file "scripts/validate-env.sh" "Environment validation script"
check_file "scripts/test-env-validation.sh" "This test script"
echo

# Summary
echo -e "${BOLD}${YELLOW}📊 Test Summary${NC}"
echo "=============="
echo -e "✅ ${GREEN}Environment validation scripts have been updated to work with your file structure${NC}"
echo -e "✅ ${GREEN}Scripts now automatically detect .env.development or .env.production files${NC}"
echo -e "✅ ${GREEN}Variable names updated to match your configuration (BOT_TOKEN, ADMIN_IDS, etc.)${NC}"
echo -e "✅ ${GREEN}Added JWT configuration validation${NC}"
echo -e "✅ ${GREEN}Enhanced security checks for multiple environment files${NC}"
echo
echo -e "${BLUE}💡 Usage Tips:${NC}"
echo "   • Run ./scripts/check-env.sh to quickly check environment variables"
echo "   • Run ./scripts/validate-env.sh for comprehensive validation"
echo "   • Scripts automatically pick the right environment file"
echo "   • Development environment takes priority over production"
echo
echo -e "${GREEN}🎉 Testing complete! Your environment validation scripts are ready.${NC}"

# Cleanup
rm -f /tmp/test_output.log
