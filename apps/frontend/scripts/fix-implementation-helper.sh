#!/bin/bash

##################################################
# Frontend Fix Implementation Helper Script
# Automates repetitive tasks from the fix plan
##################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Frontend Fix Implementation Helper${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Function to print colored messages
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "package.json" ]; then
        error "Not in frontend directory! Please run from apps/frontend/"
        exit 1
    fi
    success "Directory check passed"
}

# Function to create backup
create_backup() {
    info "Creating backup..."
    BACKUP_DIR="../frontend-backup-$(date +%Y%m%d-%H%M%S)"
    cp -r . "$BACKUP_DIR"
    success "Backup created at: $BACKUP_DIR"
}

# Menu function
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo ""
    echo "Week 1 - Critical Fixes:"
    echo "  1) Create logger utility (Issue #1)"
    echo "  2) Audit console.log usage"
    echo "  3) Create storage manager (Issue #2)"
    echo "  4) Audit localStorage usage"
    echo "  5) Install and setup Zod for env validation (Issue #3)"
    echo ""
    echo "Week 2 - High Priority:"
    echo "  6) Check outdated packages"
    echo "  7) Upgrade safe packages only"
    echo "  8) Find all .js/.jsx files to convert"
    echo ""
    echo "Week 3 - Medium Priority:"
    echo "  9) Audit components for optimization"
    echo " 10) Find all 'any' types"
    echo ""
    echo "Utilities:"
    echo " 11) Run all audits"
    echo " 12) Check current status"
    echo " 13) Install all new dependencies"
    echo ""
    echo "  0) Exit"
    echo ""
    read -p "Enter your choice: " choice
}

# Function 1: Create logger utility
create_logger() {
    info "Creating logger utility..."
    
    if [ -f "src/utils/logger.ts" ]; then
        warning "Logger already exists. Backing up..."
        mv src/utils/logger.ts src/utils/logger.ts.backup
    fi
    
    # Logger code will be created by user following the plan
    success "Ready to create src/utils/logger.ts - Check FRONTEND_FIX_IMPLEMENTATION_PLAN.md Step 1.1"
}

# Function 2: Audit console.log usage
audit_console_logs() {
    info "Auditing console.log usage..."
    
    echo "" > console_audit.txt
    echo "=== CONSOLE.LOG AUDIT ===" >> console_audit.txt
    echo "Generated: $(date)" >> console_audit.txt
    echo "" >> console_audit.txt
    
    echo "Console.log instances:" >> console_audit.txt
    grep -rn "console\.log" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> console_audit.txt || true
    
    echo -e "\n\nConsole.error instances:" >> console_audit.txt
    grep -rn "console\.error" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> console_audit.txt || true
    
    echo -e "\n\nConsole.warn instances:" >> console_audit.txt
    grep -rn "console\.warn" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> console_audit.txt || true
    
    echo -e "\n\nConsole.debug instances:" >> console_audit.txt
    grep -rn "console\.debug" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> console_audit.txt || true
    
    LOG_COUNT=$(grep -c "console\.log" console_audit.txt || echo "0")
    ERROR_COUNT=$(grep -c "console\.error" console_audit.txt || echo "0")
    WARN_COUNT=$(grep -c "console\.warn" console_audit.txt || echo "0")
    
    success "Audit complete! Results saved to console_audit.txt"
    info "Found: $LOG_COUNT console.log, $ERROR_COUNT console.error, $WARN_COUNT console.warn"
}

# Function 3: Create storage manager
create_storage_manager() {
    info "Creating storage manager..."
    
    if [ -f "src/utils/storage.ts" ]; then
        warning "Storage manager already exists. Backing up..."
        mv src/utils/storage.ts src/utils/storage.ts.backup
    fi
    
    success "Ready to create src/utils/storage.ts - Check FRONTEND_FIX_IMPLEMENTATION_PLAN.md Step 2.2"
}

# Function 4: Audit localStorage usage
audit_localstorage() {
    info "Auditing localStorage usage..."
    
    echo "" > storage_audit.txt
    echo "=== LOCALSTORAGE AUDIT ===" >> storage_audit.txt
    echo "Generated: $(date)" >> storage_audit.txt
    echo "" >> storage_audit.txt
    
    echo "localStorage.getItem:" >> storage_audit.txt
    grep -rn "localStorage\.getItem" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> storage_audit.txt || true
    
    echo -e "\n\nlocalStorage.setItem:" >> storage_audit.txt
    grep -rn "localStorage\.setItem" src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> storage_audit.txt || true
    
    echo -e "\n\nsessionStorage usage:" >> storage_audit.txt
    grep -rn "sessionStorage\." src/ --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" 2>/dev/null >> storage_audit.txt || true
    
    GET_COUNT=$(grep -c "localStorage\.getItem" storage_audit.txt || echo "0")
    SET_COUNT=$(grep -c "localStorage\.setItem" storage_audit.txt || echo "0")
    
    success "Audit complete! Results saved to storage_audit.txt"
    info "Found: $GET_COUNT getItem calls, $SET_COUNT setItem calls"
}

# Function 5: Setup Zod
setup_zod() {
    info "Installing Zod for environment validation..."
    npm install zod
    success "Zod installed! Ready to create src/config/env.ts - Check Step 3.2"
}

# Function 6: Check outdated packages
check_outdated() {
    info "Checking for outdated packages..."
    npm outdated
    success "Outdated packages check complete"
}

