#!/bin/bash

# Install and Configure Microsoft DevTunnel CLI

echo "🚀 Installing Microsoft DevTunnel CLI..."
echo "========================================"
echo ""

# Download and install
curl -sL https://aka.ms/DevTunnelCliInstall | bash

echo ""
echo "✅ DevTunnel CLI installed!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Login to DevTunnel:"
echo "   devtunnel user login"
echo ""
echo "2. List your existing tunnels:"
echo "   devtunnel list"
echo ""
echo "3. Update tunnel access to anonymous:"
echo "   devtunnel update b2qz1m0n --allow-anonymous"
echo ""
echo "4. Host the tunnels:"
echo "   # Terminal 1:"
echo "   devtunnel host b2qz1m0n -p 11400"
echo ""
echo "   # Terminal 2:"
echo "   devtunnel host <frontend-tunnel-id> -p 11300"
echo ""
echo "Or create new anonymous tunnels:"
echo "   devtunnel create analyticbot-api -p 11400 --allow-anonymous"
echo "   devtunnel create analyticbot-frontend -p 11300 --allow-anonymous"
echo ""
