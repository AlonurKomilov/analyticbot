"""MTProto application package."""

from .config import MTProtoSettings
from .di import configure_container, container
from .health import HealthCheck

__all__ = ["MTProtoSettings", "container", "configure_container", "HealthCheck"]