# Function 7: Upgrade safe packages
upgrade_safe_packages() {
    info "Upgrading safe packages (patch/minor updates only)..."
    warning "This will modify package.json and package-lock.json"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm update
        npm audit fix
        success "Safe packages upgraded!"
        info "Run 'npm run build' to test"
    else
        warning "Upgrade cancelled"
    fi
}

# Function 8: Find JS files
find_js_files() {
    info "Finding all .js and .jsx files..."
    
    echo "" > js_files_to_convert.txt
    echo "=== JS/JSX FILES TO CONVERT ===" >> js_files_to_convert.txt
    echo "Generated: $(date)" >> js_files_to_convert.txt
    echo "" >> js_files_to_convert.txt
    
    find src -name "*.js" -o -name "*.jsx" >> js_files_to_convert.txt
    
    JS_COUNT=$(find src -name "*.js" -o -name "*.jsx" | wc -l)
    
    success "Found $JS_COUNT JS/JSX files to convert"
    success "List saved to js_files_to_convert.txt"
}

# Function 9: Audit components
audit_components() {
    info "Auditing components for optimization opportunities..."
    
    echo "" > component_audit.txt
    echo "=== COMPONENT OPTIMIZATION AUDIT ===" >> component_audit.txt
    echo "Generated: $(date)" >> component_audit.txt
    echo "" >> component_audit.txt
    
    echo "Components with multiple useEffect:" >> component_audit.txt
    grep -rn "useEffect" src/components/ --include="*.tsx" 2>/dev/null | cut -d: -f1 | sort | uniq -c | sort -rn >> component_audit.txt || true
    
    echo -e "\n\nComponents with useState:" >> component_audit.txt
    grep -rn "useState" src/components/ --include="*.tsx" 2>/dev/null | cut -d: -f1 | sort | uniq -c | sort -rn >> component_audit.txt || true
    
    success "Component audit complete! Results saved to component_audit.txt"
}

# Function 10: Find 'any' types
find_any_types() {
    info "Finding all 'any' types..."
    
    echo "" > any_types_audit.txt
    echo "=== TYPESCRIPT 'ANY' AUDIT ===" >> any_types_audit.txt
    echo "Generated: $(date)" >> any_types_audit.txt
    echo "" >> any_types_audit.txt
    
    echo "'as any' usage:" >> any_types_audit.txt
    grep -rn "as any" src/ --include="*.ts" --include="*.tsx" 2>/dev/null >> any_types_audit.txt || true
    
    echo -e "\n\n': any' annotations:" >> any_types_audit.txt
    grep -rn ": any" src/ --include="*.ts" --include="*.tsx" 2>/dev/null >> any_types_audit.txt || true
    
    ANY_COUNT=$(grep -c "any" any_types_audit.txt || echo "0")
    
    success "Found $ANY_COUNT 'any' type usage instances"
    success "Results saved to any_types_audit.txt"
}

# Function 11: Run all audits
run_all_audits() {
    info "Running all audits..."
    audit_console_logs
    audit_localstorage
    find_js_files
    find_any_types
    audit_components
    success "All audits complete! Check the generated *_audit.txt files"
}

# Function 12: Check status
check_status() {
    info "Checking implementation status..."
    echo ""
    
    # Check if utilities exist
    echo "Status of key files:"
    [ -f "src/utils/logger.ts" ] && success "✓ logger.ts exists" || warning "✗ logger.ts missing"
    [ -f "src/utils/storage.ts" ] && success "✓ storage.ts exists" || warning "✗ storage.ts missing"
    [ -f "src/config/env.ts" ] && success "✓ env.ts exists" || warning "✗ env.ts missing"
    
    echo ""
    
    # Check if Zod is installed
    if npm list zod &>/dev/null; then
        success "✓ Zod installed"
    else
        warning "✗ Zod not installed"
    fi
    
    echo ""
    
    # Count remaining issues
    if [ -f "console_audit.txt" ]; then
        LOG_COUNT=$(grep -c "console\.log" src/ --include="*.ts" --include="*.tsx" 2>/dev/null || echo "0")
        info "Console.log instances remaining: $LOG_COUNT"
    fi
    
    if [ -f "storage_audit.txt" ]; then
        STORAGE_COUNT=$(grep -c "localStorage\." src/ --include="*.ts" --include="*.tsx" 2>/dev/null || echo "0")
        info "Direct localStorage calls remaining: $STORAGE_COUNT"
    fi
}

# Function 13: Install new dependencies
install_dependencies() {
    info "Installing all new dependencies for the fixes..."
    warning "This will install: zod, rollup-plugin-visualizer, vite-plugin-compression"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm install zod
        npm install --save-dev rollup-plugin-visualizer vite-plugin-compression
        success "Dependencies installed!"
    else
        warning "Installation cancelled"
    fi
}

# Main script
main() {
    check_directory
    
    while true; do
        show_menu
        
        case $choice in
            1) create_logger ;;
            2) audit_console_logs ;;
            3) create_storage_manager ;;
            4) audit_localstorage ;;
            5) setup_zod ;;
            6) check_outdated ;;
            7) upgrade_safe_packages ;;
            8) find_js_files ;;
            9) audit_components ;;
            10) find_any_types ;;
            11) run_all_audits ;;
            12) check_status ;;
            13) install_dependencies ;;
            0) 
                info "Exiting..."
                exit 0
                ;;
            *)
                error "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main
main
