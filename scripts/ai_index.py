#!/usr/bin/env python3
import argparse
import ast
import os


def py_files(root="."):
    for base, _, files in os.walk(root):
        if "/.git" in base or "/.venv" in base or "/.tox" in base:
            continue
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(base, f)


def outline(path):
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
        tree = ast.parse(src)
    except Exception:
        return []
    items = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            items.append(f"class {node.name}")
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef):
                    args = [a.arg for a in sub.args.args]
                    items.append(f"  def {sub.name}({', '.join(args)})")
        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            items.append(f"def {node.name}({', '.join(args)})")
        elif isinstance(node, ast.Import):
            items.append("import " + ", ".join([a.name for a in node.names]))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            items.append(
                f"from {mod} import " + ", ".join([a.name for a in node.names])
            )
    return items


def imports(path):
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
        tree = ast.parse(src)
    except Exception:
        return []
    edges = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                edges.append((path, a.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                edges.append((path, node.module))
    return edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--errors-file", default=None)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    with open(
        os.path.join(args.outdir, "project_map.txt"), "w", encoding="utf-8"
    ) as out:
        for f in sorted(py_files(".")):
            rel = os.path.relpath(f, ".")
            out.write(f"# {rel}\n")
            for line in outline(f):
                out.write(line + "\n")
            out.write("\n")

    with open(
        os.path.join(args.outdir, "import_graph.txt"), "w", encoding="utf-8"
    ) as out:
        for f in sorted(py_files(".")):
            for src, mod in imports(f):
                out.write(f"{os.path.relpath(src, '.')} -> {mod}\n")

    # minimal relevant snippets (optional)
    with open(
        os.path.join(args.outdir, "relevant_snippets.txt"), "w", encoding="utf-8"
    ) as out:
        pass


if __name__ == "__main__":
    main()
