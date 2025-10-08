#!/bin/bash
# SSL Certificate Setup for AnalyticBot Production
# Supports both self-signed (development) and Let's Encrypt (production) certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create SSL directory
mkdir -p docker/nginx/ssl
mkdir -p docker/nginx/ssl-challenges
mkdir -p logs/nginx

echo -e "${BLUE}🔒 SSL Certificate Setup for AnalyticBot${NC}"
echo "=========================================="

# Parse command line arguments
CERT_TYPE=${1:-self-signed}
DOMAIN=${2:-localhost}

case $CERT_TYPE in
    "self-signed")
        echo -e "${YELLOW}📋 Generating self-signed certificate for development...${NC}"

        # Generate private key
        openssl genrsa -out docker/nginx/ssl/key.pem 2048

        # Create certificate signing request config
        cat > docker/nginx/ssl/csr.conf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn

[dn]
C=US
ST=Development
L=Development
O=AnalyticBot
OU=Development
CN=${DOMAIN}
emailAddress=dev@analyticbot.local
EOF

        # Generate certificate
        openssl req -new -x509 -key docker/nginx/ssl/key.pem -out docker/nginx/ssl/cert.pem -days 365 -config docker/nginx/ssl/csr.conf

        echo -e "${GREEN}✅ Self-signed certificate generated for ${DOMAIN}${NC}"
        echo -e "${YELLOW}⚠️  Note: Browser will show security warning for self-signed certificates${NC}"
        ;;

    "letsencrypt")
        if [ "$DOMAIN" = "localhost" ]; then
            echo -e "${RED}❌ Let's Encrypt requires a real domain name${NC}"
            echo -e "${BLUE}💡 Usage: $0 letsencrypt your-domain.com${NC}"
            exit 1
        fi

        echo -e "${YELLOW}📋 Setting up Let's Encrypt certificate for ${DOMAIN}...${NC}"

        # Create temporary self-signed certificate for initial setup
        openssl genrsa -out docker/nginx/ssl/key.pem 2048
        openssl req -new -x509 -key docker/nginx/ssl/key.pem -out docker/nginx/ssl/cert.pem -days 1 -subj "/CN=${DOMAIN}"

        echo -e "${BLUE}🚀 Starting nginx with temporary certificate...${NC}"
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml up -d nginx-proxy

        sleep 5

        echo -e "${BLUE}🔐 Requesting Let's Encrypt certificate...${NC}"
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml run --rm certbot \
            certbot certonly --webroot --webroot-path=/var/www/certbot \
            --email admin@${DOMAIN} --agree-tos --no-eff-email \
            -d ${DOMAIN}

        # Copy Let's Encrypt certificates to nginx directory
        docker run --rm -v $(pwd)/docker/nginx/ssl:/etc/letsencrypt certbot/certbot \
            sh -c "cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /etc/letsencrypt/cert.pem && \
                   cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /etc/letsencrypt/key.pem"

        echo -e "${GREEN}✅ Let's Encrypt certificate obtained for ${DOMAIN}${NC}"
        echo -e "${BLUE}🔄 Restarting nginx with real certificate...${NC}"
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml -f docker/docker-compose.proxy.yml restart nginx-proxy
        ;;

    *)
        echo -e "${RED}❌ Invalid certificate type: ${CERT_TYPE}${NC}"
        echo -e "${BLUE}Usage: $0 [self-signed|letsencrypt] [domain]${NC}"
        echo ""
        echo "Examples:"
        echo "  $0 self-signed localhost          # For development"
        echo "  $0 letsencrypt analyticbot.com    # For production"
        exit 1
        ;;
esac

# Set appropriate permissions
chmod 600 docker/nginx/ssl/key.pem
chmod 644 docker/nginx/ssl/cert.pem

echo ""
echo -e "${GREEN}🎉 SSL setup complete!${NC}"
echo "===================="
echo -e "${BLUE}📋 Next steps:${NC}"
echo "  1. Start the application with proxy:"
echo "     make prod-proxy"
echo "  2. Test HTTPS access:"
echo "     curl -k https://${DOMAIN}/health"
echo "  3. View certificate details:"
echo "     openssl x509 -in docker/nginx/ssl/cert.pem -text -noout"

if [ "$CERT_TYPE" = "letsencrypt" ]; then
    echo ""
    echo -e "${BLUE}🔄 Auto-renewal setup:${NC}"
    echo "  Let's Encrypt certificates will auto-renew every 12 hours"
    echo "  Check renewal status with: docker logs analyticbot-certbot"
fi
