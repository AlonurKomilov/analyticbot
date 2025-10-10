#!/bin/bash

# DevTunnel Setup Helper Script
# This script helps you configure your frontend to use new devtunnel URLs

echo "🔧 DevTunnel Configuration Helper"
echo "=================================="
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Open VS Code Ports Panel:"
echo "   - Press Ctrl+\` (backtick) to open terminal"
echo "   - Click 'PORTS' tab"
echo ""
echo "2. Forward these ports as PUBLIC:"
echo "   - Port 11300 (Frontend)"
echo "   - Port 11400 (API)"
echo ""
echo "3. Copy the HTTPS URLs VS Code generates"
echo ""
echo "4. Enter them below:"
echo ""

read -p "Enter API DevTunnel URL (e.g., https://xxx-11400.app.github.dev): " API_URL
read -p "Enter Frontend DevTunnel URL (e.g., https://xxx-11300.app.github.dev): " FRONTEND_URL

if [[ -z "$API_URL" ]] || [[ -z "$FRONTEND_URL" ]]; then
    echo ""
    echo "❌ URLs cannot be empty. Please try again."
    exit 1
fi

echo ""
echo "📝 Updating configuration files..."

# Update frontend .env.local
cat > apps/frontend/.env.local << EOF
# Frontend Environment Variables - Development
# This file is loaded by Vite in development mode

# API Configuration
# Using DevTunnel for secure remote access
VITE_API_URL=${API_URL}
VITE_API_BASE_URL=${API_URL}

# Telegram Web App Configuration
VITE_TWA_BOT_USERNAME=@abccontrol_bot
VITE_TWA_START_PARAM=analytics

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=true
VITE_DEFAULT_THEME=light

# Mode
VITE_NODE_ENV=development
EOF

echo "✅ Updated apps/frontend/.env.local"

# Update .env.development CORS
echo ""
echo "⚠️  IMPORTANT: You need to manually add these URLs to CORS_ORIGINS in .env.development:"
echo ""
echo "Add to CORS_ORIGINS array:"
echo "  \"${API_URL}\","
echo "  \"${FRONTEND_URL}\""
echo ""
echo "📝 Then restart services:"
echo "  make dev-stop"
echo "  make dev-start"
echo ""
echo "🎉 Access your app at: ${FRONTEND_URL}"
