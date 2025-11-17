#!/bin/bash
# ============================================================================
# Frontend Deployment Script
# ============================================================================
# Builds and deploys the React frontend to /var/www/analyticbot/frontend/
# Uses .env.production for API configuration (api.analyticbot.org)
# ============================================================================

set -e  # Exit on error

PROJECT_DIR="/home/abcdeveloper/projects/analyticbot"
FRONTEND_DIR="$PROJECT_DIR/apps/frontend"
DEPLOY_DIR="/var/www/analyticbot/frontend"

echo "🚀 AnalyticBot Frontend Deployment"
echo "===================================="
echo ""

# Step 1: Clean previous build
echo "🧹 Cleaning previous build..."
cd "$FRONTEND_DIR"
rm -rf dist/

# Step 2: Build with production environment
echo "📦 Building frontend (production mode)..."
echo "   Using .env.production (API: api.analyticbot.org)"
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully"
echo ""

# Step 3: Backup current deployment (if exists)
if [ -d "$DEPLOY_DIR" ]; then
    echo "💾 Backing up current deployment..."
    sudo mv "$DEPLOY_DIR" "${DEPLOY_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Step 4: Create deployment directory
echo "📁 Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"

# Step 5: Copy built files
echo "📋 Copying built files to deployment directory..."
sudo cp -r dist/* "$DEPLOY_DIR/"

# Step 6: Set correct permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data "$DEPLOY_DIR"
sudo chmod -R 755 "$DEPLOY_DIR"

# Step 7: Verify deployment
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📊 Deployment Summary:"
echo "   Source: $FRONTEND_DIR/dist/"
echo "   Target: $DEPLOY_DIR"
echo "   Files: $(sudo find $DEPLOY_DIR -type f | wc -l) files"
echo "   Size: $(sudo du -sh $DEPLOY_DIR | cut -f1)"
echo ""

# Step 8: Test nginx config and reload
echo "🔍 Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx config is valid"
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
else
    echo "❌ Nginx config test failed!"
    echo "⚠️  Deployment completed but nginx not reloaded"
    exit 1
fi

echo ""
echo "🎉 Frontend deployment complete!"
echo ""
echo "🌐 Access your application at:"
echo "   • https://www.analyticbot.org"
echo "   • https://analyticbot.org (redirects to www)"
echo ""
echo "💡 API requests will be sent to:"
echo "   • https://api.analyticbot.org"
echo ""
