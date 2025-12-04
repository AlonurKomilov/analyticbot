"""
Credit System API Endpoints

Handles credit balance, transactions, purchases, and rewards.
"""

import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user
from apps.di import get_container
from infra.db.repositories.credit_repository import CreditRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credits", tags=["Credits"])


# ============================================
# PYDANTIC MODELS
# ============================================


class CreditBalanceResponse(BaseModel):
    """User's credit balance response"""

    balance: float
    lifetime_earned: float
    lifetime_spent: float
    daily_streak: int
    can_claim_daily: bool


class CreditTransactionResponse(BaseModel):
    """Credit transaction record"""

    id: str
    amount: float
    balance_after: float
    type: str
    category: str | None
    description: str | None
    created_at: str


class TransactionListResponse(BaseModel):
    """Paginated transaction list"""

    transactions: list[CreditTransactionResponse]
    total: int
    page: int
    limit: int


class CreditPackageResponse(BaseModel):
    """Credit package for purchase"""

    id: int
    name: str
    slug: str
    credits: float
    bonus_credits: float
    total_credits: float
    price: float
    currency: str
    description: str | None
    is_popular: bool


class CreditServiceResponse(BaseModel):
    """Service that costs credits"""

    id: int
    service_key: str
    name: str
    description: str | None
    credit_cost: float
    category: str
    icon: str | None


class SpendCreditsRequest(BaseModel):
    """Request to spend credits on a service"""

    service_key: str = Field(..., description="Service to purchase")
    reference_id: str | None = Field(None, description="Reference ID for tracking")


class SpendCreditsResponse(BaseModel):
    """Response after spending credits"""

    success: bool
    credits_spent: float
    new_balance: float
    service: str
    transaction_id: str


class DailyRewardResponse(BaseModel):
    """Daily reward claim response"""

    success: bool
    credits_earned: float
    streak: int
    new_balance: float
    message: str


class CheckAffordResponse(BaseModel):
    """Check if user can afford a service"""

    can_afford: bool
    balance: float
    cost: float
    shortfall: float


# ============================================
# DEPENDENCY
# ============================================


async def get_db_pool():
    """Get database pool from DI container"""
    container = get_container()
    try:
        pool = await container.database.asyncpg_pool()
        return pool
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(status_code=500, detail="Database pool not available")


async def get_credit_repository(pool=Depends(get_db_pool)) -> CreditRepository:
    """Get credit repository instance"""
    return CreditRepository(pool)


# ============================================
# BALANCE ENDPOINTS
# ============================================


@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get current user's credit balance"""
    user_id = int(current_user["id"])

    balance_info = await credit_repo.get_balance(user_id)

    # Check if can claim daily reward
    from datetime import datetime

    can_claim = True
    if balance_info.get("last_daily_reward_at"):
        last_claim = balance_info["last_daily_reward_at"].date()
        if last_claim == datetime.utcnow().date():
            can_claim = False

    return CreditBalanceResponse(
        balance=float(balance_info["balance"]),
        lifetime_earned=float(balance_info["lifetime_earned"]),
        lifetime_spent=float(balance_info["lifetime_spent"]),
        daily_streak=balance_info["daily_streak"],
        can_claim_daily=can_claim,
    )


