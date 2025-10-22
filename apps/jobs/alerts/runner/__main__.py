"""
Entry point for running alert runner as a module
Usage: python -m apps.jobs.alerts.runner
"""

import asyncio

from apps.jobs.alerts.runner.cli import main

if __name__ == "__main__":
    asyncio.run(main())
