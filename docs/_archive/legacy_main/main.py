#!/usr/bin/env python3
"""
DEPRECATED: Legacy main runner - Use apps/api/main.py and apps/bot/run_bot.py directly

For new development, use the canonical entry points:
- API: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
- Bot: python -m apps.bot.run_bot

This file remains for backward compatibility.
"""

import argparse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_bot():
    """Run the main Telegram bot"""
    import subprocess
    import sys

    print("🤖 Starting Telegram bot...")
    result = subprocess.run(
        [sys.executable, "-m", "apps.bot.run_bot"], cwd=str(Path(__file__).parent)
    )
    sys.exit(result.returncode)


def run_api():
    """Run the main API server"""
    import uvicorn

    from apps.api.main import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_ai_api():
    """Run the AI/ML API server (DEPRECATED - use main API)"""
    import uvicorn
    from archive.pure_ai_api import app

    print("⚠️  DEPRECATED: AI API moved to main API. Use 'python main.py api' instead.")
    uvicorn.run(app, host="0.0.0.0", port=8001)


def run_security_api():
    """Run the Security API server (DEPRECATED - use main API)"""
    import uvicorn
    from archive.security_api import app

    print("⚠️  DEPRECATED: Security API moved to main API. Use 'python main.py api' instead.")
    uvicorn.run(app, host="0.0.0.0", port=8002)


def run_tests():
    """Run test suite"""
    import pytest

    pytest.main(["-v", "tests/"])


def main():
    parser = argparse.ArgumentParser(description="AnalyticBot Runner")
    parser.add_argument(
        "component",
        choices=["bot", "api", "ai-api", "security-api", "tests"],
        help="Component to run",
    )

    args = parser.parse_args()

    if args.component == "bot":
        run_bot()
    elif args.component == "api":
        run_api()
    elif args.component == "ai-api":
        run_ai_api()
    elif args.component == "security-api":
        run_security_api()
    elif args.component == "tests":
        run_tests()


if __name__ == "__main__":
    main()
