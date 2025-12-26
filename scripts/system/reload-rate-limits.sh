#!/bin/bash
# Reload Rate Limit Configurations
# 
# This script reloads rate limit configs from Redis without full restart.
# For production use, consider using the API endpoint instead.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔄 Reloading Rate Limit Configurations..."
echo "========================================"

# Check if API is running
if ! pgrep -f "uvicorn.*apps.api.main:app" > /dev/null; then
    echo "❌ API is not running!"
    echo "💡 Start the API first: make -f Makefile.dev dev-start"
    exit 1
fi

# Get admin token (you should replace this with actual admin token)
if [ -z "$ADMIN_TOKEN" ]; then
    echo "⚠️  ADMIN_TOKEN not set. Please set it:"
    echo "   export ADMIN_TOKEN='your_admin_jwt_token'"
    echo ""
    echo "   You can get a token by logging in as admin:"
    echo "   curl -X POST http://localhost:11400/auth/login \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"email\":\"admin@analyticbot.org\",\"password\":\"your_password\"}' | jq -r '.access_token'"
    exit 1
fi

# Call the reload endpoint
echo "📡 Calling reload endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:11400/admin/rate-limits/reload \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json")

# Parse response
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
UPDATED=$(echo "$RESPONSE" | jq -r '.updated_count')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
RESTART_NEEDED=$(echo "$RESPONSE" | jq -r '.requires_restart')

if [ "$SUCCESS" = "true" ]; then
    echo "✅ $MESSAGE"
    echo ""
    echo "📊 Updated configs: $UPDATED"
    
    if [ "$RESTART_NEEDED" = "true" ]; then
        echo ""
        echo "⚠️  API RESTART RECOMMENDED"
        echo "   For full effect, restart the API:"
        echo "   make -f Makefile.dev dev-stop && make -f Makefile.dev dev-start"
        echo ""
        read -p "Do you want to restart now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔄 Restarting API..."
            cd "$PROJECT_ROOT"
            make -f Makefile.dev dev-stop
            sleep 2
            make -f Makefile.dev dev-start
            echo "✅ API restarted successfully!"
        fi
    fi
else
    echo "❌ Failed to reload configs"
    echo "   $MESSAGE"
    exit 1
fi
