"""
Core statistical analysis endpoints.
Handles historical metrics, trends, and growth analysis.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime

from core.security_engine.auth_handler import get_current_user
from core.models.user import User
from core.models.analytics import HistoricalMetrics, GrowthAnalysis
from core.services.analytics.statistics_service import StatisticsService
from apps.shared.dependencies import get_analytics_service

router = APIRouter(prefix="/statistics/core", tags=["statistics-core"])

# TODO: Migrate core historical endpoints from analytics_core_router.py
# - Growth trends
# - Historical comparisons
# - Core metrics analysis