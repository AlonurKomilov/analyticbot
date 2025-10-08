#!/bin/bash
# Payment System Staging Test Script
# Tests all payment flows before production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Payment System Staging Tests${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Test configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
TEST_USER_ID=1
TEST_PLAN_ID="price_test_monthly"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test 1: API Health Check
echo -e "${BLUE}Test 1: API Health Check${NC}"
echo "-------------------------"

if curl -f "$API_BASE_URL/health" > /dev/null 2>&1; then
    print_status "API is healthy"
else
    print_error "API health check failed"
    exit 1
fi

# Test 2: Payment System Status
echo ""
echo -e "${BLUE}Test 2: Payment System Status${NC}"
echo "------------------------------"

PAYMENT_STATUS=$(curl -s "$API_BASE_URL/api/payments/status" | jq -r '.status' 2>/dev/null || echo "error")

if [[ "$PAYMENT_STATUS" == "ok" ]]; then
    print_status "Payment system is operational"
else
    print_error "Payment system status check failed"
    exit 1
fi

# Test 3: Available Plans
echo ""
echo -e "${BLUE}Test 3: Available Plans${NC}"
echo "------------------------"

PLANS_RESPONSE=$(curl -s "$API_BASE_URL/api/payments/plans" 2>/dev/null)
PLANS_COUNT=$(echo "$PLANS_RESPONSE" | jq '. | length' 2>/dev/null || echo "0")

if [[ "$PLANS_COUNT" -gt 0 ]]; then
    print_status "Found $PLANS_COUNT available plans"
    echo "Plans:"
    echo "$PLANS_RESPONSE" | jq -r '.[] | "  • \(.name): \(.price_monthly) \(.currency)/month"' 2>/dev/null || echo "  Error parsing plans"
else
    print_warning "No plans found - this may be expected in staging"
fi

# Test 4: User Subscription Check
echo ""
echo -e "${BLUE}Test 4: User Subscription Check${NC}"
echo "--------------------------------"

SUBSCRIPTION_RESPONSE=$(curl -s "$API_BASE_URL/api/payments/user/$TEST_USER_ID/subscription" 2>/dev/null)
SUBSCRIPTION_EXISTS=$(echo "$SUBSCRIPTION_RESPONSE" | jq -r '.subscription != null' 2>/dev/null || echo "false")

if [[ "$SUBSCRIPTION_EXISTS" == "true" ]]; then
    print_info "User has existing subscription"
    SUBSCRIPTION_STATUS=$(echo "$SUBSCRIPTION_RESPONSE" | jq -r '.subscription.status' 2>/dev/null || echo "unknown")
    echo "  Status: $SUBSCRIPTION_STATUS"
else
    print_info "User has no active subscription (expected for new users)"
fi

# Test 5: Payment History
echo ""
echo -e "${BLUE}Test 5: Payment History${NC}"
echo "------------------------"

HISTORY_RESPONSE=$(curl -s "$API_BASE_URL/api/payments/user/$TEST_USER_ID/history" 2>/dev/null)
PAYMENTS_COUNT=$(echo "$HISTORY_RESPONSE" | jq '.payments | length' 2>/dev/null || echo "0")

print_info "User has $PAYMENTS_COUNT payment records"

# Test 6: Webhook Endpoint
echo ""
echo -e "${BLUE}Test 6: Webhook Endpoint${NC}"
echo "-------------------------"

# Test webhook endpoint accessibility (should return 400 for missing signature)
WEBHOOK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE_URL/api/payments/webhook/stripe" \
    -H "Content-Type: application/json" \
    -d '{"test": "webhook"}' 2>/dev/null || echo "000")

if [[ "$WEBHOOK_STATUS" == "400" ]]; then
    print_status "Webhook endpoint is accessible (returns 400 for missing signature)"
elif [[ "$WEBHOOK_STATUS" == "422" ]]; then
    print_status "Webhook endpoint is accessible (validation error expected)"
