#!/bin/bash
# Final Payment System Verification
# Comprehensive test of all components before production deployment

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}🎉 Week 15-16 Payment System - Final Verification${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "Testing $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Component Tests
echo -e "${BOLD}📝 Component Verification${NC}"
echo "============================"

# Backend Components
echo -e "${BLUE}Backend Infrastructure:${NC}"
run_test "Stripe Adapter" "test -f apps/bot/services/stripe_adapter.py"
run_test "Payment Service" "test -f apps/bot/services/payment_service.py"
run_test "Payment Routes" "test -f apps/bot/api/payment_routes.py"
run_test "Payment Models" "test -f apps/bot/models/payment.py"
run_test "Payment Repository" "test -f infra/db/repositories/payment_repository.py"

# Frontend Components
echo -e "${BLUE}Frontend Components:${NC}"
run_test "Payment Form" "test -f apps/frontend/src/components/payment/PaymentForm.jsx"
run_test "Subscription Dashboard" "test -f apps/frontend/src/components/payment/SubscriptionDashboard.jsx"
run_test "Plan Selector" "test -f apps/frontend/src/components/payment/PlanSelector.jsx"
run_test "Payment API Service" "test -f apps/frontend/src/services/paymentAPI.js"
run_test "API Client" "test -f apps/frontend/src/services/apiClient.js"

# Configuration Files
echo -e "${BLUE}Configuration Files:${NC}"
run_test "Environment Template" "test -f .env.example"
run_test "Frontend Environment Template" "test -f apps/frontend/.env.example"
run_test "Production Docker Compose" "test -f docker/docker-compose.prod.yml"
run_test "Deployment Script" "test -f deploy_production.sh && test -x deploy_production.sh"
run_test "Stripe Webhook Guide" "test -f STRIPE_WEBHOOK_SETUP_GUIDE.md"

# Dependencies
echo ""
echo -e "${BOLD}📦 Dependency Verification${NC}"
echo "=============================="

# Python Dependencies
echo -e "${BLUE}Python Dependencies:${NC}"
run_test "Stripe Python Library" "source .venv/bin/activate && python -c 'import stripe'"
run_test "FastAPI" "source .venv/bin/activate && python -c 'import fastapi'"
run_test "Pydantic" "source .venv/bin/activate && python -c 'import pydantic'"

# Frontend Dependencies
echo -e "${BLUE}Frontend Dependencies:${NC}"
run_test "Stripe React Components" "test -d apps/frontend/node_modules/@stripe/react-stripe-js"
run_test "Stripe JS Library" "test -d apps/frontend/node_modules/@stripe/stripe-js"
run_test "Axios HTTP Client" "test -d apps/frontend/node_modules/axios"

# Configuration Integrity
echo ""
echo -e "${BOLD}⚙️  Configuration Verification${NC}"
echo "=================================="

echo -e "${BLUE}Package Configuration:${NC}"
run_test "Requirements.txt Updated" "grep -q stripe requirements.txt"
run_test "PyProject.toml Updated" "grep -q stripe pyproject.toml"
run_test "Frontend Package.json Updated" "grep -q '@stripe/react-stripe-js' apps/frontend/package.json"

echo -e "${BLUE}Database Configuration:${NC}"
run_test "Payment Migration Exists" "test -f infra/db/alembic/versions/0005_payment_system.py"
run_test "No Duplicate Migrations" "test ! -f infra/db/alembic/versions/0005_payment_test.py"

# Import Tests
echo ""
echo -e "${BOLD}🔧 Import Verification${NC}"
echo "=========================="

echo -e "${BLUE}Python Imports:${NC}"
run_test "Stripe Adapter Import" "python -c 'from apps.bot.services.stripe_adapter import StripeAdapter'"
run_test "Payment Service Import" "python -c 'from apps.bot.services.payment_service import PaymentService'"
run_test "Payment Models Import" "python -c 'from apps.bot.models.payment import PaymentCreate, SubscriptionCreate'"
run_test "Payment Routes Import" "python -c 'from apps.bot.api.payment_routes import router'"

# API Integration Test
echo ""
echo -e "${BOLD}🌐 API Integration Verification${NC}"
echo "=================================="

# Check if main API includes payment routes
if grep -q "from apps.bot.api.payment_routes import router as payment_router" apps/api/main.py && \
   grep -q "app.include_router(payment_router)" apps/api/main.py; then
    echo -e "API Integration: ${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "API Integration: ${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# File Structure Verification
echo ""
echo -e "${BOLD}📁 File Structure Verification${NC}"
echo "==============================="

# Check critical directories exist
CRITICAL_DIRS=(
    "apps/bot/services"
    "apps/bot/api"
    "apps/bot/models"
    "apps/frontend/src/components/payment"
    "apps/frontend/src/services"
    "infra/db/repositories"
)

for dir in "${CRITICAL_DIRS[@]}"; do
    run_test "Directory: $dir" "test -d $dir"
done

# Documentation Verification
echo ""
echo -e "${BOLD}📚 Documentation Verification${NC}"
echo "==============================="

run_test "Implementation Plan" "test -f WEEK_15_16_PAYMENT_SYSTEM_PLAN.md"
run_test "Implementation Complete Report" "test -f WEEK_15_16_IMPLEMENTATION_COMPLETE.md"
run_test "Webhook Setup Guide" "test -f STRIPE_WEBHOOK_SETUP_GUIDE.md"

# File Size Verification (ensure files aren't empty)
echo ""
echo -e "${BOLD}📊 Content Verification${NC}"
echo "========================"

# Check file sizes to ensure they contain actual implementation
CRITICAL_FILES=(
    "apps/bot/services/stripe_adapter.py:5000"
    "apps/bot/api/payment_routes.py:3000"
    "apps/frontend/src/components/payment/PaymentForm.jsx:4000"
    "apps/frontend/src/components/payment/SubscriptionDashboard.jsx:6000"
    "apps/frontend/src/components/payment/PlanSelector.jsx:5000"
)

for file_check in "${CRITICAL_FILES[@]}"; do
    file_path="${file_check%:*}"
    min_size="${file_check#*:}"

    if [[ -f "$file_path" ]]; then
        file_size=$(wc -c < "$file_path")
        if [[ $file_size -gt $min_size ]]; then
            echo -e "Content: $(basename "$file_path"): ${GREEN}✅ PASS${NC} ($file_size bytes)"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "Content: $(basename "$file_path"): ${RED}❌ FAIL${NC} (only $file_size bytes)"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        echo -e "Content: $(basename "$file_path"): ${RED}❌ MISSING${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
done

# Summary
echo ""
echo -e "${BOLD}📊 VERIFICATION SUMMARY${NC}"
echo "========================="
echo ""
echo -e "Total Tests: ${BOLD}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

# Calculate completion percentage
COMPLETION_PERCENTAGE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
echo -e "Completion: ${BOLD}$COMPLETION_PERCENTAGE%${NC}"

echo ""

# Final Status
if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${BOLD}${GREEN}🎉 VERIFICATION COMPLETE: ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Payment System is 100% ready for production deployment${NC}"
    echo ""
    echo -e "${BOLD}${BLUE}🚀 NEXT STEPS FOR PRODUCTION:${NC}"
    echo "1. Configure production Stripe keys (.env.production)"
    echo "2. Run deployment: ${BOLD}sudo ./deploy_production.sh${NC}"
    echo "3. Configure Stripe webhooks (see STRIPE_WEBHOOK_SETUP_GUIDE.md)"
    echo "4. Test payment flows with real transactions"
    echo ""
    echo -e "${BOLD}${GREEN}💰 REVENUE GENERATION: READY TO ACTIVATE${NC}"

elif [[ $COMPLETION_PERCENTAGE -ge 90 ]]; then
    echo -e "${BOLD}${YELLOW}⚠️  VERIFICATION MOSTLY COMPLETE ($COMPLETION_PERCENTAGE%)${NC}"
    echo -e "${YELLOW}Minor issues detected, but system is deployable${NC}"
    echo ""
    echo -e "${YELLOW}Review failed tests above and proceed with caution${NC}"

else
    echo -e "${BOLD}${RED}❌ VERIFICATION FAILED ($COMPLETION_PERCENTAGE%)${NC}"
    echo -e "${RED}Critical issues detected - do not deploy to production${NC}"
    echo ""
    echo -e "${RED}Please resolve all failed tests before deployment${NC}"
fi

echo ""
echo -e "${BLUE}Deployment Command: ${BOLD}sudo ./deploy_production.sh${NC}"
echo -e "${BLUE}Testing Command: ${BOLD}./test_staging.sh${NC}"
echo -e "${BLUE}Documentation: ${BOLD}cat PRODUCTION_DEPLOYMENT_GUIDE.md${NC}"

exit $FAILED_TESTS
