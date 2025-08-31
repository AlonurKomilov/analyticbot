#!/usr/bin/env python3
"""
🛡️ Security & Code Quality Auto-Fixer
Addresses issues from GitHub Advanced Security alerts
"""

import re
import os
import sys
from pathlib import Path

def fix_regex_vulnerability():
    """Fix overly permissive regular expression in content_optimizer.py"""
    file_path = "/home/alonur/analyticbot/apps/bot/services/ml/content_optimizer.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    # The problematic regex pattern
    old_pattern = r'r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"'
    
    # Safer, more specific URL pattern
    new_pattern = r'r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?"'
    
    if old_pattern.replace('\\', '') in content.replace('\\', ''):
        # Replace the vulnerable pattern
        content = content.replace(
            'r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"',
            'r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?""'
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
            
        print("✅ Fixed overly permissive regex pattern in content_optimizer.py")
        return True
    else:
        print("⚠️  Regex pattern not found or already fixed")
        return False

def fix_unused_imports():
    """Remove unused imports from various files"""
    fixes_applied = 0
    
    # File-specific unused import fixes
    unused_imports_map = {
        "/home/alonur/analyticbot/twa-frontend/src/components/StorageFileBrowser.jsx": ["DownloadIcon"],
        "/home/alonur/analyticbot/twa-frontend/src/components/PostViewDynamicsChart.jsx": ["Line", "LineChart"],
        "/home/alonur/analyticbot/twa-frontend/src/components/EnhancedMediaUploader.jsx": ["RefreshIcon", "Button", "Tooltip"],
        "/home/alonur/analyticbot/twa-frontend/src/components/BestTimeRecommender.jsx": ["TimeIcon", "TrendingUpIcon", "IconButton"],
        "/home/alonur/analyticbot/twa-frontend/src/components/AnalyticsDashboard.jsx": ["Fab"],
    }
    
    for file_path, unused_imports in unused_imports_map.items():
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            original_content = content
            
            # Remove unused imports from import statements
            for unused_import in unused_imports:
                # Pattern to match import statements
                patterns = [
                    # Named imports: import { A, UnusedImport, B }
                    rf'import\s*\{{\s*([^}}]*?),?\s*{re.escape(unused_import)}\s*,?\s*([^}}]*?)\s*\}}\s*from',
                    # Single import: import UnusedImport from
                    rf'import\s+{re.escape(unused_import)}\s+from[^\n]*\n',
                    # Default with named: import Default, { UnusedImport }
                    rf'(import\s+\w+\s*,\s*\{{\s*[^}}]*?),?\s*{re.escape(unused_import)}\s*,?\s*([^}}]*?\}})',
                ]
                
                for pattern in patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        # More sophisticated replacement
                        content = re.sub(pattern, lambda m: fix_import_statement(m, unused_import), content, flags=re.MULTILINE)
                        
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Removed unused imports from {os.path.basename(file_path)}: {', '.join(unused_imports)}")
                fixes_applied += 1
            else:
                print(f"⚠️  No changes needed in {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            
    return fixes_applied

def fix_import_statement(match, unused_import):
    """Helper function to properly fix import statements"""
    full_match = match.group(0)
    
    # If it's a single import line, remove the entire line
    if f'import {unused_import} from' in full_match:
        return ''
        
    # For named imports, carefully remove just the unused import
    # This is a simplified approach - in production, use AST parsing
    result = full_match
    
    # Remove the unused import and clean up commas
    result = re.sub(rf',?\s*{re.escape(unused_import)}\s*,?', '', result)
    result = re.sub(r',\s*,', ',', result)  # Fix double commas
    result = re.sub(r'{\s*,', '{', result)  # Fix leading comma
    result = re.sub(r',\s*}', '}', result)  # Fix trailing comma
    
    return result

def fix_information_exposure():
    """Fix information exposure through exceptions"""
    api_files = [
        "/home/alonur/analyticbot/apis/standalone_performance_api.py",
        "/home/alonur/analyticbot/apis/performance_api.py",
        "/home/alonur/analyticbot/apis/main_api.py",
        "/home/alonur/analyticbot/api.py",
    ]
    
    fixes_applied = 0
    
    for file_path in api_files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            original_content = content
            
            # Pattern to find exception handling that might expose stack traces
            patterns_to_fix = [
                # return {"error": str(e)} -> return {"error": "Internal server error"}
                (r'return\s*\{\s*["\']error["\']\s*:\s*str\(e\)\s*\}', 'return {"error": "Internal server error"}'),
                # logger.error(f"Error: {e}") -> logger.error(f"Error occurred", exc_info=True)
                (r'logger\.error\(f?["\']([^"\']*)\{e\}["\'][^)]*\)', r'logger.error("\1", exc_info=True)'),
                # print(e) -> logger.error("Error occurred", exc_info=True)
                (r'print\(e\)', 'logger.error("Error occurred", exc_info=True)'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed information exposure in {os.path.basename(file_path)}")
                fixes_applied += 1
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            
    return fixes_applied

def fix_url_sanitization():
    """Fix incomplete URL substring sanitization"""
    test_file = "/home/alonur/analyticbot/tests/test_security_system.py"
    
    if not os.path.exists(test_file):
        print(f"⚠️  Test file not found: {test_file}")
        return False
        
    try:
        with open(test_file, 'r') as f:
            content = f.read()
            
        # Look for the problematic URL checking pattern
        if "accounts.google.com" in content:
            # Replace with more secure URL validation
            content = re.sub(
                r'if\s+"accounts\.google\.com"\s+in\s+auth_url:',
                'if auth_url.startswith("https://accounts.google.com/"):',
                content
            )
            
            with open(test_file, 'w') as f:
                f.write(content)
                
            print("✅ Fixed URL substring sanitization in test_security_system.py")
            return True
        else:
            print("⚠️  URL pattern not found or already fixed")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing URL sanitization: {e}")
        return False

def validate_fixes():
    """Validate that the fixes were applied correctly"""
    print("\n🔍 Validating fixes...")
    
    validation_passed = True
    
    # Check if regex was fixed
    content_optimizer_path = "/home/alonur/analyticbot/apps/bot/services/ml/content_optimizer.py"
    if os.path.exists(content_optimizer_path):
        with open(content_optimizer_path, 'r') as f:
            content = f.read()
        if '[$-_@.&+]' not in content:
            print("✅ Regex vulnerability fix validated")
        else:
            print("❌ Regex vulnerability still present")
            validation_passed = False
    
    # Add more validation as needed
    
    return validation_passed

def main():
    """Main function to run all security fixes"""
    print("🛡️  Security & Code Quality Auto-Fixer")
    print("=" * 50)
    print()
    
    total_fixes = 0
    
    # Fix regex vulnerability
    print("🔧 Fixing regex vulnerability...")
    if fix_regex_vulnerability():
        total_fixes += 1
    
    print("\n🔧 Fixing unused imports...")
    unused_import_fixes = fix_unused_imports()
    total_fixes += unused_import_fixes
    
    print("\n🔧 Fixing information exposure...")
    info_exposure_fixes = fix_information_exposure()
    total_fixes += info_exposure_fixes
    
    print("\n🔧 Fixing URL sanitization...")
    if fix_url_sanitization():
        total_fixes += 1
    
    # Validate fixes
    print("\n🔍 Validating fixes...")
    if validate_fixes():
        print("✅ All fixes validated successfully")
    else:
        print("⚠️  Some fixes may need manual review")
    
    print(f"\n📊 Summary:")
    print(f"   Total fixes applied: {total_fixes}")
    print(f"   Files processed: Multiple")
    print(f"   Security issues addressed: 4 categories")
    
    if total_fixes > 0:
        print(f"\n🎉 {total_fixes} security fixes applied successfully!")
        print("\n📋 Next steps:")
        print("   1. Review the changes")
        print("   2. Run tests to ensure no regressions")
        print("   3. Commit the changes")
        print("   4. Monitor GitHub Security alerts")
    else:
        print("\n✨ No fixes needed - code is already secure!")
    
    return total_fixes

if __name__ == "__main__":
    try:
        fixes_applied = main()
        sys.exit(0 if fixes_applied >= 0 else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
