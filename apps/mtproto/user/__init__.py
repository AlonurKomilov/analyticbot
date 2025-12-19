"""
User MTProto Management - Multi-tenant MTProto clients for users.

This module manages user-owned MTProto sessions that are added via the frontend.
Credentials are stored encrypted in the database (user_bot_credentials table).

Components:
- user_mtproto_service.py: UserMTProtoService and UserMTProtoClient
  - Manages pool of user-specific MTProto clients
  - Credentials from encrypted database fields
  - Session string based authentication
"""

from apps.mtproto.user.user_mtproto_service import (
    UserMTProtoService,
    UserMTProtoClient,
)

__all__ = [
    "UserMTProtoService",
    "UserMTProtoClient",
]
