# AI Fixer v2 (Project-Aware) + Auto-Trigger

How to use:
- Manually: add label `ai-fix` **or** comment `/ai-fix` on the PR.
- Automatically: when the main CI fails, `auto-ai-fix-on-red.yml` adds `ai-fix` label to the PR → AI Fixer runs.

What it does:
1) ruff --fix & format
2) mypy (only changed files vs origin/main)
3) pytest + diff-cover (changed lines ≥ 85%)
4) if any fails, the AI creates a unified diff patch, applies it safely (allowed dirs only), re-runs, and pushes.

Requires repo secret: `OPENAI_API_KEY`.
