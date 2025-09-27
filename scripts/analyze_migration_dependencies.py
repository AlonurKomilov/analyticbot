#!/usr/bin/env python3
"""
Migration Dependency Analysis Script
Analyzes current core/apps/infra dependencies to plan migration to src/ architecture
"""

import ast
import json
from collections import defaultdict
from pathlib import Path


class MigrationAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(set)
        self.file_imports = {}
        self.circular_deps = []

    def analyze_project(self):
        """Analyze entire project for migration planning"""
        print("🔍 Analyzing project for migration planning...")

        # Analyze each directory
        for directory in ["core", "apps", "infra"]:
            if (self.project_root / directory).exists():
                self._analyze_directory(directory)

        # Find circular dependencies
        self._find_circular_dependencies()

        # Generate migration report
        return self._generate_report()

    def _analyze_directory(self, directory):
        """Analyze imports in a directory"""
        dir_path = self.project_root / directory

        for py_file in dir_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                file_key = str(py_file.relative_to(self.project_root))
                self.file_imports[file_key] = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._record_import(file_key, alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._record_import(file_key, node.module)

            except Exception as e:
                print(f"⚠️ Could not analyze {py_file}: {e}")

    def _record_import(self, file_key, module_name):
        """Record an import relationship"""
        # Check if it's a core/apps/infra import
        if any(module_name.startswith(prefix) for prefix in ["core", "apps", "infra"]):
            self.file_imports[file_key].append(module_name)

            # Extract source and target layers
            source_layer = file_key.split("/")[0]
            target_layer = module_name.split(".")[0]

            if source_layer != target_layer:
                self.dependencies[source_layer].add(target_layer)

    def _find_circular_dependencies(self):
        """Find circular dependencies between layers"""
        for layer in self.dependencies:
            for dep_layer in self.dependencies[layer]:
                if layer in self.dependencies.get(dep_layer, set()):
                    self.circular_deps.append((layer, dep_layer))

    def _generate_report(self):
        """Generate migration analysis report"""
        report = {
            "total_files_analyzed": len(self.file_imports),
            "layer_dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "circular_dependencies": self.circular_deps,
            "migration_priority": self._calculate_migration_priority(),
            "proposed_mapping": self._propose_src_mapping(),
        }

        return report

    def _calculate_migration_priority(self):
        """Calculate which components should be migrated first"""
        # Components with fewer dependencies should be migrated first
        priority = {}

        for file_key, imports in self.file_imports.items():
            external_deps = len(
                [imp for imp in imports if not imp.startswith(file_key.split("/")[0])]
            )
            priority[file_key] = external_deps

        # Sort by dependency count (ascending)
        return sorted(priority.items(), key=lambda x: x[1])

    def _propose_src_mapping(self):
        """Propose how current files should map to src/ structure"""
        mapping = {
            "core/models/": "src/shared_kernel/domain/entities/",
            "core/services/analytics_*": "src/analytics/application/services/",
            "core/services/payment_*": "src/payments/application/services/",
            "core/services/user_*": "src/identity/application/services/",
            "core/repositories/": "src/*/domain/repositories/",
            "core/security_engine/": "src/security/",
            "core/ports/": "src/shared_kernel/domain/ports/",
            "infra/db/repositories/": "src/*/infrastructure/persistence/",
            "infra/cache/": "src/shared_kernel/infrastructure/cache/",
            "infra/email/": "src/shared_kernel/infrastructure/email/",
            "infra/monitoring/": "src/shared_kernel/infrastructure/monitoring/",
            "apps/api/": "src/api_service/presentation/",
            "apps/bot/": "src/bot_service/presentation/",
        }
        return mapping


def main():
    """Main analysis function"""
    analyzer = MigrationAnalyzer(".")
    report = analyzer.analyze_project()

    print("\n📊 MIGRATION ANALYSIS REPORT")
    print("=" * 50)
    print(f"Total files analyzed: {report['total_files_analyzed']}")
    print(f"Layer dependencies: {report['layer_dependencies']}")
    print(f"Circular dependencies: {report['circular_dependencies']}")

    # Save detailed report
    with open("migration_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ Analysis complete! Report saved to migration_analysis.json")

    # Print migration priority
    print("\n🎯 MIGRATION PRIORITY (lowest dependencies first):")
    for file_path, dep_count in report["migration_priority"][:10]:
        print(f"  {dep_count:2d} deps: {file_path}")


if __name__ == "__main__":
    main()
