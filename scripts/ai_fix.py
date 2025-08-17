#!/usr/bin/env python3
import argparse, os, re, subprocess, sys, json

ALLOWED_DIRS = ["bot/", "api/", "alembic/", "tests/", "scripts/", "docker/"]
MAX_PATCH_BYTES = 300_000

SYSTEM_MSG = "You output only a unified diff patch in a fenced ```patch block. No explanations."
USER_INTRO = """You are a senior Python engineer.
I will give you:
- Git diff against origin/main
- Project map (per-file outline)
- Import graph
- Mypy/PyTest/Diff-cover results (if any)

Goal: Return ONLY ONE unified diff patch to fix failures with minimal, safe changes.
Constraints:
- Prefer editing only inside: bot/, api/, alembic/, tests/, scripts/, docker/.
- Keep public interfaces stable unless necessary; if changed, update all references.
- If changed code lacks tests (diff coverage), add a small focused test under tests/.
- No heavy new dependencies.
- Begin with:
*** Begin Patch
*** Update File: <path>
...
*** End Patch
"""

def run(cmd):
    return subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)

def filter_allowed(patch: str) -> str:
    lines = patch.splitlines()
    allowed, current = [], None
    for ln in lines:
        m = re.match(r"\*\*\* Update File: (.+)", ln)
        if m:
            current = m.group(1)
            if not any(current.startswith(p) for p in ALLOWED_DIRS):
                current = None
        if ln.startswith("*** Begin Patch") or ln.startswith("*** End Patch"):
            allowed.append(ln); continue
        if current is not None:
            allowed.append(ln)
    return "\n".join(allowed)

def call_openai(prompt: str) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key: return ""
    import urllib.request
    data = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        data=data
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
        return json.loads(resp)["choices"][0]["message"]["content"]
    except Exception:
        return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    ctx = open(args.context, "r", encoding="utf-8", errors="ignore").read()
    prompt = USER_INTRO + "\n\n=== CONTEXT START ===\n" + ctx[:180000] + "\n=== CONTEXT END ===\n\nReturn ONLY the patch inside:\n```patch\n...here...\n```"

    content = call_openai(prompt)
    if not content: sys.exit(0)
    m = re.search(r"```patch\s+([\s\S]*?)```", content)
    if not m: sys.exit(0)
    patch = filter_allowed(m.group(1).strip())
    if not patch or len(patch.encode("utf-8")) > MAX_PATCH_BYTES: sys.exit(0)

    open("ai.patch", "w", encoding="utf-8").write(patch)
    p = run("git apply -3 --whitespace=fix ai.patch")
    if p.returncode != 0: sys.exit(0)
    print("AI patch applied.")

if __name__ == "__main__":
    main()
