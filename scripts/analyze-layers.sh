#!/bin/bash
# Docker Layer Analysis Script for AnalyticBot
# Analyzes image layers, build cache efficiency, and provides optimization recommendations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

IMAGE_NAME=${1:-"analyticbot"}

echo -e "${BLUE}🔍 Docker Layer Analysis for $IMAGE_NAME${NC}"
echo "================================================="

# Check if image exists
if ! docker images $IMAGE_NAME* --format "{{.Repository}}:{{.Tag}}" | head -1 >/dev/null 2>&1; then
    echo -e "${RED}❌ No images found matching: $IMAGE_NAME${NC}"
    echo "Available images:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    exit 1
fi

echo -e "${BLUE}📊 Image Overview:${NC}"
echo "==================="
docker images $IMAGE_NAME* --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo -e "${BLUE}🔬 Layer Analysis:${NC}"
echo "=================="

# Analyze each image
for image in $(docker images $IMAGE_NAME* --format "{{.Repository}}:{{.Tag}}"); do
    echo ""
    echo -e "${YELLOW}📋 Image: $image${NC}"
    echo "----------------------------------------"
    
    # Get image ID
    IMAGE_ID=$(docker images $image --format "{{.ID}}")
    
    # Show layer history
    echo -e "${BLUE}Layer History (most recent first):${NC}"
    docker history $image --format "table {{.CreatedBy}}\t{{.Size}}" --no-trunc | head -10
    
    # Show layer sizes
    echo ""
    echo -e "${BLUE}Largest Layers:${NC}"
    docker history $image --format "{{.Size}}\t{{.CreatedBy}}" --no-trunc | \
        grep -v "0B" | sort -hr | head -5 | \
        while read size command; do
            echo "  $size - $(echo $command | cut -c1-100)..."
        done
    
    echo ""
done

echo ""
echo -e "${BLUE}💾 Build Cache Analysis:${NC}"
echo "========================="
docker system df --format "table {{.Type}}\t{{.Total}}\t{{.Active}}\t{{.Size}}\t{{.Reclaimable}}"

echo ""
echo -e "${BLUE}🚀 Optimization Recommendations:${NC}"
echo "=================================="

# Check for common optimization opportunities
TOTAL_CACHE_SIZE=$(docker system df --format "{{.Size}}" | grep "Build Cache" | head -1 || echo "0B")
TOTAL_IMAGES_SIZE=$(docker system df --format "{{.Size}}" | head -1)

echo -e "${GREEN}✅ Current Status:${NC}"
echo "  • Total Images Size: $TOTAL_IMAGES_SIZE"
echo "  • Build Cache Size: $TOTAL_CACHE_SIZE"
echo "  • BuildKit Enabled: $([ "$DOCKER_BUILDKIT" = "1" ] && echo "Yes" || echo "No")"

echo ""
echo -e "${YELLOW}💡 Optimization Tips:${NC}"

# Check .dockerignore
if [ -f ".dockerignore" ]; then
    DOCKERIGNORE_LINES=$(wc -l < .dockerignore)
    echo "  ✅ .dockerignore exists ($DOCKERIGNORE_LINES lines)"
else
    echo "  ❌ .dockerignore missing - add it to reduce build context"
fi

# Check for multi-stage builds
if grep -q "FROM.*AS" docker/Dockerfile 2>/dev/null; then
    STAGES=$(grep -c "FROM.*AS" docker/Dockerfile)
    echo "  ✅ Multi-stage build detected ($STAGES stages)"
else
    echo "  ❌ Consider using multi-stage builds"
fi

# Check for layer optimization opportunities
echo ""
echo -e "${BLUE}🎯 Build Performance Tips:${NC}"
echo "1. Use specific service builds: make build-api, build-bot"
echo "2. Enable BuildKit: export DOCKER_BUILDKIT=1"
echo "3. Use cache mounts: RUN --mount=type=cache,target=/root/.cache/pip"
echo "4. Order layers by change frequency (deps first, code last)"
echo "5. Use .dockerignore to reduce build context"
echo "6. Regular cleanup: docker system prune -f"

echo ""
echo -e "${BLUE}📈 Cache Efficiency Score:${NC}"

# Calculate cache efficiency (simplified)
if [ -f "docker/Dockerfile" ]; then
    COPY_LAYERS=$(grep -c "^COPY\|^ADD" docker/Dockerfile)
    RUN_LAYERS=$(grep -c "^RUN" docker/Dockerfile)
    TOTAL_LAYERS=$((COPY_LAYERS + RUN_LAYERS))
    
    if [ $TOTAL_LAYERS -gt 0 ]; then
        if [ $COPY_LAYERS -lt $RUN_LAYERS ]; then
            echo -e "${GREEN}✅ Good: More RUN than COPY layers ($RUN_LAYERS RUN, $COPY_LAYERS COPY)${NC}"
        else
            echo -e "${YELLOW}⚠️  Consider consolidating COPY operations ($RUN_LAYERS RUN, $COPY_LAYERS COPY)${NC}"
        fi
    fi
fi

echo ""
echo -e "${BLUE}🧹 Cleanup Commands:${NC}"
echo "===================="
echo "Clean build cache:     docker builder prune -f"
echo "Clean unused images:   docker image prune -f"
echo "Clean everything:      docker system prune -af"
echo "Clean specific image:  docker rmi $IMAGE_NAME:TAG"

echo ""
echo -e "${GREEN}🎉 Analysis complete!${NC}"