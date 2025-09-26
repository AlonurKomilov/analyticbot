"""
Consolidated Mock Email Service

Migrated from scattered email mock implementations.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import random

from ..infrastructure.base import BaseMockService, mock_metrics
from ..constants import EMAIL_DELAY_MS, EMAIL_SUCCESS_RATE

logger = logging.getLogger(__name__)


class MockEmailService(BaseMockService):
    """Consolidated Mock Email Service"""
    
    def __init__(self):
        super().__init__("MockEmailService")
        self.sent_emails = []
        self.failed_emails = []
        self.email_templates = {}
        
    def get_service_name(self) -> str:
        return self.service_name
    
    async def health_check(self) -> Dict[str, Any]:
        """Email service health check"""
        mock_metrics.record_call(self.service_name, "health_check")
        
        base_health = await super().health_check()
        base_health.update({
            "emails_sent": len(self.sent_emails),
            "failed_emails": len(self.failed_emails),
            "success_rate": EMAIL_SUCCESS_RATE,
            "templates_loaded": len(self.email_templates)
        })
        return base_health
    
    async def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """Send a mock email"""
        mock_metrics.record_call(self.service_name, "send_email")
        await asyncio.sleep(EMAIL_DELAY_MS / 1000)
        
        will_succeed = random.random() < EMAIL_SUCCESS_RATE
        
        email_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
            "from": kwargs.get("from", "noreply@analyticbot.com"),
            "success": will_succeed
        }
        
        if will_succeed:
            self.sent_emails.append(email_data)
            logger.info(f"Mock email sent to {to}: {subject}")
        else:
            email_data["error"] = "mock_failure"
            self.failed_emails.append(email_data)
            logger.warning(f"Mock email failed to {to}")
        
        return will_succeed
    
    def reset(self) -> None:
        """Reset service state"""
        super().reset()
        self.sent_emails.clear()
        self.failed_emails.clear()
        self.email_templates.clear()