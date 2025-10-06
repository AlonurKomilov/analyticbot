#!/usr/bin/env python3
"""
Security Issues Fix Script
Identifies and helps fix security vulnerabilities
"""

import re
from pathlib import Path


def scan_for_hardcoded_secrets():
    """Scan for potential hardcoded secrets"""
    project_root = Path(__file__).parent.parent
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']{3,}["\']',
        r'secret\s*=\s*["\'][^"\']{3,}["\']',
        r'token\s*=\s*["\'][^"\']{10,}["\']',
        r'api_key\s*=\s*["\'][^"\']{10,}["\']',
    ]

    issues = []
    for py_file in project_root.rglob("*.py"):
        if ".venv" in str(py_file) or "archive" in str(py_file):
            continue

        try:
            with open(py_file) as f:
                content = f.read()

            for pattern in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append(
                        {
                            "file": str(py_file),
                            "line": content[: match.start()].count("\n") + 1,
                            "match": match.group(),
                        }
                    )
        except Exception:
            continue

    return issues


def main():
    print("🔒 Security Audit Results:")
    print("=" * 40)

    issues = scan_for_hardcoded_secrets()

    if issues:
        print(f"⚠️ Found {len(issues)} potential security issues:")
        for issue in issues:
            print(f"  📁 {issue['file']}:{issue['line']}")
            print(f"     {issue['match']}")
            print()
    else:
        print("✅ No obvious hardcoded secrets found")

    print("\n🔧 Recommendations:")
    print("- Use environment variables for all secrets")
    print("- Use SecretStr type for sensitive data")
    print("- Review .env files for real secrets")


if __name__ == "__main__":
    main()
