#!/usr/bin/env python3
"""
CI guard: detect exact/structural duplicate python modules/functions in prod code.
Scans only apps/, core/, infra/ (excludes tests and docs/_archive).
Fails if any structural module duplicates are found across different files.
"""

import ast
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "apps", ROOT / "core", ROOT / "infra"]


def canon_module_dump(src: str) -> str:
    """Canonicalize AST to detect structural duplicates regardless of names/constants"""

    class C(ast.NodeTransformer):
        def visit_Name(self, n):
            n.id = "v"
            return n

        def visit_arg(self, n):
            n.arg = "v"
            n.annotation = None
            return n

        def visit_Attribute(self, n):
            self.generic_visit(n)
            n.attr = "a"
            return n

        def visit_Constant(self, n):
            v = n.value
            if isinstance(v, str):
                n.value = "STR"
            elif isinstance(v, (int, float, complex)):
                n.value = 0
            elif isinstance(v, bytes):
                n.value = b"B"
            elif isinstance(v, bool):
                n.value = bool(v)
            else:
                n.value = "CONST"
            return n

        def visit_FunctionDef(self, n):
            n.name = "FUNC"
            n.decorator_list = []
            self.generic_visit(n)
            return n

        def visit_AsyncFunctionDef(self, n):
            n.name = "AFUNC"
            n.decorator_list = []
            self.generic_visit(n)
            return n

        def visit_ClassDef(self, n):
            n.name = "CLASS"
            n.decorator_list = []
            self.generic_visit(n)
            return n

    try:
        tree = ast.parse(src)
    except Exception:
        return ""

    tree = C().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.dump(tree, include_attributes=False)


def sha1(s: str) -> str:
    """Generate SHA1 hash of string"""
    h = hashlib.sha1()
    h.update(s.encode())
    return h.hexdigest()


def main():
    """Main duplicate detection logic"""
    py_files = []

    # Collect all Python files from production directories
    for d in SCAN_DIRS:
        if d.exists():
            for f in d.rglob("*.py"):
                # Skip test files and any files with 'test' in path
                if "test" in f.parts or f.name.startswith("test_"):
                    continue
                py_files.append(f)

    print(f"Scanning {len(py_files)} Python files in production directories...")

    modmap = {}
    clashes = []

    # Process each file and detect structural duplicates
    for f in py_files:
        try:
            src = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Skip empty files and empty __init__.py files (legitimate package markers)
        if not src.strip():
            continue

        # Skip minimal __init__.py files that are just package markers
        if f.name == "__init__.py" and len(src.strip()) < 100:
            continue

        dump = canon_module_dump(src)
        if not dump:
            continue

        h = sha1(dump)

        if h in modmap and modmap[h] != f:
            clashes.append((str(modmap[h].relative_to(ROOT)), str(f.relative_to(ROOT))))
        else:
            modmap[h] = f

    if clashes:
        print("❌ Duplicate structural modules detected in prod code:")
        for a, b in clashes[:50]:  # Limit output to first 50 clashes
            print(f"   - {a} <=> {b}")
        if len(clashes) > 50:
            print(f"   ... and {len(clashes) - 50} more duplicates")
        print("\nStructural duplicates found! Please consolidate duplicate code.")
        sys.exit(1)

    print("✅ dup_guard: OK - No structural duplicates found in production code")


if __name__ == "__main__":
    main()
