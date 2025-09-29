#!/usr/bin/env python3
"""
AST-based codemod to update legacy imports to canonical module paths.
Uses libcst for safe AST transformation without regex foot-guns.
"""

import sys
from pathlib import Path

try:
    import libcst as cst
except ImportError:
    print("ERROR: libcst not installed. Install with: pip install libcst")
    sys.exit(1)

# Mapping of old module paths to new canonical paths
MAPPING = {
    # Root bot/ -> apps/bot/
    "bot": "apps.bot",
    "bot.config": "apps.bot.config",
    "bot.handlers": "apps.bot.schedule_handlers",  # handlers.py was merged into schedule_handlers.py
    "bot.api": "apps.bot.api",
    "bot.services": "apps.bot.services",
    "bot.utils": "apps.bot.utils",
    "bot.database": "apps.bot.database",
    "bot.middlewares": "apps.bot.middlewares",
    # Root apis/ -> apps/api/
    "apis": "apps.api",
    "apis.handlers": "apps.api.routers",  # handlers -> routers pattern
    # Moved files from duplication cleanup
    "scripts.translate_comments": "apps.bot.utils.translate_comments",
    "health_app": "apps.bot.utils.health_app",
    # Legacy main -> canonical
    "main": "apps.api.main",  # root main.py -> API main
    # Configuration consolidation
    "bot.config": "config.settings",  # for most cases, some might need apps.bot.config
}

# Prefixes that should be rewritten (for dotted imports)
PREFIX_MAPPING = {
    "bot.": "apps.bot.",
    "apis.": "apps.api.",
}


class ImportRewriter(cst.CSTTransformer):
    """AST transformer to rewrite import statements"""

    def __init__(self):
        self.changes_made = 0

    def _rewrite_module_name(self, module_name: str) -> tuple[str, bool]:
        """Rewrite a module name if it matches mapping. Returns (new_name, changed)"""

        # Direct mapping match
        if module_name in MAPPING:
            return MAPPING[module_name], True

        # Prefix mapping match
        for old_prefix, new_prefix in PREFIX_MAPPING.items():
            if module_name.startswith(old_prefix):
                new_name = module_name.replace(old_prefix, new_prefix, 1)
                return new_name, True

        return module_name, False

    def _create_attribute_from_dotted_name(self, name: str) -> cst.Name | cst.Attribute:
        """Create a Name or Attribute node from a dotted module name"""
        parts = name.split(".")
        if len(parts) == 1:
            return cst.Name(parts[0])

        # Build nested attributes: a.b.c -> Attribute(Attribute(Name(a), Name(b)), Name(c))
        result = cst.Name(parts[0])
        for part in parts[1:]:
            result = cst.Attribute(value=result, attr=cst.Name(part))
        return result

    def leave_ImportFrom(
        self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom
    ) -> cst.ImportFrom:
        """Handle 'from module import ...' statements"""

        if not updated_node.module:
            return updated_node

        # Extract the module name
        if isinstance(updated_node.module, cst.Name):
            module_name = updated_node.module.value
        elif isinstance(updated_node.module, cst.Attribute):
            # Handle dotted imports like from bot.config import settings
            module_name = cst.Module([]).code_for_node(updated_node.module).strip()
        else:
            return updated_node

        new_module_name, changed = self._rewrite_module_name(module_name)

        if changed:
            self.changes_made += 1
            print(
                f"  Rewriting: from {module_name} import ... -> from {new_module_name} import ..."
            )
            new_module_node = self._create_attribute_from_dotted_name(new_module_name)
            return updated_node.with_changes(module=new_module_node)

        return updated_node

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """Handle 'import module' statements"""

        if not isinstance(updated_node.names, cst.ImportStar):
            new_names = []
            changed = False

            for import_alias in updated_node.names:
                if isinstance(import_alias.name, cst.Name):
                    old_name = import_alias.name.value
                    new_name, name_changed = self._rewrite_module_name(old_name)

                    if name_changed:
                        self.changes_made += 1
                        print(f"  Rewriting: import {old_name} -> import {new_name}")
                        new_import_name = self._create_attribute_from_dotted_name(new_name)
                        new_names.append(import_alias.with_changes(name=new_import_name))
                        changed = True
                    else:
                        new_names.append(import_alias)
                elif isinstance(import_alias.name, cst.Attribute):
                    # Handle dotted imports like import bot.config
                    old_name = cst.Module([]).code_for_node(import_alias.name).strip()
                    new_name, name_changed = self._rewrite_module_name(old_name)

                    if name_changed:
                        self.changes_made += 1
                        print(f"  Rewriting: import {old_name} -> import {new_name}")
                        new_import_name = self._create_attribute_from_dotted_name(new_name)
                        new_names.append(import_alias.with_changes(name=new_import_name))
                        changed = True
                    else:
                        new_names.append(import_alias)
                else:
                    new_names.append(import_alias)

            if changed:
                return updated_node.with_changes(names=new_names)

        return updated_node


def rewrite_file(file_path: Path) -> bool:
    """Rewrite imports in a single file. Returns True if changes were made."""
    try:
        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()

        # Parse and transform
        tree = cst.parse_module(source_code)
        transformer = ImportRewriter()
        new_tree = tree.visit(transformer)

        if transformer.changes_made > 0:
            print(f"📝 {file_path}: {transformer.changes_made} import(s) updated")

            # Write back the transformed code
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_tree.code)

            return True

        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        # Process specific files passed as arguments
        files_to_process = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Find all Python files excluding archive and .venv
        root = Path(".")
        files_to_process = []

        for pattern in ["**/*.py"]:
            for file_path in root.glob(pattern):
                # Skip archive, .venv, node_modules, git, and other build directories
                path_parts = file_path.parts
                if any(
                    exclude in path_parts
                    for exclude in [
                        "archive",
                        ".venv",
                        "node_modules",
                        "__pycache__",
                        ".git",
                    ]
                ):
                    continue
                files_to_process.append(file_path)

    print(f"🔍 Found {len(files_to_process)} Python files to check")

    files_changed = 0

    for file_path in sorted(files_to_process):
        if rewrite_file(file_path):
            files_changed += 1

    print("\n✅ Processing complete:")
    print(f"   📁 Files checked: {len(files_to_process)}")
    print(f"   📝 Files changed: {files_changed}")
    print("\n🎯 Import canonicalization complete!")

    if files_changed > 0:
        print("\nNext steps:")
        print("1. Review changes: git diff")
        print("2. Test imports: python -m pytest --collect-only")
        print(
            "3. Commit: git add . && git commit -m 'refactor(imports): AST codemod to canonical module paths'"
        )


if __name__ == "__main__":
    main()
