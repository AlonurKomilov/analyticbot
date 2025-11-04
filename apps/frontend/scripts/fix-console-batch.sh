#!/bin/bash
#
# Batch Console.log Replacement Script
# 
# This script systematically replaces console.* calls with appropriate logger instances
# across the frontend codebase.
#
# Usage: ./fix-console-batch.sh [file_pattern]
#

set -e

FRONTEND_DIR="/home/abcdeveloper/projects/analyticbot/apps/frontend"
cd "$FRONTEND_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Console.log Batch Replacement Tool ===${NC}\n"

# File groups based on domain
declare -A FILE_GROUPS=(
    ["store"]="store/slices/**/*.ts"
    ["utils"]="utils/*.tsx utils/*.ts"
    ["features"]="features/**/api/*.ts features/**/services/*.ts"
    ["validation"]="validation/*.ts"
    ["services"]="services/**/*.ts"
    ["shared"]="shared/**/*.tsx shared/**/*.ts"
    ["components"]="features/**/components/*.tsx"
)

# Function to detect appropriate logger for file
get_logger_for_file() {
    local file="$1"
    
    if [[ "$file" =~ /api/ ]] || [[ "$file" =~ /services/ ]] || [[ "$file" =~ API ]]; then
        echo "apiLogger"
    elif [[ "$file" =~ /auth/ ]] || [[ "$file" =~ Auth ]]; then
        echo "authLogger"
    elif [[ "$file" =~ /store/ ]] || [[ "$file" =~ Store ]]; then
        echo "storeLogger"
    elif [[ "$file" =~ /router/ ]] || [[ "$file" =~ Router ]] || [[ "$file" =~ Route ]]; then
        echo "routerLogger"
    else
        echo "uiLogger"
    fi
}

# Function to get relative import path to logger
get_import_path() {
    local file="$1"
    local depth=$(echo "$file" | grep -o "/" | wc -l)
    
    # Calculate relative path
    local prefix=""
    for ((i=1; i<depth; i++)); do
        prefix="../${prefix}"
    done
    
    echo "${prefix}utils/logger"
}

# Function to check if file already has logger import
has_logger_import() {
    local file="$1"
    grep -q "from.*utils/logger" "$file" 2>/dev/null
}

# Function to add logger import
add_logger_import() {
    local file="$1"
    local logger="$2"
    local import_path=$(get_import_path "$file")
    
    if has_logger_import "$file"; then
        echo -e "${YELLOW}  ⚠ Logger already imported${NC}"
        return 0
    fi
    
    # Find last import line
    local last_import=$(grep -n "^import " "$file" | tail -1 | cut -d: -f1)
    
    if [ -z "$last_import" ]; then
        echo -e "${RED}  ✗ No import statements found${NC}"
        return 1
    fi
    
    # Insert logger import after last import
    sed -i "${last_import}a import { ${logger} } from '${import_path}';" "$file"
    echo -e "${GREEN}  ✓ Added import: ${logger}${NC}"
}

# Function to replace console calls
replace_console_calls() {
    local file="$1"
    local logger="$2"
    
    # Count before
    local before=$(grep -c "console\." "$file" 2>/dev/null || echo 0)
    
    if [ "$before" -eq 0 ]; then
        echo -e "${YELLOW}  ⚠ No console calls found${NC}"
        return 0
    fi
    
    # Replace console.log, console.error, console.warn, console.info, console.debug
    sed -i "s/console\.log(/${logger}.log(/g" "$file"
    sed -i "s/console\.error(/${logger}.error(/g" "$file"
    sed -i "s/console\.warn(/${logger}.warn(/g" "$file"
    sed -i "s/console\.info(/${logger}.info(/g" "$file"
    sed -i "s/console\.debug(/${logger}.debug(/g" "$file"
    
    # Count after
    local after=$(grep -c "console\." "$file" 2>/dev/null || echo 0)
    local replaced=$((before - after))
    
    if [ "$replaced" -gt 0 ]; then
        echo -e "${GREEN}  ✓ Replaced ${replaced}/${before} console calls${NC}"
    else
        echo -e "${YELLOW}  ⚠ No replacements made (might contain console.table, console.dir, etc.)${NC}"
    fi
}

# Process a single file
process_file() {
    local file="$1"
    
    # Skip if file doesn't exist
    [ ! -f "$file" ] && return
    
    # Skip archive and test files
    [[ "$file" =~ /archive/ ]] && return
    [[ "$file" =~ /__tests__/ ]] && return
    [[ "$file" =~ /__mocks__/ ]] && return
    [[ "$file" =~ \.test\. ]] && return
    [[ "$file" =~ \.spec\. ]] && return
    
    echo -e "\n${BLUE}Processing:${NC} $file"
    
    # Detect appropriate logger
    local logger=$(get_logger_for_file "$file")
    echo -e "${BLUE}  Using: ${logger}${NC}"
    
    # Add import if needed
    add_logger_import "$file" "$logger"
    
    # Replace console calls
    replace_console_calls "$file" "$logger"
}

# Main processing
if [ $# -eq 1 ]; then
    # Process specific file or pattern
    echo -e "${BLUE}Processing pattern: $1${NC}\n"
    
    for file in src/$1; do
        process_file "$file"
    done
else
    # Process all file groups
    echo -e "${BLUE}Processing all file groups...${NC}\n"
    
    for group in "${!FILE_GROUPS[@]}"; do
        echo -e "\n${BLUE}=== Processing Group: ${group} ===${NC}"
        pattern="${FILE_GROUPS[$group]}"
        
        files=$(find src -path "src/${pattern}" 2>/dev/null || true)
        
        if [ -z "$files" ]; then
            echo -e "${YELLOW}No files found for pattern: ${pattern}${NC}"
            continue
        fi
        
        while IFS= read -r file; do
            process_file "$file"
        done <<< "$files"
    done
fi

echo -e "\n${GREEN}=== Batch Processing Complete ===${NC}\n"

# Final report
echo -e "${BLUE}Checking remaining console calls...${NC}"
remaining=$(grep -r "console\." --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js" src/ 2>/dev/null | grep -v "node_modules" | grep -v "archive" | grep -v "__mocks__" | wc -l)
echo -e "${YELLOW}Remaining console calls: ${remaining}${NC}\n"

echo -e "${BLUE}Top files with remaining console calls:${NC}"
grep -r "console\." --include="*.tsx" --include="*.ts" src/ 2>/dev/null | grep -v "node_modules" | grep -v "archive" | grep -v "__mocks__" | cut -d: -f1 | sort | uniq -c | sort -rn | head -10

echo -e "\n${GREEN}✓ Done!${NC}"
