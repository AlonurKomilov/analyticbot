#!/bin/bash

# Validate Environment Configuration Script
# Performs comprehensive validation of environment variables
# Updated to work with .env.development and .env.production files

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Environment Configuration Validation${NC}"
echo "========================================="

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

VALIDATION_ERRORS=()
VALIDATION_WARNINGS=()

# Validation functions
validate_required_var() {
    local var_name="$1"
    local var_value="${!var_name}"
    
    if [[ -z "$var_value" ]]; then
        VALIDATION_ERRORS+=("Required variable $var_name is missing")
        return 1
    fi
    return 0
}

validate_secret_key() {
    if validate_required_var "SECRET_KEY"; then
        # Skip validation if it contains variable substitution
        if [[ "$SECRET_KEY" == *"\${"* ]]; then
            echo -e "   ℹ️  ${BLUE}SECRET_KEY contains variable substitution - skipping format validation${NC}"
        else
            if [[ ${#SECRET_KEY} -lt 32 ]]; then
                VALIDATION_ERRORS+=("SECRET_KEY must be at least 32 characters long (current: ${#SECRET_KEY})")
            fi
            
            # Check for common weak patterns (but be more specific)
            if [[ "$SECRET_KEY" == "password123" ]] || [[ "$SECRET_KEY" == "123456789" ]] || [[ "$SECRET_KEY" == "secretkey" ]] || [[ "$SECRET_KEY" == "your_secret_key_here" ]]; then
                VALIDATION_WARNINGS+=("SECRET_KEY appears to be a common placeholder - consider using a more random key")
            fi
        fi
    fi
}

validate_jwt_config() {
    if validate_required_var "JWT_SECRET_KEY"; then
        # Skip validation if it contains variable substitution
        if [[ "$JWT_SECRET_KEY" == *"\${"* ]]; then
            echo -e "   ℹ️  ${BLUE}JWT_SECRET_KEY contains variable substitution - skipping format validation${NC}"
        else
            if [[ ${#JWT_SECRET_KEY} -lt 32 ]]; then
                VALIDATION_ERRORS+=("JWT_SECRET_KEY must be at least 32 characters long (current: ${#JWT_SECRET_KEY})")
            fi
            
            # Check for common weak patterns (but be more specific)
            if [[ "$JWT_SECRET_KEY" == "password123" ]] || [[ "$JWT_SECRET_KEY" == "123456789" ]] || [[ "$JWT_SECRET_KEY" == "secretkey" ]] || [[ "$JWT_SECRET_KEY" == "your_jwt_secret_here" ]]; then
                VALIDATION_WARNINGS+=("JWT_SECRET_KEY appears to be a common placeholder - consider using a more random key")
            fi
        fi
    fi
    
    # Validate JWT algorithm
    if [[ -n "$JWT_ALGORITHM" ]]; then
        case "$JWT_ALGORITHM" in
            HS256|HS384|HS512|RS256|RS384|RS512|ES256|ES384|ES512) ;;
            *) VALIDATION_WARNINGS+=("JWT_ALGORITHM '$JWT_ALGORITHM' is not a standard algorithm") ;;
        esac
    fi
}

validate_postgres_config() {
    validate_required_var "POSTGRES_USER"
    validate_required_var "POSTGRES_PASSWORD"
    validate_required_var "POSTGRES_DB"
    validate_required_var "POSTGRES_HOST"
    validate_required_var "POSTGRES_PORT"
    
    # Validate port is numeric
    if [[ -n "$POSTGRES_PORT" ]] && ! [[ "$POSTGRES_PORT" =~ ^[0-9]+$ ]]; then
        VALIDATION_ERRORS+=("POSTGRES_PORT must be numeric (current: $POSTGRES_PORT)")
    fi
    
    # Check password strength
    if [[ -n "$POSTGRES_PASSWORD" ]] && [[ ${#POSTGRES_PASSWORD} -lt 8 ]]; then
        VALIDATION_WARNINGS+=("POSTGRES_PASSWORD is less than 8 characters - consider using a stronger password")
    fi
}

validate_api_config() {
    validate_required_var "API_HOST"
    validate_required_var "API_PORT"
    
    # Validate API port is numeric and in valid range
    if [[ -n "$API_PORT" ]]; then
        if ! [[ "$API_PORT" =~ ^[0-9]+$ ]]; then
            VALIDATION_ERRORS+=("API_PORT must be numeric (current: $API_PORT)")
        elif [[ $API_PORT -lt 1024 ]] || [[ $API_PORT -gt 65535 ]]; then
            VALIDATION_WARNINGS+=("API_PORT $API_PORT is outside recommended range (1024-65535)")
        fi
    fi
}

validate_telegram_config() {
    validate_required_var "BOT_TOKEN"
    validate_required_var "ADMIN_IDS"
    
    # Validate bot token format (skip if it contains variable substitution)
    if [[ -n "$BOT_TOKEN" ]] && [[ "$BOT_TOKEN" != *"\${"* ]]; then
        if ! [[ "$BOT_TOKEN" =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
            VALIDATION_ERRORS+=("BOT_TOKEN format appears invalid (should be like: 123456789:ABC-DEF...)")
        fi
    fi
    
    # Validate admin IDs (can be comma-separated or array format)
    if [[ -n "$ADMIN_IDS" ]]; then
        # Skip validation if it contains variable substitution
        if [[ "$ADMIN_IDS" == *"\${"* ]]; then
            echo -e "   ℹ️  ${BLUE}ADMIN_IDS contains variable substitution - skipping format validation${NC}"
        else
            # Remove brackets and quotes for validation
            admin_ids_clean=$(echo "$ADMIN_IDS" | sed 's/[\[\]"]//g')
            IFS=',' read -ra ids <<< "$admin_ids_clean"
            for id in "${ids[@]}"; do
                id=$(echo "$id" | xargs) # trim whitespace
                if [[ -n "$id" ]] && ! [[ "$id" =~ ^[0-9]+$ ]]; then
                    VALIDATION_ERRORS+=("ADMIN_IDS contains non-numeric ID: $id")
                fi
            done
        fi
    fi
}

validate_optional_config() {
    # Validate LOG_LEVEL
    if [[ -n "$LOG_LEVEL" ]]; then
        case "$LOG_LEVEL" in
            DEBUG|INFO|WARNING|ERROR|CRITICAL) ;;
            *) VALIDATION_WARNINGS+=("LOG_LEVEL '$LOG_LEVEL' is not a standard level (DEBUG, INFO, WARNING, ERROR, CRITICAL)") ;;
        esac
    fi
    
    # Validate ENVIRONMENT
    if [[ -n "$ENVIRONMENT" ]]; then
        case "$ENVIRONMENT" in
            development|production|testing|staging) ;;
            *) VALIDATION_WARNINGS+=("ENVIRONMENT '$ENVIRONMENT' is not standard (development, production, testing, staging)") ;;
        esac
    fi
    
    # Validate DEBUG
    if [[ -n "$DEBUG" ]]; then
        case "$DEBUG" in
            true|false|True|False|1|0) ;;
            *) VALIDATION_WARNINGS+=("DEBUG should be true/false (current: $DEBUG)") ;;
        esac
    fi
}

check_file_permissions() {
    # Check permissions for environment files
    for env_file in ".env.development" ".env.production" ".env"; do
        if [[ -f "$env_file" ]]; then
            local perms=$(stat -c "%a" "$env_file")
            if [[ "$perms" != "600" ]] && [[ "$perms" != "644" ]]; then
                VALIDATION_WARNINGS+=("$env_file file permissions are $perms - consider setting to 600 for security")
            fi
        fi
    done
}

# Run all validations
echo -e "\n${YELLOW}🔐 Validating Security Configuration...${NC}"
validate_secret_key

echo -e "\n${YELLOW}� Validating JWT Configuration...${NC}"
validate_jwt_config

echo -e "\n${YELLOW}�🗄️  Validating Database Configuration...${NC}"
validate_postgres_config

echo -e "\n${YELLOW}🚀 Validating API Configuration...${NC}"
validate_api_config

echo -e "\n${YELLOW}🤖 Validating Telegram Configuration...${NC}"
validate_telegram_config

echo -e "\n${YELLOW}⚙️  Validating Optional Configuration...${NC}"
validate_optional_config

echo -e "\n${YELLOW}📁 Checking File Permissions...${NC}"
check_file_permissions

# Display results
echo -e "\n${YELLOW}📊 Validation Results:${NC}"
echo "========================"

if [[ ${#VALIDATION_ERRORS[@]} -eq 0 ]]; then
    echo -e "✅ ${GREEN}No validation errors found${NC}"
else
    echo -e "❌ ${RED}Found ${#VALIDATION_ERRORS[@]} validation errors:${NC}"
    for error in "${VALIDATION_ERRORS[@]}"; do
        echo -e "   • $error"
    done
fi

if [[ ${#VALIDATION_WARNINGS[@]} -gt 0 ]]; then
    echo -e "\n⚠️  ${YELLOW}Found ${#VALIDATION_WARNINGS[@]} warnings:${NC}"
    for warning in "${VALIDATION_WARNINGS[@]}"; do
        echo -e "   • $warning"
    done
fi

# Connection tests (if no errors)
if [[ ${#VALIDATION_ERRORS[@]} -eq 0 ]]; then
    echo -e "\n${YELLOW}🔗 Testing Connections...${NC}"
    
    # Test PostgreSQL connection (if available)
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" >/dev/null 2>&1; then
            echo -e "✅ ${GREEN}PostgreSQL connection successful${NC}"
        else
            echo -e "⚠️  ${YELLOW}PostgreSQL connection failed (service may not be running)${NC}"
        fi
    else
        echo -e "ℹ️  ${BLUE}PostgreSQL client not available for connection test${NC}"
    fi
    
    # Test Redis connection (if configured)
    if [[ -n "$REDIS_URL" ]] && command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; then
            echo -e "✅ ${GREEN}Redis connection successful${NC}"
        else
            echo -e "⚠️  ${YELLOW}Redis connection failed (service may not be running)${NC}"
        fi
    fi
fi

# Final summary
echo -e "\n${YELLOW}📋 Summary:${NC}"
if [[ ${#VALIDATION_ERRORS[@]} -eq 0 ]]; then
    echo -e "✅ ${GREEN}Environment configuration is valid and ready for use${NC}"
    exit 0
else
    echo -e "❌ ${RED}Environment configuration has errors that must be fixed${NC}"
    echo -e "💡 ${BLUE}Run ./scripts/create-env-template.sh to generate a template${NC}"
    exit 1
fi