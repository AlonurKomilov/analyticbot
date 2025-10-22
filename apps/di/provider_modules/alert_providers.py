"""
Alert Service Providers

Factory functions for alert system services.
Includes alert condition evaluation, rule management, event tracking, and notifications.
"""

import logging

logger = logging.getLogger(__name__)


def create_alert_condition_evaluator(alert_repository=None, **kwargs):
    """Create alert condition evaluator (core alert logic)"""
    try:
        from core.services.bot.alerts import AlertConditionEvaluator

        if alert_repository is None:
            logger.warning("Cannot create alert condition evaluator: missing alert repository")
            return None

        return AlertConditionEvaluator(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert condition evaluator not available: {e}")
        return None


def create_alert_rule_manager(alert_repository=None, **kwargs):
    """Create alert rule manager (CRUD for alert rules)"""
    try:
        from core.services.bot.alerts import AlertRuleManager

        if alert_repository is None:
            logger.warning("Cannot create alert rule manager: missing alert repository")
            return None

        return AlertRuleManager(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert rule manager not available: {e}")
        return None


def create_alert_event_manager(alert_repository=None, **kwargs):
    """Create alert event manager (manages alert events and history)"""
    try:
        from core.services.bot.alerts import AlertEventManager

        if alert_repository is None:
            logger.warning("Cannot create alert event manager: missing alert repository")
            return None

        return AlertEventManager(alert_repository=alert_repository)
    except ImportError as e:
        logger.warning(f"Alert event manager not available: {e}")
        return None


def create_telegram_alert_notifier(bot=None, **kwargs):
    """Create Telegram alert notifier (sends alerts via Telegram)"""
    try:
        from apps.bot.adapters.alert_adapters import TelegramAlertNotifier

        if bot is None:
            logger.warning("Cannot create telegram alert notifier: missing bot")
            return None

        return TelegramAlertNotifier(bot=bot)
    except ImportError as e:
        logger.warning(f"Telegram alert notifier not available: {e}")
        return None
