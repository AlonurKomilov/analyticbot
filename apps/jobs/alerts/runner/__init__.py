"""
Alert Runner Package
Modular alert detection and notification system

Main exports:
- AlertRunner: Main orchestration class
- AlertDetector: Detection logic for spike/quiet/growth alerts
- AlertNotifier: Telegram notification delivery
- main: CLI entry point
"""

from apps.jobs.alerts.runner.cli import main
from apps.jobs.alerts.runner.detector import AlertDetector
from apps.jobs.alerts.runner.notifier import AlertNotifier
from apps.jobs.alerts.runner.runner import AlertRunner

__all__ = ["AlertRunner", "AlertDetector", "AlertNotifier", "main"]
