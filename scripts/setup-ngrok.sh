#!/bin/bash
# Setup ngrok with permanent URL
# Requires ngrok account (free tier available)

set -e

echo "🚀 Setting up ngrok (Permanent URL)"
echo "===================================="

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 Installing ngrok..."
    
    # Download ngrok
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    
    echo "✅ ngrok installed"
fi

echo ""
echo "📋 Step 1: Get your ngrok authtoken"
echo "==================================="
echo "1. Go to: https://dashboard.ngrok.com/signup"
echo "2. Sign up for free account"
echo "3. Copy your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
echo -n "Enter your ngrok authtoken: "
read AUTHTOKEN

ngrok config add-authtoken $AUTHTOKEN

echo ""
echo "✅ Authtoken configured!"
echo ""
echo "📋 Step 2: Choose subdomain (requires paid plan)"
echo "================================================"
echo "Free tier: Random URL (e.g., https://abc-123.ngrok-free.app)"
echo "Paid tier: Custom subdomain (e.g., https://yourname.ngrok-free.app)"
echo ""
echo "Do you have a paid ngrok account? (y/n): "
read HAS_PAID

if [ "$HAS_PAID" = "y" ]; then
    echo -n "Enter your desired subdomain: "
    read SUBDOMAIN
    NGROK_CMD="ngrok http --domain=${SUBDOMAIN}.ngrok-free.app 11400"
    TUNNEL_URL="https://${SUBDOMAIN}.ngrok-free.app"
else
    echo "⚠️  Free tier will generate random URLs each time"
    echo "💡 Consider upgrading to ngrok paid ($8/month) for permanent URL"
    NGROK_CMD="ngrok http 11400"
    TUNNEL_URL="Random URL (check terminal)"
fi

# Save config
cat > .ngrok-config << EOF
NGROK_CMD=$NGROK_CMD
TUNNEL_URL=$TUNNEL_URL
EOF

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 To start ngrok tunnel:"
echo "   $NGROK_CMD"
echo ""
echo "📝 Or use the dev-start script:"
echo "   make -f Makefile.dev dev-tunnel-ngrok"
echo ""
echo "🌐 Your URL: $TUNNEL_URL"

if [ "$HAS_PAID" != "y" ]; then
    echo ""
    echo "⚠️  Note: Free tier URL changes every restart"
    echo "💡 Upgrade to paid for permanent URL: https://ngrok.com/pricing"
fi
