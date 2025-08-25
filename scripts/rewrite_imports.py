#!/usr/bin/env python3
"""
AST-based codemod to update imports for canonical architecture.

Updates imports:
- from bot.* -> from apps.bot.*
- from apis.* -> from apps.api.*
- from security.* -> from core.security_engine.*
- alembic path updates
"""

import ast
from pathlib import Path


class ImportRewriter(ast.NodeTransformer):
    """AST transformer to rewrite import statements"""

    def __init__(self):
        self.changes = []

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """Rewrite import statements like: import bot.handlers"""
        new_names = []
        for alias in node.names:
            old_name = alias.name
            new_name = self._rewrite_module_name(old_name)
            if new_name != old_name:
                self.changes.append((old_name, new_name))
                alias.name = new_name
            new_names.append(alias)
        node.names = new_names
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Rewrite from imports like: from bot.handlers import something"""
        if node.module:
            old_module = node.module
            new_module = self._rewrite_module_name(old_module)
            if new_module != old_module:
                self.changes.append((old_module, new_module))
                node.module = new_module
        return node

    def _rewrite_module_name(self, module_name: str) -> str:
        """Rewrite a single module name according to our rules"""
        # Bot imports: bot.* -> apps.bot.*
        if module_name.startswith("bot.") or module_name == "bot":
            if module_name == "bot":
                return "apps.bot"
            return module_name.replace("bot.", "apps.bot.", 1)

        # API imports: apis.* -> apps.api.*
        if module_name.startswith("apis.") or module_name == "apis":
            if module_name == "apis":
                return "apps.api"
            return module_name.replace("apis.", "apps.api.", 1)

        # Security imports: security.* -> core.security_engine.*
        if module_name.startswith("security.") or module_name == "security":
            if module_name == "security":
                return "core.security_engine"
            return module_name.replace("security.", "core.security_engine.", 1)

        return module_name


def rewrite_file(file_path: Path) -> list[tuple[str, str]]:
    """Rewrite imports in a single file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"⚠️ Syntax error in {file_path}, skipping")
            return []

        rewriter = ImportRewriter()
        new_tree = rewriter.visit(tree)

        if rewriter.changes:
            # Convert back to source code
            import astor

            new_content = astor.to_source(new_tree)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"✅ Updated {file_path}")
            for old, new in rewriter.changes:
                print(f"   {old} -> {new}")

        return rewriter.changes

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return []


def find_python_files(root_path: Path) -> list[Path]:
    """Find all Python files to process"""
    python_files = []

    # Directories to process
    dirs_to_check = [
        "apps",
        "core",
        "scripts",
        "tests",
        "config",
        "infra",
        "archive",  # include archive for reference
    ]

    # Also check root level .py files
    for file_path in root_path.glob("*.py"):
        if file_path.is_file():
            python_files.append(file_path)

    # Check subdirectories
    for dir_name in dirs_to_check:
        dir_path = root_path / dir_name
        if dir_path.exists():
            python_files.extend(dir_path.glob("**/*.py"))

    return python_files


def main():
    """Main function"""
    root = Path("/workspaces/analyticbot")

    print("🔄 Starting import rewrite for canonical architecture...")

    # Check if astor is available
    try:
        import astor
    except ImportError:
        print("❌ astor library not found. Install with: pip install astor")
        return

    python_files = find_python_files(root)
    print(f"📁 Found {len(python_files)} Python files to check")

    total_changes = 0
    for file_path in python_files:
        changes = rewrite_file(file_path)
        total_changes += len(changes)

    print(f"\n✅ Import rewrite complete! Made {total_changes} changes.")


if __name__ == "__main__":
    main()
