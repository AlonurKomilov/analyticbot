#!/usr/bin/env python3
"""
AnalyticBot - Main Runner
Entry point for running different components of the application
"""

import argparse
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_bot():
    """Run the main Telegram bot"""
    from scripts.run_bot import main

    main()


def run_api():
    """Run the main API server"""
    import uvicorn

    from apis.main_api import app

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_ai_api():
    """Run the AI/ML API server"""
    import uvicorn

    from apis.pure_ai_api import app

    uvicorn.run(app, host="0.0.0.0", port=8001)


def run_security_api():
    """Run the Security API server"""
    import uvicorn

    from apis.security_api import app

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
