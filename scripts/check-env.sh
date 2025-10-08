#!/bin/bash

# Check Environment Variables Script
# Validates that all required environment variables are set
# Updated to work with .env.development and .env.production files

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}🔍 Environment Variables Check${NC}"
echo "=================================="

# Detect and load appropriate environment file
ENV_FILE=""
ENV_TYPE=""

if [[ -f ".env.development" ]]; then
    ENV_FILE=".env.development"
    ENV_TYPE="development"
elif [[ -f ".env.production" ]]; then
    ENV_FILE=".env.production"
    ENV_TYPE="production"
elif [[ -f ".env" ]]; then
    ENV_FILE=".env"
    ENV_TYPE="generic"
fi

if [[ -n "$ENV_FILE" ]]; then
    echo -e "📄 Loading $ENV_FILE ($ENV_TYPE environment)..."
    # Safe loading with proper escaping
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue

        # Extract variable name and value
        if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
            var_name="${BASH_REMATCH[1]}"
            var_value="${BASH_REMATCH[2]}"

            # Remove surrounding quotes if present
            var_value="${var_value%\"}"
            var_value="${var_value#\"}"
            var_value="${var_value%\'}"
            var_value="${var_value#\'}"

            # Export the variable
            export "$var_name"="$var_value"
        fi
    done < "$ENV_FILE"
else
    echo -e "⚠️  ${YELLOW}No environment file found${NC}"
    echo -e "   Looking for: .env.development, .env.production, or .env"
fi

# Required environment variables (based on your .env structure)
REQUIRED_VARS=(
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "POSTGRES_DB"
    "POSTGRES_HOST"
    "POSTGRES_PORT"
    "SECRET_KEY"
    "JWT_SECRET_KEY"
    "API_HOST"
    "API_PORT"
    "BOT_TOKEN"
    "ADMIN_IDS"
)

# Optional environment variables with defaults
OPTIONAL_VARS=(
    "ENVIRONMENT:development"
    "DEBUG:true"
    "LOG_LEVEL:INFO"
    "REDIS_URL:redis://localhost:6379"
    "CORS_ORIGINS:*"
)

# Check required variables
echo -e "\n${YELLOW}📋 Required Variables:${NC}"
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo -e "  ❌ ${RED}$var${NC} - Missing"
        MISSING_VARS+=("$var")
    else
        # Mask sensitive values
        if [[ $var == *"PASSWORD"* ]] || [[ $var == *"SECRET"* ]] || [[ $var == *"TOKEN"* ]]; then
            masked_value=$(echo "${!var}" | sed 's/./*/g')
            echo -e "  ✅ ${GREEN}$var${NC} - $masked_value"
        else
            echo -e "  ✅ ${GREEN}$var${NC} - ${!var}"
        fi
    fi
done

# Check optional variables
echo -e "\n${YELLOW}⚙️  Optional Variables (with defaults):${NC}"
for var_default in "${OPTIONAL_VARS[@]}"; do
    var="${var_default%%:*}"
    default="${var_default##*:}"

    if [[ -z "${!var}" ]]; then
        echo -e "  ⚠️  ${YELLOW}$var${NC} - Using default: $default"
    else
        echo -e "  ✅ ${GREEN}$var${NC} - ${!var}"
    fi
done

# Check for environment files
echo -e "\n${YELLOW}📄 Environment Files:${NC}"

# Check development environment
if [[ -f ".env.development" ]]; then
    echo -e "  ✅ ${GREEN}.env.development${NC} - Found (Development config)"
    if [[ -f ".env.development.example" ]]; then
        echo -e "     ℹ️  ${BLUE}.env.development.example${NC} - Template available"
    fi
fi

# Check production environment
if [[ -f ".env.production" ]]; then
    echo -e "  ✅ ${GREEN}.env.production${NC} - Found (Production config)"
    if [[ -f ".env.production.example" ]]; then
        echo -e "     ℹ️  ${BLUE}.env.production.example${NC} - Template available"
    fi
fi

# Check generic .env
if [[ -f ".env" ]]; then
    echo -e "  ✅ ${GREEN}.env${NC} - Found (Generic config)"
fi

# Current environment info
if [[ -n "$ENV_FILE" ]]; then
    echo -e "  🎯 ${BLUE}Active Environment:${NC} $ENV_TYPE ($ENV_FILE)"
else
    echo -e "  ⚠️  ${YELLOW}No environment file loaded${NC}"
fi

# Summary
echo -e "\n${YELLOW}📊 Summary:${NC}"
if [[ ${#MISSING_VARS[@]} -eq 0 ]]; then
    echo -e "  ✅ ${GREEN}All required environment variables are set${NC}"
    exit 0
else
    echo -e "  ❌ ${RED}Missing ${#MISSING_VARS[@]} required variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "     - $var"
    done
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "  1. Create a .env file with the missing variables"
    echo "  2. Export variables in your shell: export VAR_NAME=value"
    echo "  3. Use ./scripts/create-env-template.sh to generate a template"
    exit 1
fi
