# scripts/dedupe_plan.py
import csv
import hashlib
import os
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXCLUDES = ["archive/", "results/", ".git/", ".venv/", "node_modules/", "__pycache__/"]
PREF = [
    r"^apps/api/",
    r"^apps/bot/",
    r"^apps/frontend/",
    r"^core/",
    r"^infra/",
    r"^config/",
    r"^scripts/",
    r"^tests/",
    r"^docs/",
]
DEPREF = [r"^apis/", r"^bot/", r"^archive/", r"^results/"]


def should_skip(p):
    s = p.replace("\\", "/")
    return any(s.startswith(x) for x in EXCLUDES)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8192), b""):
            h.update(b)
    return h.hexdigest()


def rank(p):
    for i, pat in enumerate(PREF):
        if re.search(pat, p):
            return i
    penalty = sum(100 for pat in DEPREF if re.search(pat, p))
    return 50 + penalty


def main():
    files = []
    for dp, _, fns in os.walk(ROOT):
        for fn in fns:
            rp = os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/")
            if should_skip(rp):
                continue
            try:
                h = sha256(os.path.join(ROOT, rp))
            except:
                continue
            files.append((rp, fn, h))

    by_hash = defaultdict(list)
    by_name = defaultdict(list)
    for rp, fn, h in files:
        by_hash[h].append(rp)
        by_name[fn].append((rp, h))

    # Ensure reports directory exists
    rep = ROOT / "docs" / "reports"
    rep.mkdir(parents=True, exist_ok=True)

    # Write exact duplicates CSV
    with open(rep / "exact_duplicates.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hash", "canonical", "redundants[]"])
        for h, paths in sorted(by_hash.items(), key=lambda kv: kv[0]):
            if len(paths) < 2:
                continue
            canon = sorted(paths, key=rank)[0]
            reds = [p for p in paths if p != canon]
            w.writerow([h, canon, "|".join(reds)])

    # Write same name different content CSV
    with open(rep / "same_name_diff_content.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "paths[]", "hashes[]"])
        for name, items in sorted(by_name.items()):
            hashes = sorted({h for _, h in items})
            if len(hashes) <= 1:
                continue
            paths = sorted([rp for rp, _ in items])
            w.writerow([name, "|".join(paths), "|".join(hashes)])

    # Write summary report
    with open(rep / "dedupe_report.md", "w") as f:
        f.write(
            "# Dedupe Plan\n\n- exact_duplicates.csv and same_name_diff_content.csv generated.\n"
        )

    print("OK: wrote dedupe plan to docs/reports/")


if __name__ == "__main__":
    main()
