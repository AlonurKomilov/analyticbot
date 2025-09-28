"""
PaymentService Interface - Public API for payments module
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class PaymentService(Protocol):
    """PaymentService public interface"""

    async def process_payment(self, payment_data: dict) -> dict:
        """process_payment operation"""
        ...

    async def get_payment_status(self, payment_id: int) -> str:
        """get_payment_status operation"""
        ...

    async def get_user_billing(self, user_id: int) -> dict:
        """get_user_billing operation"""
        ...

    async def cancel_subscription(self, user_id: int) -> bool:
        """cancel_subscription operation"""
        ...
