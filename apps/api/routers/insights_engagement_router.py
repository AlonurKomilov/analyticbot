"""
Engagement and audience insights endpoints.
Handles engagement metrics, audience analysis, and trending content.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime

from core.security_engine.auth_handler import get_current_user
from core.models.user import User
from core.models.analytics import EngagementMetrics, AudienceInsights, PostListResponse
from core.services.analytics.engagement_service import EngagementService
from apps.shared.dependencies import get_analytics_service

router = APIRouter(prefix="/insights/engagement", tags=["insights-engagement"])

# TODO: Migrate engagement endpoints from analytics_insights_router.py
# - /channels/{channel_id}/engagement
# - /channels/{channel_id}/audience
# - /channels/{channel_id}/trending