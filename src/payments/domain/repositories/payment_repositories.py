"""
Payment Domain Repository Interfaces

Abstract interfaces defining data access contracts for the payments domain.
These interfaces are implemented by the infrastructure layer.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..entities import Payment, PaymentMethod, Subscription
from ..value_objects import (
    PaymentId, PaymentMethodId, SubscriptionId, CustomerId, PlanId,
    PaymentStatus, SubscriptionStatus, PaymentProvider
)


class IPaymentRepository(ABC):
    """Repository interface for Payment aggregate"""
    
    # ========== CRUD OPERATIONS ==========
    
    @abstractmethod
    async def save(self, payment: Payment) -> None:
        """Save payment to storage"""
        
    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Optional[Payment]:
        """Get payment by ID"""
        
    @abstractmethod
    async def get_by_provider_payment_id(
        self, 
        provider: PaymentProvider,
        provider_payment_id: str
    ) -> Optional[Payment]:
        """Get payment by provider's payment ID"""
        
    @abstractmethod
    async def exists(self, payment_id: PaymentId) -> bool:
        """Check if payment exists"""
        
    @abstractmethod
    async def delete(self, payment_id: PaymentId) -> bool:
        """Delete payment (soft delete)"""
        
    # ========== QUERY OPERATIONS ==========
    
    @abstractmethod
    async def find_by_customer_id(
        self,
        customer_id: CustomerId,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[PaymentStatus] = None
    ) -> List[Payment]:
        """Find payments by customer ID with optional filtering"""
        
    @abstractmethod
    async def find_by_status(
        self,
        status: PaymentStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Find payments by status"""
        
    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0
    ) -> List[Payment]:
        """Find payments within date range"""
        
    @abstractmethod
    async def find_failed_payments_for_retry(
        self,
        max_retry_count: int = 3,
        limit: int = 50
    ) -> List[Payment]:
        """Find failed payments eligible for retry"""
        
    @abstractmethod
    async def find_by_payment_method_id(
        self,
        payment_method_id: PaymentMethodId,
        limit: int = 50,
        offset: int = 0
    ) -> List[Payment]:
        """Find payments by payment method"""
        
    # ========== ANALYTICS ==========
    
    @abstractmethod
    async def get_payment_statistics(
        self,
        customer_id: Optional[CustomerId] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payment statistics"""
        
    @abstractmethod
    async def get_revenue_by_period(
        self,
        period: str,  # 'day', 'week', 'month', 'year'
        periods_count: int = 12
    ) -> List[Dict[str, Any]]:
        """Get revenue breakdown by time period"""
        
    @abstractmethod
    async def get_top_customers_by_revenue(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top customers by total revenue"""
        
    # ========== IDEMPOTENCY ==========
    
    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Payment]:
        """Get payment by idempotency key"""
        
    @abstractmethod
    async def reserve_idempotency_key(self, idempotency_key: str, payment_id: PaymentId) -> bool:
        """Reserve idempotency key for payment"""


class IPaymentMethodRepository(ABC):
    """Repository interface for PaymentMethod entities"""
    
    # ========== CRUD OPERATIONS ==========
    
    @abstractmethod
    async def save(self, payment_method: PaymentMethod) -> None:
        """Save payment method to storage"""
        
    @abstractmethod
    async def get_by_id(self, payment_method_id: PaymentMethodId) -> Optional[PaymentMethod]:
        """Get payment method by ID"""
        
    @abstractmethod
    async def exists(self, payment_method_id: PaymentMethodId) -> bool:
        """Check if payment method exists"""
        
    @abstractmethod
    async def delete(self, payment_method_id: PaymentMethodId) -> bool:
        """Delete payment method (soft delete)"""
        
    # ========== QUERY OPERATIONS ==========
    
    @abstractmethod
    async def find_by_customer_id(
        self,
        customer_id: CustomerId,
        active_only: bool = True
    ) -> List[PaymentMethod]:
        """Find payment methods by customer ID"""
        
    @abstractmethod
    async def get_default_for_customer(self, customer_id: CustomerId) -> Optional[PaymentMethod]:
        """Get customer's default payment method"""
        
    @abstractmethod
    async def find_by_provider(
        self,
        provider: PaymentProvider,
        customer_id: Optional[CustomerId] = None
    ) -> List[PaymentMethod]:
        """Find payment methods by provider"""
        
    @abstractmethod
    async def find_expiring_cards(
        self,
        days_ahead: int = 30,
        limit: int = 100
    ) -> List[PaymentMethod]:
        """Find card payment methods expiring soon"""
        
    @abstractmethod
    async def get_by_provider_method_id(
        self,
        provider: PaymentProvider,
        provider_method_id: str
    ) -> Optional[PaymentMethod]:
        """Get payment method by provider's method ID"""
        
    # ========== BUSINESS OPERATIONS ==========
    
    @abstractmethod
    async def set_as_default(
        self,
        payment_method_id: PaymentMethodId,
        customer_id: CustomerId
    ) -> None:
        """Set payment method as default and unset others"""
        
    @abstractmethod
    async def deactivate_all_for_customer(
        self,
        customer_id: CustomerId,
        except_method_id: Optional[PaymentMethodId] = None
    ) -> int:
        """Deactivate all payment methods for customer"""
        
    @abstractmethod
    async def count_by_customer(self, customer_id: CustomerId, active_only: bool = True) -> int:
        """Count payment methods for customer"""


class ISubscriptionRepository(ABC):
    """Repository interface for Subscription aggregate"""
    
    # ========== CRUD OPERATIONS ==========
    
    @abstractmethod
    async def save(self, subscription: Subscription) -> None:
        """Save subscription to storage"""
        
    @abstractmethod
    async def get_by_id(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        """Get subscription by ID"""
        
    @abstractmethod
    async def exists(self, subscription_id: SubscriptionId) -> bool:
        """Check if subscription exists"""
        
    @abstractmethod
    async def delete(self, subscription_id: SubscriptionId) -> bool:
        """Delete subscription (soft delete)"""
        
    # ========== QUERY OPERATIONS ==========
    
    @abstractmethod
    async def find_by_customer_id(
        self,
        customer_id: CustomerId,
        active_only: bool = True
    ) -> List[Subscription]:
        """Find subscriptions by customer ID"""
        
    @abstractmethod
    async def get_active_subscription_for_customer(
        self,
        customer_id: CustomerId
    ) -> Optional[Subscription]:
        """Get customer's active subscription"""
        
    @abstractmethod
    async def find_by_status(
        self,
        status: SubscriptionStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Subscription]:
        """Find subscriptions by status"""
        
    @abstractmethod
    async def find_by_plan_id(
        self,
        plan_id: PlanId,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Subscription]:
        """Find subscriptions by plan ID"""
        
    @abstractmethod
    async def find_expiring_trials(
        self,
        days_ahead: int = 3,
        limit: int = 100
    ) -> List[Subscription]:
        """Find trial subscriptions expiring soon"""
        
    @abstractmethod
    async def find_due_for_renewal(
        self,
        limit: int = 100
    ) -> List[Subscription]:
        """Find subscriptions due for renewal"""
        
    @abstractmethod
    async def find_past_due(
        self,
        days_overdue: int = 1,
        limit: int = 100
    ) -> List[Subscription]:
        """Find past due subscriptions"""
        
    @abstractmethod
    async def find_for_cancellation(
        self,
        max_failed_days: int = 30,
        limit: int = 100
    ) -> List[Subscription]:
        """Find subscriptions that should be auto-canceled"""
        
    @abstractmethod
    async def get_by_provider_subscription_id(
        self,
        provider_subscription_id: str
    ) -> Optional[Subscription]:
        """Get subscription by provider's subscription ID"""
        
    # ========== ANALYTICS ==========
    
    @abstractmethod
    async def get_subscription_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get subscription statistics"""
        
    @abstractmethod
    async def get_churn_rate(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate churn rate for given period"""
        
    @abstractmethod
    async def get_revenue_forecast(
        self,
        periods_ahead: int = 12
    ) -> List[Dict[str, Any]]:
        """Get recurring revenue forecast"""
        
    @abstractmethod
    async def get_plan_popularity(self) -> List[Dict[str, Any]]:
        """Get subscription plan popularity statistics"""
        
    # ========== BILLING OPERATIONS ==========
    
    @abstractmethod
    async def mark_as_billed(
        self,
        subscription_id: SubscriptionId,
        payment_id: PaymentId,
        billing_period_start: datetime,
        billing_period_end: datetime
    ) -> None:
        """Mark subscription as billed for period"""
        
    @abstractmethod
    async def update_next_billing_date(
        self,
        subscription_id: SubscriptionId,
        next_billing_date: datetime
    ) -> None:
        """Update next billing date"""


class IPaymentPlanRepository(ABC):
    """Repository interface for subscription plans"""
    
    # ========== CRUD OPERATIONS ==========
    
    @abstractmethod
    async def get_by_id(self, plan_id: PlanId) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        
    @abstractmethod
    async def get_all_active(self) -> List[Dict[str, Any]]:
        """Get all active plans"""
        
    @abstractmethod
    async def exists(self, plan_id: PlanId) -> bool:
        """Check if plan exists"""
        
    # ========== PRICING ==========
    
    @abstractmethod
    async def get_plan_pricing(
        self,
        plan_id: PlanId,
        billing_cycle: str
    ) -> Optional[Dict[str, Any]]:
        """Get plan pricing for specific billing cycle"""