#!/usr/bin/env python3
"""
Fix Duplicate Test Functions
Identifies and suggests fixes for duplicate test function names
"""

import ast
import os
from collections import defaultdict
from pathlib import Path


def analyze_test_duplicates():
    """Analyze and report duplicate test functions"""

    print("🔍 ANALYZING TEST DUPLICATES")
    print("=" * 50)

    # Collect all test functions
    all_functions = defaultdict(list)
    total_functions = 0

    for root, dirs, files in os.walk("tests/"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                            all_functions[node.name].append(file_path)
                            total_functions += 1

                except Exception as e:
                    print(f"⚠️ Could not parse {file_path}: {e}")

    # Find duplicates
    duplicates = {name: files for name, files in all_functions.items() if len(files) > 1}

    print("📊 DUPLICATE ANALYSIS:")
    print(f"Total test functions: {total_functions}")
    print(f"Unique function names: {len(all_functions)}")
    print(f"Duplicate function names: {len(duplicates)}")
    print(f"Total duplicate instances: {sum(len(files) - 1 for files in duplicates.values())}")

    if duplicates:
        print("\n🔄 DUPLICATE FUNCTION DETAILS:")
        for name, files in sorted(duplicates.items()):
            print(f"\n📍 {name} ({len(files)} copies):")
            for i, file_path in enumerate(files, 1):
                print(f"  {i}. {file_path}")

    return duplicates


def suggest_fixes(duplicates):
    """Suggest fixes for duplicate test functions"""

    print("\n💡 SUGGESTED FIXES:")
    print("=" * 50)

    high_priority = []

    for name, files in duplicates.items():
        if len(files) > 3:
            high_priority.append((name, files))

        print(f"\n🎯 Fix {name}:")
        for i, file_path in enumerate(files):
            # Suggest renaming based on file location
            parts = Path(file_path).parts
            if "integration" in parts:
                suggestion = f"{name}_integration"
            elif "unit" in parts:
                suggestion = f"{name}_unit"
            elif "api" in parts:
                suggestion = f"{name}_api"
            elif "e2e" in parts:
                suggestion = f"{name}_e2e"
            else:
                # Use filename as suffix
                filename = Path(file_path).stem
                suggestion = f"{name}_{filename.replace('test_', '')}"

            if i > 0:  # Keep first occurrence as-is
                print(f"  📝 Rename in {file_path}")
                print(f"      {name} → {suggestion}")

    if high_priority:
        print("\n🚨 HIGH PRIORITY (3+ duplicates):")
        for name, files in high_priority:
            print(f"  • {name}: {len(files)} copies")


def create_cleanup_script():
    """Create a script to help with manual cleanup"""

    script_content = '''#!/usr/bin/env python3
"""
Semi-Automated Test Duplicate Cleanup
Run this after manual review to clean up obvious duplicates
"""

import re
import os

# Files to check for obvious duplicates that can be auto-fixed
AUTO_FIX_PATTERNS = [
    # Pattern: (filename_pattern, old_name, new_name)
    ("integration/test_api_endpoints.py", "test_client", "test_client_api_endpoints"),
    ("integration/test_api_basic.py", "test_client", "test_client_api_basic"),
    ("test_content_protection_isolated.py", "test_tier_limits_structure", "test_tier_limits_structure_isolated"),
    ("test_content_protection_isolated.py", "test_tier_progression", "test_tier_progression_isolated"),
]

def apply_auto_fixes():
    """Apply safe automatic fixes"""
    
    for filename_pattern, old_name, new_name in AUTO_FIX_PATTERNS:
        for root, dirs, files in os.walk('tests/'):
            for file in files:
                file_path = os.path.join(root, file)
                if filename_pattern in file_path and file.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Replace function definition
                        pattern = f"def {old_name}("
                        replacement = f"def {new_name}("
                        
                        if pattern in content:
                            new_content = content.replace(pattern, replacement)
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"✅ Fixed {old_name} → {new_name} in {file_path}")
                            
                    except Exception as e:
                        print(f"❌ Error fixing {file_path}: {e}")

if __name__ == "__main__":
    print("🔧 APPLYING AUTOMATIC DUPLICATE FIXES")
    apply_auto_fixes()
    print("✅ Auto-fixes complete. Run test analysis again to verify.")
'''

    with open("scripts/cleanup_duplicates.py", "w", encoding="utf-8") as f:
        f.write(script_content)

    os.chmod("scripts/cleanup_duplicates.py", 0o755)
    print("\n📄 Created cleanup script: scripts/cleanup_duplicates.py")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent.parent)  # Go to project root
    duplicates = analyze_test_duplicates()
    suggest_fixes(duplicates)
    create_cleanup_script()

    print("\n✅ NEXT STEPS:")
    print("1. Review duplicate suggestions above")
    print("2. Run: python scripts/cleanup_duplicates.py")
    print("3. Run tests to verify: pytest tests/ --no-cov -x")
