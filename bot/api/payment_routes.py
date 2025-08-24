"""
Payment system API routes
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from bot.models.payment import (
    PaymentCreate, PaymentResponse, PaymentMethodCreate, PaymentMethodResponse,
    SubscriptionCreate, SubscriptionResponse, BillingCycle, PaymentProvider,
    PaymentStatus, SubscriptionStatus
)
from bot.services.payment_service import PaymentService
from bot.database.repositories.payment_repository import PaymentRepository


class PaymentStats(BaseModel):
    """Payment statistics response"""
    payment_count: int
    total_revenue: Decimal
    failed_amount: Decimal
    successful_payments: int
    failed_payments: int
    success_rate: float = Field(computed=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.success_rate = (
            self.successful_payments / max(self.payment_count, 1) * 100
            if self.payment_count > 0 else 0
        )


class SubscriptionStats(BaseModel):
    """Subscription statistics response"""
    total_subscriptions: int
    active_subscriptions: int
    canceled_subscriptions: int
    past_due_subscriptions: int
    avg_subscription_amount: Optional[Decimal]
    churn_rate: float = Field(computed=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.churn_rate = (
            self.canceled_subscriptions / max(self.total_subscriptions, 1) * 100
            if self.total_subscriptions > 0 else 0
        )


class PlanWithPricing(BaseModel):
    """Plan with pricing information"""
    id: int
    name: str
    max_channels: int
    max_posts_per_month: int
    price_monthly: Decimal
    price_yearly: Decimal
    is_active: bool
    savings_yearly: Decimal = Field(computed=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate yearly savings (monthly * 12 - yearly)
        monthly_yearly_cost = self.price_monthly * 12
        self.savings_yearly = monthly_yearly_cost - self.price_yearly


class WebhookRequest(BaseModel):
    """Webhook request model"""
    provider: str
    event_type: str
    signature: str
    webhook_secret: str


# Router setup
payment_router = APIRouter(prefix="/payment", tags=["payments"])
security = HTTPBearer()


# Mock dependency functions - replace with real authentication
async def get_current_user_id(token: str = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    # TODO: Implement real JWT validation
    return 1  # Mock user ID


async def get_payment_service() -> PaymentService:
    """Get payment service instance"""
    # TODO: Implement proper dependency injection
    from bot.database.connection import get_db_pool
    pool = await get_db_pool()
    repository = PaymentRepository(pool)
    service = PaymentService(repository)
    
    # Register adapters - TODO: get from config
    from bot.services.payment_service import StripeAdapter, PaymeAdapter, ClickAdapter
    
    # Mock configurations - replace with real config
    service.register_adapter(StripeAdapter("sk_test_...", "whsec_..."))
    service.register_adapter(PaymeAdapter("merchant_123", "secret_key"))
    service.register_adapter(ClickAdapter("merchant_456", "service_789", "secret"))
    
    return service


# Payment Method Endpoints
@payment_router.post("/methods", response_model=PaymentMethodResponse)
async def create_payment_method(
    payment_method_data: PaymentMethodCreate,
    provider: PaymentProvider = PaymentProvider.STRIPE,
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create a new payment method"""
    try:
        return await payment_service.create_payment_method(
            user_id=user_id,
            payment_method_data=payment_method_data,
            provider=provider.value
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create payment method")


@payment_router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's payment methods"""
    return await payment_service.get_user_payment_methods(user_id)


@payment_router.delete("/methods/{method_id}")
async def delete_payment_method(
    method_id: str,
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Delete a payment method"""
    # Verify ownership
    methods = await payment_service.get_user_payment_methods(user_id)
    method_exists = any(method.id == method_id for method in methods)
    
    if not method_exists:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    success = await payment_service.repository.delete_payment_method(method_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete payment method")
    
    return {"message": "Payment method deleted successfully"}


# Payment Processing Endpoints
@payment_router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Process a one-time payment"""
    try:
        return await payment_service.process_payment(
            user_id=user_id,
            payment_data=payment_data,
            idempotency_key=idempotency_key
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment processing failed")


@payment_router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    limit: int = 50,
    offset: int = 0,
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's payment history"""
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
    
    payments = await payment_service.repository.get_user_payments(user_id, limit, offset)
    return [PaymentResponse(**payment) for payment in payments]


@payment_router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get specific payment details"""
    payment = await payment_service.repository.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify ownership
    if payment["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return PaymentResponse(**payment)


# Subscription Endpoints
@payment_router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create a new subscription"""
    try:
        return await payment_service.create_subscription(
            user_id=user_id,
            subscription_data=subscription_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create subscription")


@payment_router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_current_subscription(
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's current active subscription"""
    subscription = await payment_service.repository.get_user_active_subscription(user_id)
    if not subscription:
        return None
    
    return SubscriptionResponse(
        id=subscription["id"],
        user_id=subscription["user_id"],
        plan_id=subscription["plan_id"],
        plan_name=subscription["plan_name"],
        status=SubscriptionStatus(subscription["status"]),
        billing_cycle=BillingCycle(subscription["billing_cycle"]),
        amount=subscription["amount"],
        currency=subscription["currency"],
        current_period_start=subscription["current_period_start"],
        current_period_end=subscription["current_period_end"],
        trial_ends_at=subscription["trial_ends_at"],
        created_at=subscription["created_at"]
    )


@payment_router.put("/subscription/cancel")
async def cancel_subscription(
    user_id: int = Depends(get_current_user_id),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Cancel user's active subscription"""
    subscription = await payment_service.repository.get_user_active_subscription(user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    success = await payment_service.repository.update_subscription_status(
        subscription_id=subscription["id"],
        status=SubscriptionStatus.CANCELED,
        canceled_at=datetime.utcnow()
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    # TODO: Cancel with payment provider if provider_subscription_id exists
    
    return {"message": "Subscription canceled successfully"}


# Plan Endpoints
@payment_router.get("/plans", response_model=List[PlanWithPricing])
async def get_pricing_plans(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get all available pricing plans"""
    plans = await payment_service.repository.get_all_active_plans()
    return [PlanWithPricing(**plan) for plan in plans]


@payment_router.get("/plans/{plan_id}", response_model=PlanWithPricing)
async def get_plan(
    plan_id: int,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get specific plan details"""
    plan = await payment_service.repository.get_plan_with_pricing(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return PlanWithPricing(**plan)


# Webhook Endpoints
@payment_router.post("/webhooks/{provider}")
async def handle_payment_webhook(
    provider: PaymentProvider,
    request: Request,
    signature: str = Header(None, alias="Stripe-Signature"),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Handle payment provider webhooks"""
    try:
        payload = await request.body()
        
        # Get webhook secret from config - TODO: implement proper config
        webhook_secrets = {
            PaymentProvider.STRIPE: "whsec_test_secret",
            PaymentProvider.PAYME: "payme_webhook_secret", 
            PaymentProvider.CLICK: "click_webhook_secret"
        }
        
        webhook_secret = webhook_secrets.get(provider)
        if not webhook_secret:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        result = await payment_service.handle_webhook(
            provider=provider.value,
            payload=payload,
            signature=signature,
            webhook_secret=webhook_secret
        )
        
        return {"message": "Webhook processed", "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# Analytics Endpoints
@payment_router.get("/analytics/revenue", response_model=PaymentStats)
async def get_revenue_analytics(
    days: int = 30,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get revenue analytics for specified period"""
    if days > 365:
        raise HTTPException(status_code=400, detail="Maximum 365 days allowed")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    stats = await payment_service.repository.get_revenue_stats(start_date, end_date)
    return PaymentStats(**stats)


@payment_router.get("/analytics/subscriptions", response_model=SubscriptionStats)
async def get_subscription_analytics(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get subscription analytics"""
    stats = await payment_service.repository.get_subscription_stats()
    return SubscriptionStats(**stats)


# Health Check
@payment_router.get("/health")
async def payment_health_check():
    """Health check for payment system"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "supported_providers": [provider.value for provider in PaymentProvider]
    }
