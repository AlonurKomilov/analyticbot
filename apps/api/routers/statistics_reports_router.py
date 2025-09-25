"""
Statistical reports and analysis endpoints.
Handles report generation, comparisons, and trending analysis.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from core.security_engine.auth_handler import get_current_user
from core.models.user import User
from core.models.analytics import ReportData, ComparisonResult
from core.services.analytics.reports_service import ReportsService
from apps.shared.dependencies import get_analytics_service

router = APIRouter(prefix="/statistics/reports", tags=["statistics-reports"])

# TODO: Migrate report endpoints from analytics_insights_router.py
# - /reports/{channel_id}
# - /comparison/{channel_id}  
# - /trends/posts/top