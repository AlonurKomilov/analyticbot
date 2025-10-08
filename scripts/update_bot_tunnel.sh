#!/bin/bash

# 🤖 Update Bot TWA Configuration Script
# Usage: ./update_bot_tunnel.sh https://your-tunnel-url.com

if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <HTTPS_URL>"
    echo "   Example: $0 https://abc123-3000.euw.devtunnels.ms"
    exit 1
fi

HTTPS_URL="$1"

# Validate URL format
if [[ ! "$HTTPS_URL" =~ ^https:// ]]; then
    echo "❌ Error: URL must start with https://"
    echo "   Telegram Web Apps require HTTPS URLs"
    exit 1
fi

echo "🔧 Updating AnalyticBot TWA Configuration"
echo "========================================"
echo "New HTTPS URL: $HTTPS_URL"
echo ""

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backed up current .env file"

# Update .env file
if grep -q "TWA_HOST_URL=" .env; then
    # Update existing TWA_HOST_URL
    sed -i "s|TWA_HOST_URL=.*|TWA_HOST_URL=$HTTPS_URL|" .env
    echo "✅ Updated existing TWA_HOST_URL in .env"
else
    # Add TWA_HOST_URL
    echo "" >> .env
    echo "# Telegram Web App (TWA) Configuration" >> .env
    echo "TWA_HOST_URL=$HTTPS_URL" >> .env
    echo "✅ Added TWA_HOST_URL to .env"
fi

# Update bot code to use HTTPS validation (revert development HTTP allowance)
if grep -q "settings.ENVIRONMENT == 'development'" apps/bot/handlers/user_handlers.py; then
    echo "🔄 Reverting bot code to require HTTPS (removing development HTTP allowance)"

    # Create backup
    cp apps/bot/handlers/user_handlers.py apps/bot/handlers/user_handlers.py.backup.$(date +%Y%m%d_%H%M%S)

    # Revert to original HTTPS-only validation
    cat > /tmp/https_only_validation.py << 'EOF'
def _is_public_https(url: str) -> bool:
    return (
        url.startswith("https://")
        and (not url.startswith("https://localhost"))
        and (not url.startswith("https://127."))
        and (not url.startswith("https://0.0.0.0"))
    )
EOF

    # Replace the function in the file
    python3 << 'EOF'
import re

with open('apps/bot/handlers/user_handlers.py', 'r') as f:
    content = f.read()

# Replace the _is_public_https function
new_function = '''def _is_public_https(url: str) -> bool:
    return (
        url.startswith("https://")
        and (not url.startswith("https://localhost"))
        and (not url.startswith("https://127."))
        and (not url.startswith("https://0.0.0.0"))
    )'''

# Find and replace the function
pattern = r'def _is_public_https\(url: str\) -> bool:.*?(?=\n\ndef|\n\n\w|\Z)'
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

with open('apps/bot/handlers/user_handlers.py', 'w') as f:
    f.write(content)
EOF

    echo "✅ Reverted bot code to HTTPS-only validation"
fi

echo ""
echo "🔄 Restarting bot service..."
sudo docker-compose restart bot

echo ""
echo "⏳ Waiting for bot to start..."
sleep 5

echo ""
echo "🧪 Testing bot configuration..."
if sudo docker logs analyticbot-bot --tail 5 | grep -q "Starting AnalyticBot"; then
    echo "✅ Bot restarted successfully"
else
    echo "⚠️  Bot may still be starting - check logs with: sudo docker logs analyticbot-bot"
fi

echo ""
echo "🎯 TWA Configuration Complete!"
echo "================================"
echo "✅ HTTPS URL configured: $HTTPS_URL"
echo "✅ Bot service restarted"
echo "✅ Ready for TWA testing"
echo ""
echo "📱 Next Steps:"
echo "1. Open your Telegram bot"
echo "2. Send /dashboard command"
echo "3. Click the Dashboard button"
echo "4. TWA should open with your frontend!"
echo ""
echo "🔍 Troubleshooting:"
echo "- Check bot logs: sudo docker logs analyticbot-bot"
echo "- Test URL in browser: $HTTPS_URL"
echo "- Verify tunnel is running and accessible"