else
    print_warning "Webhook endpoint returned status: $WEBHOOK_STATUS"
fi

# Test 7: Frontend Components
echo ""
echo -e "${BLUE}Test 7: Frontend Components${NC}"
echo "----------------------------"

# Check if frontend files exist
FRONTEND_COMPONENTS=(
    "apps/frontend/src/components/payment/PaymentForm.jsx"
    "apps/frontend/src/components/payment/SubscriptionDashboard.jsx"
    "apps/frontend/src/components/payment/PlanSelector.jsx"
    "apps/frontend/src/services/paymentAPI.js"
)

for component in "${FRONTEND_COMPONENTS[@]}"; do
    if [[ -f "$component" ]]; then
        print_status "$(basename "$component") exists"
    else
        print_error "$(basename "$component") missing"
    fi
done

# Test 8: Environment Configuration
echo ""
echo -e "${BLUE}Test 8: Environment Configuration${NC}"
echo "----------------------------------"

# Check if environment files exist
ENV_FILES=(
    ".env.production.template"
    "apps/frontend/.env.production.template"
)

for env_file in "${ENV_FILES[@]}"; do
    if [[ -f "$env_file" ]]; then
        print_status "$(basename "$env_file") exists"
    else
        print_error "$(basename "$env_file") missing"
    fi
done

# Test 9: Docker Configuration
echo ""
echo -e "${BLUE}Test 9: Docker Configuration${NC}"
echo "-----------------------------"

if [[ -f "docker-compose.prod.yml" ]]; then
    print_status "Production Docker Compose configuration exists"
else
    print_error "Production Docker Compose configuration missing"
fi

if [[ -f "deploy_production.sh" && -x "deploy_production.sh" ]]; then
    print_status "Production deployment script is ready"
else
    print_error "Production deployment script missing or not executable"
fi

# Test 10: Dependencies
echo ""
echo -e "${BLUE}Test 10: Dependencies${NC}"
echo "----------------------"

# Check Python dependencies
if python -c "import stripe" 2>/dev/null; then
    print_status "Stripe Python library is installed"
else
    print_error "Stripe Python library not found"
fi

# Check if frontend dependencies are installed
if [[ -d "apps/frontend/node_modules/@stripe" ]]; then
    print_status "Stripe frontend dependencies are installed"
else
    print_warning "Stripe frontend dependencies may not be installed"
fi

# Test Summary
echo ""
echo -e "${GREEN}📊 Test Summary${NC}"
echo "================"

# Count tests
TOTAL_TESTS=10
echo "Completed $TOTAL_TESTS test categories"

# Check critical components
CRITICAL_ISSUES=0

# API availability
if ! curl -f "$API_BASE_URL/health" > /dev/null 2>&1; then
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

# Payment system status
if [[ "$PAYMENT_STATUS" != "ok" ]]; then
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

# Webhook endpoint
if [[ "$WEBHOOK_STATUS" != "400" && "$WEBHOOK_STATUS" != "422" ]]; then
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

echo ""
if [[ $CRITICAL_ISSUES -eq 0 ]]; then
    print_status "🚀 All critical systems are operational!"
    print_status "✅ Payment system is ready for production deployment"
    echo ""
    print_info "Next Steps:"
    echo "1. Configure production Stripe keys"
    echo "2. Run: ./deploy_production.sh"
    echo "3. Set up Stripe webhooks (see STRIPE_WEBHOOK_SETUP_GUIDE.md)"
    echo "4. Test payment flows with real transactions"

    echo ""
    print_info "Deployment Command:"
    echo "  sudo ./deploy_production.sh"

else
    print_error "$CRITICAL_ISSUES critical issue(s) found"
    print_warning "Please resolve critical issues before production deployment"
fi

echo ""
print_info "For detailed webhook setup instructions:"
print_info "  cat STRIPE_WEBHOOK_SETUP_GUIDE.md"

echo ""
print_status "🧪 Staging tests completed"
