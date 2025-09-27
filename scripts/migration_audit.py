#!/usr/bin/env python3
"""
Migration Audit - Check what was missed and verify architecture pattern
"""

import os
from collections import defaultdict
from pathlib import Path


def audit_migration():
    """Comprehensive audit of migration completeness"""

    print("🔍 MIGRATION AUDIT - COMPREHENSIVE ANALYSIS")
    print("=" * 70)

    # Check old locations
    old_locations = ["core", "apps", "infra"]
    remaining_files = defaultdict(list)

    for location in old_locations:
        if os.path.exists(location):
            for root, dirs, files in os.walk(location):
                for file in files:
                    if file.endswith(".py"):
                        file_path = Path(root) / file
                        remaining_files[location].append(str(file_path))

    print("📊 REMAINING FILES IN OLD LOCATIONS:")
    total_remaining = 0
    for location, files in remaining_files.items():
        print(f"\n📁 {location.upper()}/ - {len(files)} files:")
        total_remaining += len(files)
        for file in sorted(files)[:10]:  # Show first 10
            print(f"   • {file}")
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more files")

    print(f"\n⚠️  TOTAL REMAINING FILES: {total_remaining}")

    # Check src/ structure
    print("\n🏗️  CURRENT src/ STRUCTURE:")
    if os.path.exists("src"):
        for item in sorted(os.listdir("src")):
            if os.path.isdir(f"src/{item}"):
                substructure = []
                if os.path.exists(f"src/{item}"):
                    for subitem in sorted(os.listdir(f"src/{item}")):
                        if os.path.isdir(f"src/{item}/{subitem}"):
                            substructure.append(subitem)

                print(f"   📂 {item}/")
                if substructure:
                    print(f"      └── {', '.join(substructure[:5])}")

    # Identify architecture pattern
    print("\n🏛️  ARCHITECTURE PATTERN ANALYSIS:")

    # Check if modules have domain/application/infrastructure layers
    module_pattern = []
    if os.path.exists("src"):
        for module in os.listdir("src"):
            module_path = Path("src") / module
            if module_path.is_dir() and not module.startswith("_"):
                layers = []
                for layer in [
                    "domain",
                    "application",
                    "infrastructure",
                    "presentation",
                ]:
                    if (module_path / layer).exists():
                        layers.append(layer)
                if layers:
                    module_pattern.append((module, layers))

    if module_pattern:
        print("   🎯 Pattern: MODULE MONOLITH (each module has own layers)")
        for module, layers in module_pattern[:5]:
            print(f"      • {module}: {', '.join(layers)}")

    # Critical analysis
    print("\n❗ CRITICAL MIGRATION ISSUES:")

    issues = []

    # Check if core files are still being used
    if remaining_files.get("core"):
        issues.append(
            f"• {len(remaining_files['core'])} files still in core/ - may cause import conflicts"
        )

    if remaining_files.get("infra"):
        issues.append(
            f"• {len(remaining_files['infra'])} files still in infra/ - database/cache logic not migrated"
        )

    if remaining_files.get("apps"):
        issues.append(
            f"• {len(remaining_files['apps'])} files still in apps/ - service logic not migrated"
        )

    # Check for legacy patterns
    if os.path.exists("core/di_container.py"):
        issues.append(
            "• DI Container still in core/ - should be in src/shared/ or src/infrastructure/"
        )

    if os.path.exists("core/protocols.py"):
        issues.append("• Service protocols still in core/ - should be in domain layers")

    for issue in issues:
        print(f"   {issue}")

    if not issues:
        print("   ✅ No critical issues found")

    print("\n🎯 RECOMMENDATIONS:")
    recommendations = [
        "1. Move core/protocols.py to src/shared_kernel/domain/protocols/",
        "2. Move core/di_container.py to src/shared_kernel/infrastructure/di/",
        "3. Migrate remaining infra/db/ repositories to appropriate modules",
        "4. Create src/legacy/ for deprecated but still needed files",
        "5. Update all imports to use new module monolith structure",
        "6. Consider creating src/common/ for shared utilities",
    ]

    for rec in recommendations:
        print(f"   {rec}")


if __name__ == "__main__":
    audit_migration()
