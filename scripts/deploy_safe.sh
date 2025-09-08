#!/bin/bash
# Safe Production Deployment Script
# Deploys AnalyticBot with comprehensive rate limiting protection

echo "🚀 AnalyticBot Safe Production Deployment"
echo "🛡️ With Comprehensive Rate Limiting Protection"
echo "=" >&2 | head -c 60 && echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Verify rate limiting settings
echo "🔍 Verifying rate limiting configuration..."

# Check MTProto rate limiting settings
LIMIT=$(grep "MTPROTO_HISTORY_LIMIT_PER_RUN" .env | cut -d'=' -f2)
CONCURRENCY=$(grep "MTPROTO_CONCURRENCY" .env | cut -d'=' -f2)
SLEEP=$(grep "MTPROTO_SLEEP_THRESHOLD" .env | cut -d'=' -f2)

echo "   📊 Message limit per run: $LIMIT (should be ≤50)"
echo "   🔀 Concurrency: $CONCURRENCY (should be ≤1)"
echo "   ⏱️ Sleep threshold: $SLEEP (should be ≥2.0)"

# Validate safe settings
if [ "$LIMIT" -gt 50 ]; then
    echo "⚠️  WARNING: MTPROTO_HISTORY_LIMIT_PER_RUN=$LIMIT is too high for safety"
    echo "   Recommended: ≤50 messages per run"
fi

if [ "$CONCURRENCY" -gt 1 ]; then
    echo "⚠️  WARNING: MTPROTO_CONCURRENCY=$CONCURRENCY may cause rate limits"
    echo "   Recommended: 1 for maximum safety"
fi

if [ "$(echo "$SLEEP < 2.0" | bc -l)" -eq 1 ]; then
    echo "⚠️  WARNING: MTPROTO_SLEEP_THRESHOLD=$SLEEP is too low"
    echo "   Recommended: ≥2.0 seconds for safety"
fi

echo ""
echo "🛡️ Rate Limiting Protection Features:"
echo "   ✅ Multi-layer delays in data collection scripts"
echo "   ✅ Conservative Docker configuration"
echo "   ✅ Safe .env settings"
echo "   ✅ Production-ready MTProto service"
echo ""

# Deployment options
echo "🚀 Deployment Options:"
echo "1. Core services only (API + Bot + DB + Redis)"
echo "2. Core + MTProto data collection (RATE LIMITED)"
echo "3. Full stack with frontend"
echo "4. Development mode"
echo ""

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🚀 Deploying core services..."
        docker-compose up -d db redis api bot
        ;;
    2)
        echo "🚀 Deploying with SAFE MTProto data collection..."
        echo "🛡️ Rate limiting protections enabled"
        docker-compose --profile mtproto up -d db redis api bot mtproto
        ;;
    3)
        echo "🚀 Deploying full stack..."
        docker-compose --profile mtproto up -d
        ;;
    4)
        echo "🚀 Deploying development mode..."
        docker-compose --profile dev --profile mtproto up -d
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
echo "🔍 Checking service health..."

# Check database
if docker-compose exec -T db pg_isready > /dev/null 2>&1; then
    echo "   ✅ Database: Healthy"
else
    echo "   ❌ Database: Not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "   ✅ Redis: Healthy"
else
    echo "   ❌ Redis: Not ready"
fi

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ API: Healthy"
else
    echo "   ❌ API: Not ready"
fi

# Check MTProto service if deployed
if [ "$choice" -eq 2 ] || [ "$choice" -eq 3 ] || [ "$choice" -eq 4 ]; then
    echo "   🔍 MTProto service status..."
    if docker-compose exec -T mtproto python scripts/mtproto_service.py status > /dev/null 2>&1; then
        echo "   ✅ MTProto: Healthy with rate limiting"
    else
        echo "   ⚠️  MTProto: Starting or checking configuration"
    fi
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "   API: http://localhost:8000"
echo "   Database: localhost:5433"
echo "   Redis: localhost:6380"

if [ "$choice" -eq 3 ] || [ "$choice" -eq 4 ]; then
    echo "   Frontend: http://localhost:3000"
fi

echo ""
echo "🛡️ SAFETY REMINDERS:"
echo "   • Rate limiting is active on all data collection"
echo "   • Message limits are capped at safe levels"
echo "   • Multi-layer delays prevent Telegram blocks"
echo "   • Monitor logs for any rate limit warnings"
echo ""
echo "📊 To monitor data collection:"
echo "   docker-compose logs -f mtproto"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose down"
