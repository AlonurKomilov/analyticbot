#!/usr/bin/env python3
"""
Migrate exact duplicates to archive and create compatibility shims.
"""

import csv
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run_git_command(cmd):
    """Run git command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=ROOT, check=True, capture_output=True, text=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def create_compat_shim(redundant_path, canonical_path):
    """Create a compatibility shim for Python files."""
    if not redundant_path.endswith(".py") or redundant_path.endswith("__init__.py"):
        return

    # Convert canonical path to module import
    canonical_module = canonical_path[:-3].replace("/", ".")

    shim_content = f"""# AUTO-GENERATED COMPAT SHIM — redirects to canonical module
from {canonical_module} import *  # noqa: F401,F403
"""

    # Create the shim file
    shim_path = ROOT / redundant_path
    shim_path.parent.mkdir(parents=True, exist_ok=True)

    with open(shim_path, "w") as f:
        f.write(shim_content)

    print(f"  → Created compat shim: {redundant_path} → {canonical_module}")


def migrate_duplicates():
    """Process exact duplicates and migrate them."""
    duplicates_file = ROOT / "docs/reports/exact_duplicates.csv"

    if not duplicates_file.exists():
        print("ERROR: docs/reports/exact_duplicates.csv not found")
        return False

    moved_files = []
    shim_files = []

    # Increase CSV field size limit
    csv.field_size_limit(1000000)

    with open(duplicates_file) as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            if len(row) < 3:
                continue

            _hash_val, canonical, redundants_str = row[0], row[1], row[2]

            # Skip node_modules files
            if "node_modules" in canonical or "node_modules" in redundants_str:
                continue

            redundants = [r.strip() for r in redundants_str.split("|") if r.strip()]

            print("\nProcessing duplicate group:")
            print(f"  Canonical: {canonical}")
            print(f"  Redundants: {redundants}")

            for redundant in redundants:
                if not redundant:
                    continue

                # Check if file exists
                redundant_path = ROOT / redundant
                if not redundant_path.exists():
                    print(f"  WARNING: {redundant} does not exist, skipping")
                    continue

                # Create archive path
                archive_path = f"archive/duplicates/{redundant}"
                archive_full_path = ROOT / archive_path
                archive_full_path.parent.mkdir(parents=True, exist_ok=True)

                # Git mv the file
                success, output = run_git_command(f'git mv "{redundant}" "{archive_path}"')
                if success:
                    print(f"  ✓ Moved {redundant} → {archive_path}")
                    moved_files.append((redundant, archive_path))

                    # Create compat shim if it's a Python file
                    if redundant.endswith(".py") and not redundant.endswith("__init__.py"):
                        create_compat_shim(redundant, canonical)
                        shim_files.append(redundant)

                else:
                    print(f"  ERROR: Failed to move {redundant}: {output}")
                    return False

    print("\n✓ Migration complete:")
    print(f"  - Moved {len(moved_files)} duplicate files to archive/")
    print(f"  - Created {len(shim_files)} compatibility shims")

    return True


if __name__ == "__main__":
    if migrate_duplicates():
        print("\nReady to commit changes with:")
        print(
            'git add . && git commit -m "refactor(dedupe): move exact duplicates to archive and add compat shims"'
        )
    else:
        print("\nMigration failed!")
        sys.exit(1)
