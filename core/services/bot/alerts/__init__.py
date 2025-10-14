"""
Alert Service Module

Clean Architecture: Framework-agnostic alert services
"""

from core.services.bot.alerts.alert_condition_evaluator import AlertConditionEvaluator
from core.services.bot.alerts.alert_event_manager import AlertEventManager
from core.services.bot.alerts.alert_rule_manager import AlertRuleManager
from core.services.bot.alerts.protocols import (
    AlertNotificationPort,
    AlertRepository,
)

__all__ = [
    "AlertRepository",
    "AlertNotificationPort",
    "AlertConditionEvaluator",
    "AlertRuleManager",
    "AlertEventManager",
]
