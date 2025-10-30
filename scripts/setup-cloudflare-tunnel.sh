#!/bin/bash
# Setup Cloudflare Named Tunnel - Permanent URL
# Run this once to get a permanent tunnel URL

set -e

echo "🚀 Setting up Cloudflare Named Tunnel (Permanent URL)"
echo "======================================================"

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not installed"
    echo "📦 Installing cloudflared..."
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
fi

echo ""
echo "📋 Step 1: Login to Cloudflare"
echo "=============================="
echo "This will open a browser window to authenticate."
echo "Press Enter to continue..."
read

cloudflared tunnel login

echo ""
echo "✅ Logged in successfully!"
echo ""
echo "📋 Step 2: Create a named tunnel"
echo "================================"
echo "Choose a name for your tunnel (e.g., analyticbot-api)"
echo -n "Tunnel name: "
read TUNNEL_NAME

cloudflared tunnel create $TUNNEL_NAME

echo ""
echo "✅ Tunnel created: $TUNNEL_NAME"
echo ""
echo "📋 Step 3: Get Tunnel ID"
echo "======================="

TUNNEL_ID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')
echo "Tunnel ID: $TUNNEL_ID"

echo ""
echo "📋 Step 4: Configure DNS"
echo "======================="
echo "Enter your domain name (e.g., yourdomain.com)"
echo "If you don't have one, you can use a free subdomain from:"
echo "  - afraid.org (free DNS)"
echo "  - freedns.afraid.org"
echo ""
echo -n "Domain/subdomain: "
read DOMAIN

# Create config file
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: $DOMAIN
    service: http://localhost:11400
  - service: http_status:404
EOF

echo ""
echo "📋 Step 5: Route DNS"
echo "==================="
cloudflared tunnel route dns $TUNNEL_NAME $DOMAIN

echo ""
echo "✅ Setup Complete!"
echo ""
echo "🌐 Your permanent URL: https://$DOMAIN"
echo ""
echo "📝 To start the tunnel:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "📝 To run in background:"
echo "   cloudflared tunnel run $TUNNEL_NAME &"
echo ""
echo "📝 Update your frontend .env.local:"
echo "   VITE_API_BASE_URL=https://$DOMAIN"
echo ""
echo "💡 This URL will NEVER change!"

# Save tunnel info for later use
cat > .tunnel-info << EOF
TUNNEL_NAME=$TUNNEL_NAME
TUNNEL_ID=$TUNNEL_ID
TUNNEL_URL=https://$DOMAIN
EOF

echo ""
echo "✅ Tunnel info saved to .tunnel-info"