@router.post("/daily-reward", response_model=DailyRewardResponse)
async def claim_daily_reward(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Claim daily login reward"""
    user_id = int(current_user["id"])

    result = await credit_repo.claim_daily_reward(user_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daily reward already claimed today. Come back tomorrow!",
        )

    # Get new balance
    balance_info = await credit_repo.get_balance(user_id)

    return DailyRewardResponse(
        success=True,
        credits_earned=result["credits_earned"],
        streak=result["streak"],
        new_balance=float(balance_info["balance"]),
        message=f"🎉 Day {result['streak']} streak! You earned {result['credits_earned']} credits!",
    )


# ============================================
# TRANSACTION ENDPOINTS
# ============================================


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, description="Filter by transaction type"),
    category: str | None = Query(None, description="Filter by category"),
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get user's credit transaction history"""
    user_id = int(current_user["id"])
    offset = (page - 1) * limit

    transactions = await credit_repo.get_transactions(
        user_id=user_id,
        limit=limit,
        offset=offset,
        transaction_type=type,
        category=category,
    )

    total = await credit_repo.get_transaction_count(user_id)

    return TransactionListResponse(
        transactions=[
            CreditTransactionResponse(
                id=str(t["id"]),
                amount=float(t["amount"]),
                balance_after=float(t["balance_after"]),
                type=t["type"],
                category=t["category"],
                description=t["description"],
                created_at=t["created_at"].isoformat(),
            )
            for t in transactions
        ],
        total=total,
        page=page,
        limit=limit,
    )


# ============================================
# SPENDING ENDPOINTS
# ============================================


@router.post("/spend", response_model=SpendCreditsResponse)
async def spend_credits(
    request: SpendCreditsRequest,
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Spend credits on a service"""
    user_id = int(current_user["id"])

    # Get service cost
    service = await credit_repo.get_service_by_key(request.service_key)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{request.service_key}' not found",
        )

    cost = Decimal(str(service["credit_cost"]))

    # Check balance
    if not await credit_repo.can_afford(user_id, cost):
        balance = await credit_repo.get_balance(user_id)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": "Insufficient credits",
                "balance": float(balance["balance"]),
                "cost": float(cost),
                "shortfall": float(cost - balance["balance"]),
            },
        )

    try:
        transaction = await credit_repo.spend_credits(
            user_id=user_id,
            amount=cost,
            service_key=request.service_key,
            reference_id=request.reference_id,
        )

        return SpendCreditsResponse(
            success=True,
            credits_spent=float(cost),
            new_balance=float(transaction["balance_after"]),
            service=service["name"],
            transaction_id=str(transaction["id"]),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e),
        )


@router.get("/check/{service_key}", response_model=CheckAffordResponse)
async def check_afford(
    service_key: str,
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Check if user can afford a service"""
    user_id = int(current_user["id"])

    service = await credit_repo.get_service_by_key(service_key)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_key}' not found",
        )

    cost = Decimal(str(service["credit_cost"]))
    balance_info = await credit_repo.get_balance(user_id)
    balance = Decimal(str(balance_info["balance"]))

    return CheckAffordResponse(
        can_afford=balance >= cost,
        balance=float(balance),
        cost=float(cost),
        shortfall=float(max(Decimal("0"), cost - balance)),
    )


# ============================================
# PACKAGES & SERVICES ENDPOINTS
# ============================================


@router.get("/packages", response_model=list[CreditPackageResponse])
async def get_packages(
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get available credit packages for purchase"""
    packages = await credit_repo.get_packages(active_only=True)

    return [
        CreditPackageResponse(
            id=p["id"],
            name=p["name"],
            slug=p["slug"],
            credits=float(p["credits"]),
            bonus_credits=float(p["bonus_credits"] or 0),
            total_credits=float(p["credits"]) + float(p["bonus_credits"] or 0),
            price=float(p["price"]),
            currency=p["currency"],
            description=p["description"],
            is_popular=p["is_popular"],
        )
        for p in packages
    ]


@router.get("/services", response_model=list[CreditServiceResponse])
async def get_services(
    category: str | None = Query(None, description="Filter by category"),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get available services that cost credits"""
    services = await credit_repo.get_services(active_only=True, category=category)

    return [
        CreditServiceResponse(
            id=s["id"],
            service_key=s["service_key"],
            name=s["name"],
            description=s["description"],
            credit_cost=float(s["credit_cost"]),
            category=s["category"],
            icon=s["icon"],
        )
        for s in services
    ]


@router.get("/services/{service_key}", response_model=CreditServiceResponse)
async def get_service(
    service_key: str,
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get a specific service by key"""
    service = await credit_repo.get_service_by_key(service_key)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_key}' not found",
        )

    return CreditServiceResponse(
        id=service["id"],
        service_key=service["service_key"],
        name=service["name"],
        description=service["description"],
        credit_cost=float(service["credit_cost"]),
        category=service["category"],
        icon=None,
    )
