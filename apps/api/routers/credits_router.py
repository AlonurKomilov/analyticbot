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


# ============================================
# REFERRAL ENDPOINTS
# ============================================


class ReferralStatsResponse(BaseModel):
    """User's referral statistics"""
    referral_code: str | None
    total_referrals: int
    total_credits_earned: float
    referral_link: str  # Web registration link
    bot_referral_link: str  # Telegram bot deep link
    recent_referrals: list[dict]


class ApplyReferralRequest(BaseModel):
    """Apply a referral code"""
    referral_code: str = Field(..., min_length=6, max_length=20)


class ApplyReferralResponse(BaseModel):
    """Response after applying referral"""
    success: bool
    message: str
    referrer_username: str | None
    bonus_received: float


@router.get("/referral", response_model=ReferralStatsResponse)
async def get_referral_stats(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get user's referral code and statistics"""
    user_id = int(current_user["id"])
    stats = await credit_repo.get_referral_stats(user_id)
    
    # Build referral links
    import os
    base_url = os.getenv("FRONTEND_URL", "https://analyticbot.org")
    bot_username = os.getenv("TELEGRAM_BOT_USERNAME", "abccontrol_bot")
    
    referral_link = f"{base_url}/register?ref={stats['referral_code']}" if stats['referral_code'] else ""
    bot_referral_link = f"https://t.me/{bot_username}?start=ref_{stats['referral_code']}" if stats['referral_code'] else ""
    
    return ReferralStatsResponse(
        referral_code=stats["referral_code"],
        total_referrals=stats["total_referrals"],
        total_credits_earned=stats["total_credits_earned"],
        referral_link=referral_link,
        bot_referral_link=bot_referral_link,
        recent_referrals=stats["recent_referrals"],
    )


@router.post("/referral/apply", response_model=ApplyReferralResponse)
async def apply_referral_code(
    request: ApplyReferralRequest,
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Apply a referral code (for new users who didn't use one during signup)"""
    user_id = int(current_user["id"])
    
    try:
        result = await credit_repo.apply_referral(
            referred_user_id=user_id,
            referral_code=request.referral_code,
        )
        
        return ApplyReferralResponse(
            success=True,
            message=f"Referral code applied! You received {result['referred_bonus']} bonus credits!",
            referrer_username=result["referrer_username"],
            bonus_received=result["referred_bonus"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================
# ACHIEVEMENTS ENDPOINTS
# ============================================


class AchievementResponse(BaseModel):
    """Achievement definition"""
    achievement_key: str
    name: str
    description: str | None
    credit_reward: float
    icon: str | None
    category: str
    is_earned: bool
    is_claimable: bool = False  # Can be claimed (requirements met but not yet earned)
    current_value: int
    required_value: int | None
    progress_percent: int


class AchievementProgressResponse(BaseModel):
    """User's achievement progress"""
    total_achievements: int
    earned_count: int
    claimable_count: int = 0  # Number of achievements ready to claim
    completion_percent: int
    achievements: list[AchievementResponse]


class EarnedAchievementResponse(BaseModel):
    """Achievement that was just earned"""
    achievement_key: str
    name: str
    description: str | None
    credits_awarded: float
    icon: str | None
    category: str


@router.get("/achievements", response_model=AchievementProgressResponse)
async def get_achievements(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get user's achievement progress with claimable status"""
    user_id = int(current_user["id"])
    progress = await credit_repo.get_achievement_progress(user_id)
    
    # Get claimable achievements to mark them
    claimable = await credit_repo.get_claimable_achievements(user_id)
    claimable_keys = {a["achievement_key"] for a in claimable}
    
    completion_percent = int(progress["earned_count"] / progress["total_achievements"] * 100) if progress["total_achievements"] > 0 else 0
    
    return AchievementProgressResponse(
        total_achievements=progress["total_achievements"],
        earned_count=progress["earned_count"],
        claimable_count=len(claimable_keys),
        completion_percent=completion_percent,
        achievements=[
            AchievementResponse(
                achievement_key=a["achievement_key"],
                name=a["name"],
                description=a["description"],
                credit_reward=a["credit_reward"],
                icon=a["icon"],
                category=a["category"],
                is_earned=a["is_earned"],
                is_claimable=a["achievement_key"] in claimable_keys,
                current_value=a["current_value"],
                required_value=a["required_value"],
                progress_percent=a["progress_percent"],
            )
            for a in progress["achievements"]
        ],
    )


@router.get("/achievements/earned", response_model=list[EarnedAchievementResponse])
async def get_earned_achievements(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get list of achievements user has earned"""
    user_id = int(current_user["id"])
    achievements = await credit_repo.get_user_achievements(user_id)
    
    return [
        EarnedAchievementResponse(
            achievement_key=a["achievement_key"],
            name=a["achievement_name"],
            description=a["description"],
            credits_awarded=float(a["credits_awarded"]),
            icon=a["icon"],
            category=a["category"],
        )
        for a in achievements
    ]


class ClaimAchievementRequest(BaseModel):
    """Request to claim an achievement"""
    achievement_key: str


class ClaimAchievementResponse(BaseModel):
    """Response after claiming an achievement"""
    success: bool
    message: str
    achievement: EarnedAchievementResponse | None = None
    new_balance: float | None = None


@router.post("/achievements/claim", response_model=ClaimAchievementResponse)
async def claim_achievement(
    request: ClaimAchievementRequest,
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """
    Claim an achievement that user has reached but not yet collected.
    User must meet the achievement requirements to claim.
    """
    user_id = int(current_user["id"])
    
    # Check if user can claim this achievement
    result = await credit_repo.claim_achievement(user_id, request.achievement_key)
    
    if result is None:
        return ClaimAchievementResponse(
            success=False,
            message="Achievement not found or already claimed",
        )
    
    if result.get("error"):
        return ClaimAchievementResponse(
            success=False,
            message=result["error"],
        )
    
    return ClaimAchievementResponse(
        success=True,
        message=f"🎉 Achievement unlocked: {result['name']}! +{result['credits_awarded']} credits",
        achievement=EarnedAchievementResponse(
            achievement_key=result["achievement_key"],
            name=result["name"],
            description=result["description"],
            credits_awarded=result["credits_awarded"],
            icon=result["icon"],
            category=result["category"],
        ),
        new_balance=result.get("new_balance"),
    )


class ClaimableAchievementResponse(BaseModel):
    """Achievement that can be claimed"""
    achievement_key: str
    name: str
    description: str | None
    credit_reward: float
    icon: str | None
    category: str
    current_value: int
    required_value: int


@router.get("/achievements/claimable", response_model=list[ClaimableAchievementResponse])
async def get_claimable_achievements(
    current_user: dict = Depends(get_current_user),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get list of achievements that user can claim (requirements met but not yet claimed)"""
    user_id = int(current_user["id"])
    claimable = await credit_repo.get_claimable_achievements(user_id)
    
    return [
        ClaimableAchievementResponse(
            achievement_key=a["achievement_key"],
            name=a["name"],
            description=a["description"],
            credit_reward=float(a["credit_reward"]),
            icon=a["icon"],
            category=a["category"],
            current_value=a["current_value"],
            required_value=a["required_value"],
        )
        for a in claimable
    ]


# ============================================
# LEADERBOARD ENDPOINT
# ============================================


class LeaderboardEntryResponse(BaseModel):
    """Leaderboard entry - privacy-friendly, shows achievements not credits"""
    rank: int
    user_id: int
    username: str | None
    achievements_earned: int
    total_channels: int
    current_streak: int


@router.get("/leaderboard", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    credit_repo: CreditRepository = Depends(get_credit_repository),
):
    """Get achievements leaderboard (privacy-friendly - no credit amounts shown)"""
    entries = await credit_repo.get_leaderboard(limit=limit)
    
    return [
        LeaderboardEntryResponse(
            rank=i + 1,
            user_id=e["id"],
            username=e["username"],
            achievements_earned=int(e.get("achievements_earned") or 0),
            total_channels=int(e.get("total_channels") or 0),
            current_streak=int(e.get("current_streak") or 0),
        )
        for i, e in enumerate(entries)
    ]
