#!/bin/bash
# Domain Setup Script for analyticbot.org
# This script helps you configure your custom domain with CloudFlare Tunnel

set -e

DOMAIN="analyticbot.org"
SERVER_IP="185.211.5.244"
FRONTEND_PORT="11300"
API_PORT="11400"

echo "🌐 Setting up domain: ${DOMAIN}"
echo "========================================="
echo ""

echo "📋 STEP 1: CloudFlare DNS Configuration"
echo "----------------------------------------"
echo "Go to CloudFlare Dashboard → DNS Records"
echo "Add these DNS records:"
echo ""
echo "  Type: A"
echo "  Name: @  (or analyticbot.org)"
echo "  IPv4: ${SERVER_IP}"
echo "  Proxy: ✅ Proxied (orange cloud)"
echo ""
echo "  Type: A"
echo "  Name: www"
echo "  IPv4: ${SERVER_IP}"
echo "  Proxy: ✅ Proxied (orange cloud)"
echo ""
echo "  Type: CNAME"
echo "  Name: api"
echo "  Target: ${DOMAIN}"
echo "  Proxy: ✅ Proxied"
echo ""

read -p "✅ Have you added DNS records? (yes/no): " dns_done

if [ "$dns_done" != "yes" ]; then
    echo "Please add DNS records first, then run this script again."
    exit 1
fi

echo ""
echo "📋 STEP 2: CloudFlare Tunnel Setup (RECOMMENDED)"
echo "------------------------------------------------"
echo "This creates a secure tunnel without opening ports"
echo ""
echo "Option A: Use CloudFlare Tunnel (Free, Secure, No Port Forwarding)"
echo "  1. Install cloudflared (already installed ✅)"
echo "  2. Login to CloudFlare"
echo "  3. Create named tunnel for ${DOMAIN}"
echo ""

read -p "Do you want to set up CloudFlare Tunnel? (yes/no): " setup_tunnel

if [ "$setup_tunnel" == "yes" ]; then
    echo ""
    echo "🔐 Logging into CloudFlare..."
    echo "This will open a browser. Please authorize the connection."
    
    cloudflared tunnel login
    
    echo ""
    echo "✅ CloudFlare login successful!"
    echo ""
    
    TUNNEL_NAME="analyticbot-prod"
    
    echo "📝 Creating tunnel: ${TUNNEL_NAME}"
    cloudflared tunnel create ${TUNNEL_NAME}
    
    # Get tunnel ID
    TUNNEL_ID=$(cloudflared tunnel list | grep ${TUNNEL_NAME} | awk '{print $1}')
    
    if [ -z "$TUNNEL_ID" ]; then
        echo "❌ Failed to get tunnel ID"
        exit 1
    fi
    
    echo "✅ Tunnel created with ID: ${TUNNEL_ID}"
    echo ""
    
    # Create tunnel config
    mkdir -p ~/.cloudflared
    cat > ~/.cloudflared/config.yml << EOF
tunnel: ${TUNNEL_ID}
credentials-file: /home/${USER}/.cloudflared/${TUNNEL_ID}.json

ingress:
  # Route all traffic to frontend (which proxies API internally)
  - hostname: ${DOMAIN}
    service: http://localhost:${FRONTEND_PORT}
  - hostname: www.${DOMAIN}
    service: http://localhost:${FRONTEND_PORT}
  # Catch-all rule (required)
  - service: http_status:404
EOF
    
    echo "✅ Tunnel configuration created!"
    echo ""
    
    # Route DNS to tunnel
    echo "📝 Configuring DNS to use tunnel..."
    cloudflared tunnel route dns ${TUNNEL_NAME} ${DOMAIN}
    cloudflared tunnel route dns ${TUNNEL_NAME} www.${DOMAIN}
    
    echo "✅ DNS routing configured!"
    echo ""
    
    # Save tunnel info
    cat > .tunnel-info << EOF
TUNNEL_NAME=${TUNNEL_NAME}
TUNNEL_ID=${TUNNEL_ID}
TUNNEL_URL=https://${DOMAIN}
DOMAIN=${DOMAIN}
EOF
    
    echo "✅ Tunnel info saved to .tunnel-info"
    echo ""
    
    echo "🚀 Starting tunnel..."
    cloudflared tunnel run ${TUNNEL_NAME} &
    TUNNEL_PID=$!
    
    echo "✅ Tunnel started with PID: ${TUNNEL_PID}"
    echo ""
    
    # Install as systemd service
    read -p "Do you want to install tunnel as system service (auto-start on boot)? (yes/no): " install_service
    
    if [ "$install_service" == "yes" ]; then
        sudo cloudflared service install
        sudo systemctl enable cloudflared
        sudo systemctl start cloudflared
        echo "✅ Tunnel installed as system service!"
        echo "   - Auto-starts on boot"
        echo "   - Managed by systemd"
        echo ""
        echo "   Commands:"
        echo "   sudo systemctl status cloudflared  - Check status"
        echo "   sudo systemctl restart cloudflared - Restart"
        echo "   sudo systemctl stop cloudflared    - Stop"
    fi
    
else
    echo ""
    echo "📋 Manual Setup Without Tunnel"
    echo "-------------------------------"
    echo "If not using CloudFlare Tunnel, you need to:"
    echo "1. Open ports on your firewall:"
    echo "   - Port 80 (HTTP)"
    echo "   - Port 443 (HTTPS)"
    echo "2. Install Caddy or Nginx for reverse proxy"
    echo "3. Configure SSL certificates"
    echo ""
    echo "We recommend using CloudFlare Tunnel instead (more secure, no port opening needed)"
fi

echo ""
echo "========================================="
echo "🎉 DOMAIN SETUP COMPLETE!"
echo "========================================="
echo ""
echo "Your domain: https://${DOMAIN}"
echo ""
echo "📝 Next steps:"
echo "1. Update frontend .env.local:"
echo "   VITE_API_BASE_URL="  # Use relative URLs for same-domain"
echo ""
echo "2. Restart services:"
echo "   make -f Makefile.dev dev-stop"
echo "   make -f Makefile.dev dev-start"
echo ""
echo "3. Test your domain:"
echo "   https://${DOMAIN}"
echo ""
echo "4. Access points:"
echo "   Frontend: https://${DOMAIN}"
echo "   API: https://${DOMAIN}/api/*  (proxied through frontend)"
echo ""
echo "========================================="
