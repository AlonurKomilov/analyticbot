#!/bin/bash
# Docker Build Optimization Script for AnalyticBot
# Provides intelligent caching and multi-stage build management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
BUILD_TARGET=""
BUILD_CONTEXT="../"
DOCKERFILE="docker/Dockerfile"
BUILD_ARGS=""
CACHE_FROM=""
CACHE_TO=""
PLATFORM="linux/amd64"
BUILD_KIT="1"

echo -e "${BLUE}🚀 AnalyticBot Docker Build Optimizer${NC}"
echo "====================================="

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --target)
            BUILD_TARGET="$2"
            shift 2
            ;;
        --context)
            BUILD_CONTEXT="$2"
            shift 2
            ;;
        --dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-cache)
            BUILD_ARGS="$BUILD_ARGS --no-cache"
            shift
            ;;
        --cache-from)
            CACHE_FROM="$2"
            shift 2
            ;;
        --cache-to)
            CACHE_TO="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS] TARGET"
            echo ""
            echo "Options:"
            echo "  --target TARGET        Build specific target (api, bot, worker, etc.)"
            echo "  --context PATH         Build context path (default: ../)"
            echo "  --dockerfile PATH      Dockerfile path (default: docker/Dockerfile)"
            echo "  --platform PLATFORM   Target platform (default: linux/amd64)"
            echo "  --no-cache            Disable cache"
            echo "  --cache-from CACHE    Cache source"
            echo "  --cache-to CACHE      Cache destination"
            echo "  --help                Show this help"
            echo ""
            echo "Available Targets:"
            echo "  api        - FastAPI application server"
            echo "  bot        - Telegram bot service"
            echo "  worker     - Celery worker"
            echo "  beat       - Celery scheduler"
            echo "  mtproto    - MTProto service"
            echo "  frontend   - Production frontend"
            echo "  frontend-dev - Development frontend"
            echo ""
            echo "Examples:"
            echo "  $0 --target api"
            echo "  $0 --target frontend --no-cache"
            echo "  $0 --target api --cache-from type=registry,ref=myregistry/analyticbot:cache"
            exit 0
            ;;
        *)
            if [ -z "$BUILD_TARGET" ]; then
                BUILD_TARGET="$1"
            else
                echo -e "${RED}❌ Unknown argument: $1${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate target
if [ -z "$BUILD_TARGET" ]; then
    echo -e "${RED}❌ Build target is required${NC}"
    echo "Available targets: api, bot, worker, beat, mtproto, frontend, frontend-dev"
    echo "Use --help for more information"
    exit 1
fi

# Validate target exists
VALID_TARGETS="api bot worker beat mtproto frontend frontend-dev"
if [[ ! " $VALID_TARGETS " =~ " $BUILD_TARGET " ]]; then
    echo -e "${RED}❌ Invalid target: $BUILD_TARGET${NC}"
    echo "Valid targets: $VALID_TARGETS"
    exit 1
fi

# Enable BuildKit for better performance
export DOCKER_BUILDKIT=$BUILD_KIT

echo -e "${BLUE}📋 Build Configuration:${NC}"
echo "  Target: $BUILD_TARGET"
echo "  Context: $BUILD_CONTEXT"
echo "  Dockerfile: $DOCKERFILE"
echo "  Platform: $PLATFORM"
echo "  BuildKit: $BUILD_KIT"

# Prepare build command
BUILD_CMD="docker build"
BUILD_CMD="$BUILD_CMD --file $DOCKERFILE"
BUILD_CMD="$BUILD_CMD --target $BUILD_TARGET"
BUILD_CMD="$BUILD_CMD --platform $PLATFORM"
BUILD_CMD="$BUILD_CMD --tag analyticbot:$BUILD_TARGET"
BUILD_CMD="$BUILD_CMD --tag analyticbot:$BUILD_TARGET-$(date +%Y%m%d-%H%M%S)"

# Add build arguments
if [ -n "$BUILD_ARGS" ]; then
    BUILD_CMD="$BUILD_CMD $BUILD_ARGS"
fi

# Add cache configuration
if [ -n "$CACHE_FROM" ]; then
    BUILD_CMD="$BUILD_CMD --cache-from $CACHE_FROM"
fi

if [ -n "$CACHE_TO" ]; then
    BUILD_CMD="$BUILD_CMD --cache-to $CACHE_TO"
fi

# Add build context
BUILD_CMD="$BUILD_CMD $BUILD_CONTEXT"

echo ""
echo -e "${YELLOW}🔨 Starting optimized build...${NC}"
echo "Command: $BUILD_CMD"
echo ""

# Check build context size
CONTEXT_SIZE=$(du -sh $BUILD_CONTEXT 2>/dev/null | cut -f1 || echo "unknown")
echo -e "${BLUE}📊 Build context size: $CONTEXT_SIZE${NC}"

# Run the build
start_time=$(date +%s)
if eval $BUILD_CMD; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo ""
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    echo -e "${BLUE}⏱️  Build time: ${duration}s${NC}"
    
    # Show image size
    IMAGE_SIZE=$(docker images analyticbot:$BUILD_TARGET --format "table {{.Size}}" | tail -n 1)
    echo -e "${BLUE}📦 Image size: $IMAGE_SIZE${NC}"
    
    echo ""
    echo -e "${GREEN}🎉 Image ready: analyticbot:$BUILD_TARGET${NC}"
    echo "To run: docker run -it analyticbot:$BUILD_TARGET"
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Show build cache info if BuildKit is enabled
if [ "$BUILD_KIT" = "1" ]; then
    echo ""
    echo -e "${BLUE}💾 BuildKit Cache Status:${NC}"
    docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Size}}\t{{.Reclaimable}}" | grep -E "(TYPE|Build Cache)" || echo "No cache information available"
fi

echo ""
echo -e "${BLUE}💡 Optimization Tips:${NC}"
echo "  • Use --cache-from for CI/CD builds"
echo "  • Regular cleanup: docker system prune -f"
echo "  • Multi-platform builds: --platform linux/amd64,linux/arm64"
echo "  • Layer analysis: docker history analyticbot:$BUILD_TARGET"