#!/usr/bin/env python3
"""
Quick Coverage Checker
Created: Oct 20, 2025
Purpose: Check if coverage meets minimum thresholds
"""

import json
import sys
from pathlib import Path

# Coverage thresholds
THRESHOLDS = {
    "overall": 15.0,  # Minimum overall coverage
    "critical": {
        "apps/api/middleware/auth.py": 30.0,
        "apps/api/auth_utils.py": 50.0,
        "core/security_engine/": 40.0,
    },
}


def check_coverage():
    """Check coverage against thresholds."""
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("❌ coverage.json not found. Run tests with coverage first.")
        return False

    with open(coverage_file) as f:
        data = json.load(f)

    total = data["totals"]
    overall_percent = total["percent_covered"]

    print(f"📊 Overall Coverage: {overall_percent:.2f}%")
    print(f"   Minimum Required: {THRESHOLDS['overall']:.2f}%")

    success = True

    # Check overall threshold
    if overall_percent < THRESHOLDS["overall"]:
        print("❌ Overall coverage below threshold!")
        success = False
    else:
        print("✅ Overall coverage meets threshold!")

    print()

    # Check critical files
    print("🔍 Critical Files Check:")
    for pattern, min_cov in THRESHOLDS["critical"].items():
        matching_files = []
        for file_path, stats in data["files"].items():
            if pattern in file_path:
                matching_files.append((file_path, stats["summary"]["percent_covered"]))

        if matching_files:
            for file_path, cov in matching_files:
                short_path = file_path.split("/")[-3:]
                short_path = "/".join(short_path)
                if cov < min_cov:
                    print(f"   ❌ {short_path}: {cov:.2f}% (min: {min_cov:.2f}%)")
                    success = False
                else:
                    print(f"   ✅ {short_path}: {cov:.2f}%")

    print()

    if success:
        print("✅ All coverage checks passed!")
        return True
    else:
        print("❌ Some coverage checks failed!")
        return False


if __name__ == "__main__":
    success = check_coverage()
    sys.exit(0 if success else 1)
