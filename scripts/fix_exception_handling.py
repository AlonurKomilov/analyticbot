#!/usr/bin/env python3
"""
Exception Handling Fix Script
Finds and reports unsafe exception handling patterns
"""

import re
from pathlib import Path


def find_unsafe_exception_handling():
    """Find unsafe exception handling patterns"""
    project_root = Path(__file__).parent.parent

    # Patterns to find
    unsafe_patterns = [
        r"except\s+Exception\s*:\s*pass",
        r"except\s*:\s*pass",
        r"except\s+.*\s*:\s*pass",
    ]

    issues = []
    for py_file in project_root.rglob("*.py"):
        if ".venv" in str(py_file) or "archive" in str(py_file):
            continue

        try:
            with open(py_file) as f:
                content = f.read()

            for pattern in unsafe_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    issues.append(
                        {
                            "file": str(py_file),
                            "line": line_num,
                            "pattern": match.group(),
                        }
                    )
        except Exception:
            continue

    return issues


def main():
    print("🚨 Exception Handling Audit:")
    print("=" * 40)

    issues = find_unsafe_exception_handling()

    if issues:
        print(f"⚠️ Found {len(issues)} unsafe exception handling patterns:")
        for issue in issues:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     {issue['pattern']}")
            print()
    else:
        print("✅ No unsafe exception handling found")

    print("\n🔧 Recommendations:")
    print("- Replace 'except Exception: pass' with proper logging")
    print("- Use specific exception types when possible")
    print("- Always log errors for debugging")


if __name__ == "__main__":
    main()
