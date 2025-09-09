"""
MTProto Configuration Protocol
Defines the interface for MTProto settings
"""

from typing import Protocol


class MTProtoConfigProtocol(Protocol):
    """Protocol for MTProto configuration"""

    MTPROTO_ENABLED: bool
    TELEGRAM_API_ID: int | None
    TELEGRAM_API_HASH: str | None
    TELEGRAM_SESSION_NAME: str
    TELEGRAM_PROXY: str | None
    MTPROTO_SLEEP_THRESHOLD: float
    MTPROTO_RETRY_BACKOFF: float
    MTPROTO_UPDATES_ENABLED: bool
