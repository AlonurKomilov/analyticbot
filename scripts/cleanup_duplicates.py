#!/usr/bin/env python3
"""
Semi-Automated Test Duplicate Cleanup
Run this after manual review to clean up obvious duplicates
"""

import os

# Files to check for obvious duplicates that can be auto-fixed
AUTO_FIX_PATTERNS = [
    # Pattern: (filename_pattern, old_name, new_name)
    ("integration/test_api_endpoints.py", "test_client", "test_client_api_endpoints"),
    ("integration/test_api_basic.py", "test_client", "test_client_api_basic"),
    (
        "test_content_protection_isolated.py",
        "test_tier_limits_structure",
        "test_tier_limits_structure_isolated",
    ),
    (
        "test_content_protection_isolated.py",
        "test_tier_progression",
        "test_tier_progression_isolated",
    ),
]


def apply_auto_fixes():
    """Apply safe automatic fixes"""

    for filename_pattern, old_name, new_name in AUTO_FIX_PATTERNS:
        for root, dirs, files in os.walk("tests/"):
            for file in files:
                file_path = os.path.join(root, file)
                if filename_pattern in file_path and file.endswith(".py"):
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        # Replace function definition
                        pattern = f"def {old_name}("
                        replacement = f"def {new_name}("

                        if pattern in content:
                            new_content = content.replace(pattern, replacement)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(new_content)
                            print(f"✅ Fixed {old_name} → {new_name} in {file_path}")

                    except Exception as e:
                        print(f"❌ Error fixing {file_path}: {e}")


if __name__ == "__main__":
    print("🔧 APPLYING AUTOMATIC DUPLICATE FIXES")
    apply_auto_fixes()
    print("✅ Auto-fixes complete. Run test analysis again to verify.")
