"""
IdentityService Interface - Public API for identity module
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IdentityService(Protocol):
    """IdentityService public interface"""

    async def authenticate_user(self, credentials: dict) -> dict | None:
        """authenticate_user operation"""
        ...

    async def get_user_profile(self, user_id: int) -> dict | None:
        """get_user_profile operation"""
        ...

    async def update_user_profile(self, user_id: int, data: dict) -> dict:
        """update_user_profile operation"""
        ...

    async def create_user(self, user_data: dict) -> dict:
        """create_user operation"""
        ...
