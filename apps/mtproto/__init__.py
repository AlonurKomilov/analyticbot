"""
MTProto Application Module - System and User MTProto Management

Structure:
- system/: System MTProto (ENV-configured TELEGRAM_API_ID/HASH)
- user/: User MTProto (database credentials, multi-tenant)
- shared/: Shared resources (metrics, audit)
"""

from apps.mtproto.system.config import MTProtoSettings
from apps.mtproto.system.di import configure_container, container
from apps.mtproto.system.health import HealthCheck

__all__ = ["MTProtoSettings", "container", "configure_container", "HealthCheck"]
