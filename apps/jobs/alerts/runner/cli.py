"""
Alert Runner CLI
Command-line interface for running alert detection job
"""

import argparse
import asyncio
import logging

from apps.jobs.alerts.runner.base import DEFAULT_INTERVAL_SECONDS, logger
from apps.jobs.alerts.runner.runner import AlertRunner


async def main():
    """Main entry point for running alerts job"""
    parser = argparse.ArgumentParser(description="Analytics Alert Detection Runner")
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Detection interval in seconds (default: {DEFAULT_INTERVAL_SECONDS})",
    )
    parser.add_argument("--once", action="store_true", help="Run detection once and exit")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    runner = AlertRunner()

    try:
        if args.once:
            logger.info("Running alert detection once")
            await runner.run_detection_cycle()
        else:
            logger.info(f"Starting continuous alert detection with {args.interval}s interval")
            await runner.start(args.interval)
    except KeyboardInterrupt:
        logger.info("Shutting down alert runner")
        runner.stop()
    except Exception as e:
        logger.error(f"Alert runner failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
