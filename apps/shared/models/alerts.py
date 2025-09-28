"""
Shared Alert Models

These models are used across different layers of the application
to avoid circular imports between API and Bot services.
"""
from datetime import datetime
from pydantic import BaseModel


class AlertEvent(BaseModel):
    """Alert event model shared between API and Bot services"""
    id: str
    rule_id: str
    title: str
    message: str
    severity: str  # 'info', 'warning', 'error', 'success'
    timestamp: datetime
    channel_id: str
    triggered_value: float
    threshold: float


class AlertRule(BaseModel):
    """Alert rule configuration shared between services"""
    id: str
    channel_id: str
    metric: str
    condition: str  # 'greater_than', 'less_than', 'equals'
    threshold: float
    enabled: bool
    description: str