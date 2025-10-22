"""
Shared Pydantic models for predictive insights endpoints.

This module contains request/response models used across
predictive analytics and intelligence endpoints.
"""

from pydantic import BaseModel, Field


# Request Models
class PredictionRequest(BaseModel):
    """Request for generating predictions and forecasts"""

    channel_ids: list[int]
    prediction_type: str = Field(
        ..., description="Type of prediction (growth, engagement, reach, views)"
    )
    forecast_days: int = Field(30, ge=1, le=365, description="Days to forecast ahead")
    confidence_level: float = Field(
        0.95, ge=0.8, le=0.99, description="Confidence level for predictions"
    )


class ContextualIntelligenceRequest(BaseModel):
    """Request for contextual intelligence analysis"""

    channel_id: int
    intelligence_context: list[str] = Field(
        default=["temporal", "environmental"],
        description="Types of intelligence context to analyze",
    )
    analysis_period_days: int = Field(30, ge=7, le=365, description="Analysis period in days")
    prediction_horizon_days: int = Field(7, ge=1, le=90, description="Prediction horizon in days")
    include_explanations: bool = Field(True, description="Include natural language explanations")


class CrossChannelIntelligenceRequest(BaseModel):
    """Request for cross-channel intelligence analysis"""

    channel_ids: list[int] = Field(..., description="Channel IDs to analyze (2-10 channels)")
    correlation_depth_days: int = Field(
        60, ge=14, le=180, description="Analysis depth for correlations"
    )
    include_competitive_intelligence: bool = Field(True, description="Include competitive analysis")
