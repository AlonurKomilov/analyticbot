"""
Payment routes for the bot API.
Comprehensive payment system with subscriptions, webhooks, and analytics.
"""

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from apps.bot.models.payment import (
    BillingCycle,
    PaymentCreate,
    PaymentMethodCreate,
    PaymentMethodResponse,
    PaymentProvider,
    PaymentResponse,
    PaymentStatus,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionStatus,
)
from apps.bot.services.payment_service import PaymentService
from apps.bot.services.stripe_adapter import StripeAdapter
from config import settings
from infra.db.repositories.payment_repository import AsyncpgPaymentRepository


class PaymentStats(BaseModel):
    """Payment statistics response"""

    payment_count: int
    total_revenue: Decimal
    failed_amount: Decimal
    successful_payments: int
    failed_payments: int
    success_rate: float = Field(default=0.0)

    def __init__(self, **data):
        super().__init__(**data)
        self.success_rate = (
            self.successful_payments / max(self.payment_count, 1) * 100
            if self.payment_count > 0
            else 0
        )


class SubscriptionStats(BaseModel):
    """Subscription statistics response"""

    total_subscriptions: int
    active_subscriptions: int
    canceled_subscriptions: int
    past_due_subscriptions: int
    avg_subscription_amount: Decimal | None
    churn_rate: float = Field(default=0.0)

    def __init__(self, **data):
        super().__init__(**data)
        self.churn_rate = (
            self.canceled_subscriptions / max(self.total_subscriptions, 1) * 100
            if self.total_subscriptions > 0
            else 0
        )


class PlanResponse(BaseModel):
    """Available plan response"""
    id: int
    name: str
    price_monthly: Optional[Decimal]
    price_yearly: Optional[Decimal]
    currency: str
    max_channels: Optional[int]
    max_posts_per_month: Optional[int]
    features: List[str]
    is_active: bool


class SubscriptionCreateRequest(BaseModel):
    """Create subscription request"""
    user_id: int
    plan_id: int  # Changed from str to int to match SubscriptionCreate
    payment_method_id: str  # Stripe payment method ID
    trial_days: Optional[int] = None


class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request"""
    user_id: int
    immediate: bool = False


# Initialize router
router = APIRouter(prefix="/api/payments", tags=["payments"])
security = HTTPBearer()


# Dependency to get payment service
async def get_payment_service() -> PaymentService:
    """Get payment service with Stripe adapter"""
    from infra.db.connection_manager import db_manager
    
    # Initialize database if not already done
    if not db_manager._pool:
        await db_manager.initialize()
    
    stripe_adapter = StripeAdapter(
        api_key=settings.STRIPE_SECRET_KEY.get_secret_value() if settings.STRIPE_SECRET_KEY else "",
        webhook_secret=settings.STRIPE_WEBHOOK_SECRET.get_secret_value() if settings.STRIPE_WEBHOOK_SECRET else ""
    )
    
    # Get the underlying asyncpg pool from the optimized manager
    pool = await db_manager._pool.initialize() if db_manager._pool else None
    if not pool:
        raise RuntimeError("Failed to initialize database pool")
        
    payment_repo = AsyncpgPaymentRepository(pool)
    payment_service = PaymentService(payment_repo)
    payment_service.register_adapter(stripe_adapter)
    return payment_service


@router.post("/create-subscription", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionCreateRequest,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create a new subscription with Stripe"""
    try:
        # Create subscription using payment service
        subscription_data = SubscriptionCreate(
            plan_id=request.plan_id,
            billing_cycle=BillingCycle.MONTHLY,  # Default to monthly
            payment_method_id=request.payment_method_id,
            trial_days=request.trial_days
        )
        
        result = await payment_service.create_subscription(request.user_id, subscription_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Process webhook through payment service
        result = await payment_service.process_webhook("stripe", payload, signature)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}/subscription")
async def get_user_subscription(
    user_id: int,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's current subscription"""
    try:
        subscription = await payment_service.get_user_subscription(user_id)
        if not subscription:
            return {"subscription": None}
        
        return {"subscription": subscription}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Cancel user's subscription"""
    try:
        result = await payment_service.cancel_user_subscription(
            request.user_id, 
            immediate=request.immediate
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans", response_model=List[PlanResponse])
async def get_available_plans(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get available subscription plans with pricing"""
    try:
        plans = await payment_service.get_available_plans()
        return plans
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/history")
async def get_payment_history(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get user's payment history"""
    try:
        history = await payment_service.get_payment_history(
            user_id, 
            limit=limit, 
            offset=offset
        )
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/payments", response_model=PaymentStats)
async def get_payment_stats(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get payment statistics"""
    try:
        stats = await payment_service.get_payment_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/subscriptions", response_model=SubscriptionStats)
async def get_subscription_stats(
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Get subscription statistics"""
    try:
        stats = await payment_service.get_subscription_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def payment_status():
    """Get payment system status"""
    return {
        "status": "ok", 
        "message": "Payment system is operational",
        "stripe_configured": bool(settings.STRIPE_SECRET_KEY),
        "test_mode": settings.STRIPE_TEST_MODE
    }
