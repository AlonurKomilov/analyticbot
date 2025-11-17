"""
Session Storage Module

Temporary storage for pending MTProto verification sessions.
Fixes phone_code_hash expiry issue by maintaining session continuity.
"""

import logging
from time import time

logger = logging.getLogger(__name__)

# Key: user_id, Value: (session_string, timestamp)
_pending_sessions: dict[int, tuple[str, float]] = {}


def store_pending_session(user_id: int, session_string: str):
    """Store session string for pending verification (expires after 10 minutes)"""
    _pending_sessions[user_id] = (session_string, time())
    # Clean up old sessions (older than 10 minutes)
    current_time = time()
    expired_users = [
        uid for uid, (_, timestamp) in _pending_sessions.items() if current_time - timestamp > 600
    ]
    for uid in expired_users:
        del _pending_sessions[uid]
    logger.debug(f"Stored pending session for user {user_id}")


def get_pending_session(user_id: int) -> str | None:
    """Get pending session string if exists and not expired"""
    if user_id in _pending_sessions:
        session_string, timestamp = _pending_sessions[user_id]
        if time() - timestamp < 600:  # 10 minutes
            return session_string
        else:
            del _pending_sessions[user_id]
            logger.debug(f"Pending session expired for user {user_id}")
    return None


def clear_pending_session(user_id: int):
    """Clear pending session after successful verification"""
    if user_id in _pending_sessions:
        del _pending_sessions[user_id]
        logger.debug(f"Cleared pending session for user {user_id}")
