#!/usr/bin/env python3
"""
Shared Kernel Audit - Check for components that could be separate modules
"""

import os
from collections import defaultdict
from pathlib import Path


def audit_shared_kernel_for_extraction():
    """Analyze shared_kernel to find components that could be separate modules"""

    print("🔍 SHARED KERNEL EXTRACTION AUDIT")
    print("=" * 60)
    print("🎯 Goal: Find components in shared_kernel that could be independent modules")
    print()

    shared_path = Path("src/shared_kernel")
    if not shared_path.exists():
        print("❌ shared_kernel not found!")
        return

    # Analyze shared_kernel structure
    print("📊 CURRENT SHARED_KERNEL STRUCTURE:")

    components = defaultdict(dict)

    for layer in ["domain", "application", "infrastructure"]:
        layer_path = shared_path / layer
        if layer_path.exists():
            print(f"\n📂 {layer}/:")

            for item in sorted(os.listdir(layer_path)):
                item_path = layer_path / item

                if item_path.is_dir() and item != "__pycache__":
                    file_count = len(
                        [f for f in item_path.rglob("*.py") if f.name != "__init__.py"]
                    )
                    files = [f.name for f in item_path.glob("*.py") if f.name != "__init__.py"]

                    components[layer][item] = {
                        "file_count": file_count,
                        "files": files,
                        "path": str(item_path),
                    }

                    print(f"   📁 {item}/: {file_count} files")
                    if files:
                        print(f"      Files: {', '.join(files[:3])}")
                        if len(files) > 3:
                            print(f"      ... and {len(files) - 3} more")

                elif item.endswith(".py") and item != "__init__.py":
                    components[layer][item] = {
                        "file_count": 1,
                        "files": [item],
                        "path": str(item_path),
                        "is_file": True,
                    }
                    print(f"   📄 {item}")

    # Analyze potential extractions
    print("\n🔍 EXTRACTION ANALYSIS:")
    print("Checking for components that could be independent modules...")

    extraction_candidates = []

    # Check each domain component
    domain_components = components.get("domain", {})

    for component_name, info in domain_components.items():
        if info["file_count"] > 2:  # Substantial component
            # Check if this could be a business domain
            business_domains = [
                "notifications",
                "notification",
                "messaging",
                "alerts",
                "reporting",
                "reports",
                "dashboard",
                "monitoring",
                "metrics",
                "observability",
                "workflows",
                "automation",
                "jobs",
                "content",
                "media",
                "files",
                "integration",
                "webhook",
                "api",
                "search",
                "indexing",
                "elasticsearch",
                "backup",
                "storage",
                "archiving",
            ]

            if any(domain in component_name.lower() for domain in business_domains):
                extraction_candidates.append(
                    {
                        "name": component_name,
                        "current_layer": "domain",
                        "file_count": info["file_count"],
                        "reason": "Potential business domain",
                        "suggested_module": f"src/{component_name.lower().replace('_', '_')}/",
                        "files": info["files"],
                    }
                )

    # Check application services
    app_components = components.get("application", {})

    for component_name, info in app_components.items():
        if info["file_count"] > 1:
            # Check for service-like components
            service_patterns = [
                "notification",
                "alert",
                "email",
                "sms",
                "report",
                "dashboard",
                "export",
                "job",
                "task",
                "worker",
                "scheduler",
                "integration",
                "webhook",
                "sync",
                "search",
                "index",
                "query",
            ]

            if any(pattern in component_name.lower() for pattern in service_patterns):
                extraction_candidates.append(
                    {
                        "name": component_name,
                        "current_layer": "application",
                        "file_count": info["file_count"],
                        "reason": "Substantial application service",
                        "suggested_module": f"src/{component_name.lower().replace('_services', '').replace('_service', '')}/",
                        "files": info["files"],
                    }
                )

    # Check infrastructure components
    infra_components = components.get("infrastructure", {})

    for component_name, info in infra_components.items():
        if info["file_count"] > 2:
            # Check for infrastructure that could be a module
            infra_patterns = [
                "email",
                "sms",
                "messaging",
                "storage",
                "file",
                "media",
                "search",
                "elasticsearch",
                "solr",
                "queue",
                "message",
                "kafka",
                "backup",
                "archiving",
                "sync",
            ]

            if any(pattern in component_name.lower() for pattern in infra_patterns):
                extraction_candidates.append(
                    {
                        "name": component_name,
                        "current_layer": "infrastructure",
                        "file_count": info["file_count"],
                        "reason": "Substantial infrastructure concern",
                        "suggested_module": f"src/{component_name.lower()}/",
                        "files": info["files"],
                    }
                )

    # Report findings
    if extraction_candidates:
        print("\n✨ EXTRACTION CANDIDATES FOUND:")

        for i, candidate in enumerate(extraction_candidates, 1):
            print(f"\n{i}. {candidate['name']} ({candidate['current_layer']})")
            print(f"   📊 Size: {candidate['file_count']} files")
            print(f"   🎯 Reason: {candidate['reason']}")
            print(f"   📁 Suggested: {candidate['suggested_module']}")
            print(f"   📄 Files: {', '.join(candidate['files'][:3])}")
            if len(candidate["files"]) > 3:
                print(f"        ... and {len(candidate['files']) - 3} more")

            # Suggest module structure
            candidate["suggested_module"].split("/")[-2]
            print("   🏗️  Module structure:")
            print(f"      {candidate['suggested_module']}")
            print("      ├── domain/")
            print("      ├── application/")
            print("      ├── infrastructure/")
            print("      └── presentation/")

    else:
        print("   ✅ No obvious extraction candidates found")
        print("   📝 Current shared_kernel components appear to be truly shared")

    # Check for components that should stay shared
    print("\n✅ COMPONENTS THAT SHOULD STAY IN SHARED_KERNEL:")

    core_shared = [
        "base_entity",
        "domain_events",
        "value_objects",
        "di",
        "cache",
        "database",
        "persistence",
        "common",
        "utilities",
        "helpers",
        "protocols",
        "interfaces",
        "contracts",
    ]

    staying_components = []
    for layer, layer_components in components.items():
        for comp_name, info in layer_components.items():
            if any(core in comp_name.lower() for core in core_shared):
                staying_components.append(f"{layer}/{comp_name}")

    if staying_components:
        for comp in staying_components:
            print(f"   • {comp} - Core shared infrastructure")

    # Final recommendations
    print("\n💡 FINAL RECOMMENDATIONS:")

    recommendations = []

    if extraction_candidates:
        recommendations.append(
            f"Consider extracting {len(extraction_candidates)} components as independent modules"
        )
        recommendations.append(
            "Each extracted module should have full domain/application/infrastructure/presentation layers"
        )
        recommendations.append(
            "Extracted modules should only depend on shared_kernel, not each other"
        )

    recommendations.extend(
        [
            "Keep core infrastructure (DI, cache, database) in shared_kernel",
            "Keep shared domain concepts (base entities, events) in shared_kernel",
            "Ensure extracted modules follow the same independence rules as existing modules",
            "Test each extracted module can work independently",
        ]
    )

    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")

    return extraction_candidates


if __name__ == "__main__":
    candidates = audit_shared_kernel_for_extraction()

    if candidates:
        print("\n🎯 EXTRACTION PLAN SUMMARY:")
        print(f"   📦 {len(candidates)} components could become independent modules")
        print("   🏗️  This would create a cleaner, more modular architecture")
        print("   ⚡ Each new module would be independently deployable and testable")
    else:
        print("\n✅ SHARED_KERNEL IS OPTIMAL:")
        print("   📦 All components appear to be truly shared infrastructure")
        print("   🏗️  Current structure supports the Module Monolith pattern well")
