"""
Centralized Mock Payment Service

Consolidated from scattered mock payment implementations.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import random
import uuid

from ..base import BaseMockService, mock_metrics
from ..protocols import PaymentServiceProtocol

logger = logging.getLogger(__name__)

# Payment constants
PAYMENT_DELAY_MS = 150
PAYMENT_SUCCESS_RATE = 0.92
SUPPORTED_CURRENCIES = ["usd", "eur", "gbp"]


class MockPaymentService(BaseMockService, PaymentServiceProtocol):
    """Centralized mock payment service for all testing needs"""
    
    def __init__(self):
        super().__init__("MockPaymentService")
        self.transactions = {}
        self.failed_transactions = []
        self.total_processed = 0
        
    def get_service_name(self) -> str:
        return self.service_name
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock payment service health check"""
        mock_metrics.record_call(self.service_name, "health_check")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)
        
        base_health = await super().health_check()
        base_health.update({
            "transactions_processed": self.total_processed,
            "failed_transactions": len(self.failed_transactions),
            "success_rate": PAYMENT_SUCCESS_RATE,
            "supported_currencies": SUPPORTED_CURRENCIES
        })
        return base_health
    
    async def create_payment_intent(self, amount: int, currency: str = "usd", **kwargs) -> Dict[str, Any]:
        """Create a mock payment intent"""
        mock_metrics.record_call(self.service_name, "create_payment_intent")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)
        
        if currency.lower() not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Currency {currency} not supported")
            
        intent_id = str(uuid.uuid4())
        client_secret = f"pi_{intent_id}_secret_{uuid.uuid4().hex[:8]}"
        
        # Simulate occasional failures
        will_succeed = random.random() < PAYMENT_SUCCESS_RATE
        
        intent_data = {
            "id": intent_id,
            "amount": amount,
            "currency": currency.lower(),
            "status": "requires_confirmation" if will_succeed else "requires_payment_method",
            "client_secret": client_secret,
            "created": datetime.utcnow().isoformat(),
            "metadata": kwargs.get("metadata", {}),
            "mock_simulation": {
                "will_succeed": will_succeed,
                "processing_delay": PAYMENT_DELAY_MS
            }
        }
        
        self.transactions[intent_id] = intent_data
        self.total_processed += 1
        
        return intent_data
    
    async def confirm_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        """Confirm a mock payment intent"""
        mock_metrics.record_call(self.service_name, "confirm_payment_intent")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)
        
        if intent_id not in self.transactions:
            return {"error": "Payment intent not found"}
            
        intent = self.transactions[intent_id]
        will_succeed = intent["mock_simulation"]["will_succeed"]
        
        if will_succeed:
            intent["status"] = "succeeded"
            intent["confirmed_at"] = datetime.utcnow().isoformat()
        else:
            intent["status"] = "payment_failed"
            intent["failed_at"] = datetime.utcnow().isoformat()
            intent["failure_reason"] = random.choice([
                "card_declined",
                "insufficient_funds",
                "network_error",
                "processing_error"
            ])
            self.failed_transactions.append(intent_id)
            
        return intent
    
    async def get_payment_status(self, intent_id: str) -> Dict[str, Any]:
        """Get payment status"""
        mock_metrics.record_call(self.service_name, "get_payment_status")
        
        if intent_id not in self.transactions:
            return {"error": "Payment intent not found"}
            
        return self.transactions[intent_id]
    
    async def refund_payment(self, intent_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Create a mock refund"""
        mock_metrics.record_call(self.service_name, "refund_payment")
        await asyncio.sleep(PAYMENT_DELAY_MS / 1000)
        
        if intent_id not in self.transactions:
            return {"error": "Payment intent not found"}
            
        intent = self.transactions[intent_id]
        if intent["status"] != "succeeded":
            return {"error": "Cannot refund unsuccessful payment"}
            
        refund_amount = amount or intent["amount"]
        refund_id = str(uuid.uuid4())
        
        refund_data = {
            "id": refund_id,
            "payment_intent": intent_id,
            "amount": refund_amount,
            "currency": intent["currency"],
            "status": "succeeded",
            "created": datetime.utcnow().isoformat(),
            "reason": "requested_by_customer"
        }
        
        # Update original intent
        intent["refunded"] = True
        intent["refund_id"] = refund_id
        
        return refund_data
    
    async def list_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """List recent transactions"""
        mock_metrics.record_call(self.service_name, "list_transactions")
        
        transactions = list(self.transactions.values())
        transactions.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "data": transactions[:limit],
            "has_more": len(transactions) > limit,
            "total_count": len(transactions)
        }
    
    def reset(self) -> None:
        """Reset mock service state"""
        super().reset()
        self.transactions.clear()
        self.failed_transactions.clear()
        self.total_processed = 0
    
    def get_transaction_history(self) -> Dict[str, Any]:
        """Get transaction history for testing"""
        return {
            "all_transactions": self.transactions.copy(),
            "failed_transactions": self.failed_transactions.copy(),
            "total_processed": self.total_processed,
            "success_rate": (self.total_processed - len(self.failed_transactions)) / max(1, self.total_processed)
        }