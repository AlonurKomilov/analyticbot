#!/usr/bin/env python3
"""
Module Dependency Audit - Check for inter-module dependencies
"""

import os
from collections import defaultdict
from pathlib import Path


def audit_module_dependencies():
    """Audit all modules for cross-dependencies and violations"""

    print("🔍 MODULE DEPENDENCY AUDIT")
    print("=" * 60)
    print("🎯 Rule: Modules should only depend on shared_kernel, NOT other modules")
    print()

    # Get all modules
    src_path = Path("src")
    modules = [d.name for d in src_path.iterdir() if d.is_dir() and not d.name.startswith("_")]
    modules.remove("shared_kernel")  # shared_kernel is allowed dependency

    print(f"📂 Modules found: {', '.join(modules)}")
    print()

    # Analyze dependencies
    violations = defaultdict(list)
    allowed_deps = defaultdict(list)

    for module_name in modules:
        module_path = src_path / module_name
        print(f"🔍 Analyzing {module_name}/...")

        # Find all Python files in this module
        py_files = list(module_path.rglob("*.py"))

        for py_file in py_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Look for imports from other modules
                for other_module in modules:
                    if other_module != module_name:
                        # Check for direct module imports
                        patterns = [
                            f"from src.{other_module}",
                            f"import src.{other_module}",
                            f"from {other_module}",  # relative import
                        ]

                        for pattern in patterns:
                            if pattern in content:
                                rel_path = py_file.relative_to(module_path)
                                violations[module_name].append(
                                    {
                                        "file": str(rel_path),
                                        "depends_on": other_module,
                                        "pattern": pattern,
                                    }
                                )

                # Check for shared_kernel imports (these are allowed)
                shared_patterns = ["from src.shared_kernel", "import src.shared_kernel"]

                for pattern in shared_patterns:
                    if pattern in content:
                        allowed_deps[module_name].append(str(py_file.relative_to(module_path)))
                        break

            except Exception as e:
                print(f"   ⚠️  Error reading {py_file}: {e}")

    # Report violations
    print("\n❌ MODULE DEPENDENCY VIOLATIONS:")
    total_violations = 0

    if violations:
        for module, deps in violations.items():
            print(f"\n📂 {module}/ has {len(deps)} violations:")
            for dep in deps[:5]:  # Show first 5
                print(f"   • {dep['file']} → depends on {dep['depends_on']}")
                print(f"     Pattern: {dep['pattern']}")
            if len(deps) > 5:
                print(f"   ... and {len(deps) - 5} more violations")
            total_violations += len(deps)
    else:
        print("   ✅ No direct module-to-module dependencies found!")

    # Report allowed dependencies
    print("\n✅ ALLOWED DEPENDENCIES (shared_kernel):")
    for module, files in allowed_deps.items():
        if files:
            print(f"   • {module}/ → shared_kernel ({len(set(files))} files)")

    # Check shared_kernel dependencies (should not depend on modules)
    print("\n🔍 SHARED_KERNEL DEPENDENCY CHECK:")
    shared_violations = []
    shared_path = src_path / "shared_kernel"

    if shared_path.exists():
        for py_file in shared_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for module in modules:
                    if f"from src.{module}" in content or f"import src.{module}" in content:
                        shared_violations.append(
                            {
                                "file": str(py_file.relative_to(shared_path)),
                                "depends_on": module,
                            }
                        )
            except:
                continue

    if shared_violations:
        print("   ❌ SHARED_KERNEL VIOLATIONS:")
        for violation in shared_violations:
            print(f"      • {violation['file']} → {violation['depends_on']}")
    else:
        print("   ✅ shared_kernel is clean (no module dependencies)")

    # Analyze my migration plan for potential violations
    print("\n🔍 MIGRATION PLAN DEPENDENCY ANALYSIS:")
    print("Checking if my planned repository distributions create violations...")

    migration_analysis = {
        "identity": ["user_repository.py", "admin_repository.py"],
        "analytics": ["analytics_repository.py", "reports_repository.py"],
        "payments": ["payment_repository.py", "subscription_repository.py"],
        "scheduling": ["schedule_repository.py", "delivery_repository.py"],
        "channels": ["channel_repository.py", "telegram_repository.py"],
    }

    # Check if these repositories have cross-dependencies
    repo_violations = []
    for module, repos in migration_analysis.items():
        for repo in repos:
            repo_path = f"infra/db/repositories/{repo}"
            if os.path.exists(repo_path):
                try:
                    with open(repo_path) as f:
                        content = f.read()

                    # Check if this repo imports from other modules
                    for other_module in migration_analysis.keys():
                        if other_module != module:
                            if f"from src.{other_module}" in content:
                                repo_violations.append(f"{repo} → {other_module}")
                except:
                    continue

    if repo_violations:
        print("   ❌ MIGRATION PLAN VIOLATIONS:")
        for violation in repo_violations:
            print(f"      • {violation}")
        print("   💡 Solution: Keep shared repositories in shared_kernel/infrastructure/")
    else:
        print("   ✅ Migration plan looks clean")

    # Final recommendations
    print("\n💡 ARCHITECTURAL RECOMMENDATIONS:")

    recommendations = []

    if total_violations > 0:
        recommendations.append(f"Fix {total_violations} module-to-module dependencies")
        recommendations.append("Move shared logic to shared_kernel instead of cross-module imports")

    if shared_violations:
        recommendations.append("Remove shared_kernel dependencies on specific modules")
        recommendations.append("Use dependency inversion (interfaces) instead of direct imports")

    if repo_violations:
        recommendations.append(
            "Keep shared repositories in shared_kernel, not distributed to modules"
        )
        recommendations.append("Each module should have its own domain-specific repositories only")

    recommendations.extend(
        [
            "Enforce module boundaries with import linting rules",
            "Use events/message bus for inter-module communication",
            "Keep business logic within module boundaries",
        ]
    )

    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    return total_violations == 0 and len(shared_violations) == 0


if __name__ == "__main__":
    audit_module_dependencies()
