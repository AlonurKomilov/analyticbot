"""
Centralized Mock Email Service

Consolidated from scattered mock email implementations.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Any

from ..base import BaseMockService, mock_metrics
from ..protocols import EmailServiceProtocol

logger = logging.getLogger(__name__)

# Email constants
EMAIL_DELAY_MS = 50
EMAIL_SUCCESS_RATE = 0.98


class MockEmailService(BaseMockService, EmailServiceProtocol):
    """Centralized mock email service for all testing needs"""

    def __init__(self):
        super().__init__("MockEmailService")
        self.sent_emails = []
        self.failed_emails = []
        self.email_templates = {}

    def get_service_name(self) -> str:
        return self.service_name

    async def health_check(self) -> dict[str, Any]:
        """Mock email service health check"""
        mock_metrics.record_call(self.service_name, "health_check")

        base_health = await super().health_check()
        base_health.update(
            {
                "emails_sent": len(self.sent_emails),
                "failed_emails": len(self.failed_emails),
                "success_rate": EMAIL_SUCCESS_RATE,
                "templates_loaded": len(self.email_templates),
            }
        )
        return base_health

    async def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
        """Send a mock email"""
        mock_metrics.record_call(self.service_name, "send_email")
        await asyncio.sleep(EMAIL_DELAY_MS / 1000)

        # Simulate occasional failures
        will_succeed = random.random() < EMAIL_SUCCESS_RATE

        email_data = {
            "to": to,
            "subject": subject,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
            "from": kwargs.get("from", "noreply@analyticbot.com"),
            "cc": kwargs.get("cc", []),
            "bcc": kwargs.get("bcc", []),
            "attachments": kwargs.get("attachments", []),
            "template": kwargs.get("template"),
            "success": will_succeed,
        }

        if will_succeed:
            self.sent_emails.append(email_data)
            logger.info(f"Mock email sent to {to}: {subject}")
        else:
            email_data["error"] = random.choice(
                [
                    "invalid_recipient",
                    "smtp_error",
                    "rate_limit_exceeded",
                    "template_error",
                ]
            )
            self.failed_emails.append(email_data)
            logger.warning(f"Mock email failed to {to}: {email_data['error']}")

        return will_succeed

    async def send_template_email(
        self, to: str, template_name: str, variables: dict[str, Any]
    ) -> bool:
        """Send email using a template"""
        mock_metrics.record_call(self.service_name, "send_template_email")

        if template_name not in self.email_templates:
            # Create a basic template if it doesn't exist
            self.email_templates[template_name] = {
                "subject": f"Template: {template_name}",
                "body": "Mock template email with variables: {variables}",
            }

        template = self.email_templates[template_name]
        subject = template["subject"].format(**variables)
        body = template["body"].format(variables=variables)

        return await self.send_email(to, subject, body, template=template_name)

    async def send_bulk_email(
        self, recipients: list[str], subject: str, body: str
    ) -> dict[str, Any]:
        """Send bulk emails"""
        mock_metrics.record_call(self.service_name, "send_bulk_email")

        results = {
            "total": len(recipients),
            "successful": 0,
            "failed": 0,
            "results": [],
        }

        for recipient in recipients:
            success = await self.send_email(recipient, subject, body)
            results["results"].append({"recipient": recipient, "success": success})

            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1

        return results

    async def get_email_history(self, limit: int = 50) -> dict[str, Any]:
        """Get email sending history"""
        mock_metrics.record_call(self.service_name, "get_email_history")

        all_emails = self.sent_emails + self.failed_emails
        all_emails.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "emails": all_emails[:limit],
            "total_sent": len(self.sent_emails),
            "total_failed": len(self.failed_emails),
            "success_rate": len(self.sent_emails) / max(1, len(all_emails)),
        }

    def add_template(self, name: str, subject: str, body: str):
        """Add an email template"""
        self.email_templates[name] = {
            "subject": subject,
            "body": body,
            "created": datetime.utcnow().isoformat(),
        }
        logger.info(f"Added email template: {name}")

    def reset(self) -> None:
        """Reset mock service state"""
        super().reset()
        self.sent_emails.clear()
        self.failed_emails.clear()
        self.email_templates.clear()

    def get_sent_emails(self) -> list[dict[str, Any]]:
        """Get list of sent emails for testing verification"""
        return self.sent_emails.copy()

    def get_failed_emails(self) -> list[dict[str, Any]]:
        """Get list of failed emails for testing verification"""
        return self.failed_emails.copy()
