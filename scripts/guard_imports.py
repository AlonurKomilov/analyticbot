"""
Import Guard Script
Forbids core -> apps/infra imports to maintain Clean Architecture principles
"""

import sys
import ast
import pathlib
from typing import List


ROOT = pathlib.Path(".").resolve()
CORE = ROOT / "core"
FORBIDDEN_IMPORTS = ("apps", "infra", "infrastructure")


def scan_file(file: pathlib.Path) -> List[str]:
    """Scan a Python file for forbidden imports"""
    violations = []
    
    try:
        content = file.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file}: {e}")
        return violations
    
    for node in ast.walk(tree):
        forbidden_module = None
        
        # Check "from module import ..."
        if isinstance(node, ast.ImportFrom) and node.module:
            module = node.module
            if any(module.startswith(prefix) for prefix in FORBIDDEN_IMPORTS):
                forbidden_module = module
        
        # Check "import module"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if any(module.startswith(prefix) for prefix in FORBIDDEN_IMPORTS):
                    forbidden_module = module
        
        if forbidden_module:
            rel_path = file.relative_to(ROOT).as_posix()
            violations.append(f"{rel_path}: forbidden import -> {forbidden_module}")
    
    return violations


def main():
    """Main entry point"""
    if not CORE.exists():
        print("No core/ directory found, skipping import guard check")
        return 0
    
    all_violations = []
    
    # Scan all Python files in core/
    for py_file in CORE.rglob("*.py"):
        violations = scan_file(py_file)
        all_violations.extend(violations)
    
    if all_violations:
        print("🚨 CLEAN ARCHITECTURE VIOLATION DETECTED! 🚨")
        print("\nForbidden core imports found:")
        for violation in all_violations:
            print(f"  ❌ {violation}")
        
        print(f"\n📋 Clean Architecture Rules:")
        print(f"  ✅ core/ can import: standard library, core modules")
        print(f"  ❌ core/ cannot import: apps/, infra/, infrastructure/")
        print(f"  ✅ apps/ can import: core/, standard library")
        print(f"  ✅ infra/ can import: core/, standard library, external libraries")
        
        return 1
    
    print("✅ Clean Architecture import rules satisfied!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
