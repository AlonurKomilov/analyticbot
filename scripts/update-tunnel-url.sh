#!/bin/bash

# Script to automatically update frontend .env.local with current Cloudflare tunnel URL
# This fixes the issue where Cloudflare free tunnels get new URLs on each restart

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/apps/frontend/.env.local"
TUNNEL_LOG="$PROJECT_ROOT/logs/dev_tunnel.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Checking for Cloudflare tunnel URL...${NC}"

# Wait up to 30 seconds for tunnel to start and URL to appear in logs
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if [ -f "$TUNNEL_LOG" ]; then
        # Extract the latest Cloudflare URL from logs
        TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | tail -1)
        
        if [ ! -z "$TUNNEL_URL" ]; then
            echo -e "${GREEN}✅ Found Cloudflare tunnel URL: ${TUNNEL_URL}${NC}"
            
            # Check if .env.local exists
            if [ ! -f "$ENV_FILE" ]; then
                echo -e "${RED}❌ Error: .env.local not found at $ENV_FILE${NC}"
                exit 1
            fi
            
            # Backup the original file
            cp "$ENV_FILE" "$ENV_FILE.backup"
            
            # Update VITE_API_BASE_URL with the new tunnel URL
            # Use sed to replace the line, preserving other config
            sed -i "s|^VITE_API_BASE_URL=.*|VITE_API_BASE_URL=$TUNNEL_URL|" "$ENV_FILE"
            sed -i "s|^VITE_API_URL=.*|VITE_API_URL=$TUNNEL_URL|" "$ENV_FILE"
            
            echo -e "${GREEN}✅ Updated $ENV_FILE with new tunnel URL${NC}"
            echo -e "${YELLOW}📝 Frontend will use: $TUNNEL_URL${NC}"
            echo -e "${BLUE}💡 Restart frontend or hard-refresh browser to apply changes${NC}"
            
            # Also update a tracking file for reference
            echo "TUNNEL_URL=$TUNNEL_URL" > "$PROJECT_ROOT/.tunnel-current"
            echo "UPDATED_AT=$(date -Iseconds)" >> "$PROJECT_ROOT/.tunnel-current"
            
            # Write explicit success marker for make/logs visibility
            mkdir -p "$PROJECT_ROOT/logs"
            echo "[$(date -Iseconds)] ✅ FRONTEND ENV UPDATED: $TUNNEL_URL" >> "$PROJECT_ROOT/logs/tunnel-update.log"
            
            # Print big visible confirmation banner
            echo ""
            echo "=========================================="
            echo "✅ TUNNEL URL AUTO-UPDATE COMPLETE"
            echo "=========================================="
            echo "📡 New URL: $TUNNEL_URL"
            echo "📝 Updated: apps/frontend/.env.local"
            echo "⏰ Time: $(date)"
            echo "=========================================="
            echo ""
            
            exit 0
        fi
    fi
    
    attempt=$((attempt + 1))
    echo -e "${YELLOW}⏳ Waiting for tunnel URL... ($attempt/$max_attempts)${NC}"
    sleep 1
done

echo -e "${RED}❌ Timeout: Could not find Cloudflare tunnel URL in logs${NC}"
echo -e "${YELLOW}💡 Make sure the tunnel is running: make -f Makefile.dev dev-start${NC}"
exit 1
