"""MTProto application entry point.

This module provides the main entry point for the MTProto functionality.
By default, the application is disabled via feature flag (MTPROTO_ENABLED=False)
to ensure no behavior change to existing applications.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apps.mtproto.config import MTProtoSettings  # noqa: E402
from apps.mtproto.di import configure_container, container  # noqa: E402


def setup_logging(level: str) -> None:
    """Setup logging for MTProto application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    """Main entry point for MTProto application."""
    # Load settings
    settings = MTProtoSettings()

    # Setup logging
    setup_logging(settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    # Check if MTProto is enabled
    if not settings.MTPROTO_ENABLED:
        logger.info("MTProto functionality is disabled (MTPROTO_ENABLED=False)")
        logger.info("To enable, set MTPROTO_ENABLED=true in your environment")
        return

    # Validate required settings when enabled
    if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH are required when MTPROTO_ENABLED=true")
        sys.exit(1)

    logger.info("Starting MTProto application...")

    # Configure DI container
    configure_container(settings)

    # Wire dependencies
    container.wire(modules=[__name__])

    logger.info("MTProto application initialized successfully")
    logger.info("This is a stub implementation - full functionality coming in future phases")


if __name__ == "__main__":
    main()
