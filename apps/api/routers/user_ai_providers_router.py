"""
User AI Providers API Router
==============================

Endpoints for managing user's AI provider API keys.
"""

import logging
from typing import Any
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container
from core.services.ai.provider_registry import AIProviderRegistry
from core.services.ai.models import AIProviderConfig, AIMessage

logger = logging.getLogger(__name__)

router = APIRouter(tags=["User AI Providers"])


# =====================================
# Request/Response Models
# =====================================


class AddProviderRequest(BaseModel):
    """Request to add AI provider."""
    provider: str = Field(..., description="Provider name: openai, claude, gemini, etc.")
    api_key: str = Field(..., description="API key for the provider")
    model: str = Field(..., description="Preferred model")
    set_as_default: bool = Field(False, description="Set as default provider")
    monthly_budget: float | None = Field(None, description="Optional monthly budget in USD")


class UpdateProviderRequest(BaseModel):
    """Request to update AI provider settings."""
    model: str | None = Field(None, description="Update preferred model")
    monthly_budget: float | None = Field(None, description="Update monthly budget")
    set_as_default: bool | None = Field(None, description="Set as default")


class ProviderResponse(BaseModel):
    """AI provider response."""
    provider: str
    model: str
    is_active: bool
    is_default: bool
    monthly_budget: float | None
    current_month_spent: float
    api_key_preview: str  # First 10 chars + ...


# =====================================
# Dependency Providers
# =====================================


async def get_user_ai_providers_repo():
    """Get User AI Providers Repository from DI container."""
    container = get_container()
    return await container.database.user_ai_providers_repo()


# =====================================
# Endpoints: Available Providers
# =====================================


@router.get("/providers/available")
async def list_available_providers() -> dict[str, Any]:
    """
    List all supported AI providers and their available models.
    
    Returns information about OpenAI, Claude, Gemini, etc.
    """
    try:
        providers = AIProviderRegistry.list_providers()
        
        return {
            "providers": providers,
            "total": len(providers),
        }
    except Exception as e:
        logger.error(f"Failed to list available providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list providers",
        )


# =====================================
# Endpoints: User's Providers
# =====================================


@router.get("/providers/mine")
async def list_my_providers(
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
) -> dict[str, Any]:
    """
    List user's configured AI providers.
    
    Returns providers with API key preview (not full key).
    """
    try:
        providers = await repo.list_user_providers(user_id, active_only=True)
        
        # Format response (don't expose full API keys)
        formatted = []
        for p in providers:
            formatted.append({
                "provider": p["provider_name"],
                "model": p["model_preference"],
                "is_active": p["is_active"],
                "is_default": p["is_default"],
                "monthly_budget": float(p["monthly_budget_usd"]) if p["monthly_budget_usd"] else None,
                "current_month_spent": float(p["current_month_spent_usd"]),
                "created_at": p["created_at"].isoformat(),
            })
        
        return {
            "providers": formatted,
            "total": len(formatted),
        }
    except Exception as e:
        logger.error(f"Failed to list user providers for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list providers",
        )


@router.post("/providers/add", response_model=ProviderResponse)
async def add_provider(
    request: AddProviderRequest,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
) -> ProviderResponse:
    """
    Add a new AI provider with user's API key.
    
    Validates the API key by testing it before saving.
    """
    try:
        # Validate provider exists
        if not AIProviderRegistry.is_provider_available(request.provider):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown provider: {request.provider}",
            )
        
        # Validate API key by testing it
        provider_class = AIProviderRegistry.get_provider_class(request.provider)
        test_provider = provider_class(
            AIProviderConfig(
                api_key=request.api_key,
                model=request.model,
            )
        )
        
        # Test connection
        logger.info(f"Testing API key for {request.provider}...")
        is_valid = await test_provider.test_connection()
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid API key for {request.provider}",
            )
        
        logger.info(f"✅ API key validated for {request.provider}")
        
        # Save to database (encrypted)
        provider_data = await repo.add_provider(
            user_id=user_id,
            provider_name=request.provider,
            api_key=request.api_key,
            model_preference=request.model,
            is_default=request.set_as_default,
            monthly_budget_usd=Decimal(str(request.monthly_budget)) if request.monthly_budget else None,
        )
        
        return ProviderResponse(
            provider=provider_data["provider_name"],
            model=provider_data["model_preference"],
            is_active=provider_data["is_active"],
            is_default=provider_data["is_default"],
            monthly_budget=float(provider_data["monthly_budget_usd"]) if provider_data["monthly_budget_usd"] else None,
            current_month_spent=float(provider_data["current_month_spent_usd"]),
            api_key_preview=request.api_key[:10] + "...",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add provider {request.provider} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add provider: {str(e)}",
        )


@router.put("/providers/{provider_name}/set-default")
async def set_default_provider(
    provider_name: str,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
) -> dict[str, Any]:
    """Set a provider as default."""
    try:
        # Get existing provider
        existing = await repo.get_provider(user_id, provider_name)
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_name} not found",
            )
        
        # Update as default (repo handles unsetting others)
        await repo.add_provider(
            user_id=user_id,
            provider_name=provider_name,
            api_key="dummy",  # Will be ignored on conflict update
            model_preference=existing["model_preference"],
            is_default=True,
        )
        
        return {
            "success": True,
            "provider": provider_name,
            "message": f"Set {provider_name} as default",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set default provider for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update provider",
        )


@router.delete("/providers/{provider_name}")
async def remove_provider(
    provider_name: str,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
) -> dict[str, Any]:
    """Remove an AI provider."""
    try:
        removed = await repo.remove_provider(user_id, provider_name)
        
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {provider_name} not found",
            )
        
        return {
            "success": True,
            "provider": provider_name,
            "message": f"Removed {provider_name}",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove provider for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove provider",
        )


@router.get("/providers/{provider_name}/spending")
async def get_provider_spending(
    provider_name: str,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
) -> dict[str, Any]:
    """Get spending details for a provider."""
    try:
        within_budget, budget, spent = await repo.check_budget(user_id, provider_name)
        
        return {
            "provider": provider_name,
            "current_month_spent": float(spent) if spent else 0.0,
            "monthly_budget": float(budget) if budget else None,
            "within_budget": within_budget,
            "budget_remaining": float(budget - spent) if budget and spent else None,
        }
        
    except Exception as e:
        logger.error(f"Failed to get spending for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get spending data",
        )
