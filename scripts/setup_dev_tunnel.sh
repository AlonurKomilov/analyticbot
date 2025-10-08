#!/bin/bash

# 🚀 AnalyticBot Dev Tunnel Setup Script
# This script helps set up HTTPS tunnel for TWA integration

echo "🔍 AnalyticBot Dev Tunnel Setup"
echo "================================="

# Check if frontend is running
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is running on port 3000"
else
    echo "❌ Frontend is not accessible on port 3000"
    echo "   Please check: sudo docker-compose ps"
    exit 1
fi

echo ""
echo "🔧 Available Tunnel Options:"
echo ""

# Option 1: VS Code Port Forwarding
echo "1. VS Code Port Forwarding (Recommended)"
echo "   - Open VS Code Command Palette (Ctrl+Shift+P)"
echo "   - Search: 'Remote-Tunnels: Forward Port'"
echo "   - Enter port: 3000"
echo "   - Set visibility: Public"
echo "   - Copy the HTTPS URL from Ports panel"
echo ""

# Option 2: Microsoft devtunnel
echo "2. Microsoft devtunnel"
echo "   Run: devtunnel user login"
echo "   Then: devtunnel create analyticbot-frontend --allow-anonymous"
echo "   Then: devtunnel host -p 3000 analyticbot-frontend"
echo ""

# Option 3: ngrok
echo "3. ngrok (requires account)"
echo "   Sign up: https://dashboard.ngrok.com/signup"
echo "   Get token: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "   Run: ngrok config add-authtoken YOUR_TOKEN"
echo "   Run: ngrok http 3000"
echo ""

# Option 4: Cloudflare (temporary)
echo "4. Cloudflare Tunnel (temporary, for quick testing)"
echo "   Run: cloudflared tunnel --url http://localhost:3000"
echo "   (Note: Cloudflare tunnels are temporary and may disconnect)"
echo ""

echo "🎯 After getting HTTPS URL:"
echo "1. Copy the HTTPS URL (e.g., https://abc123-3000.euw.devtunnels.ms)"
echo "2. Run: ./update_bot_tunnel.sh YOUR_HTTPS_URL"
echo "3. Test TWA integration in Telegram"
echo ""

# Test current frontend
echo "🧪 Testing frontend accessibility..."
if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Frontend responds to HTTP requests"
else
    echo "❌ Frontend not responding to HTTP requests"
fi

echo ""
echo "📝 Current frontend URL: http://173.212.236.167:3000"
echo "📝 Need HTTPS URL for TWA: https://your-tunnel-url.com"
echo ""
echo "Choose an option above and follow the instructions!"
