"""
Mock Email Service
Implements EmailServiceProtocol for demo mode
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any

from core.protocols import EmailServiceProtocol
from tests.mocks.constants import DEMO_API_DELAY_MS

logger = logging.getLogger(__name__)


class MockEmailService(EmailServiceProtocol):
    """Mock email service for demo mode"""

    def __init__(self):
        self.service_name = "MockEmailService"
        self.sent_emails = []
        logger.info(f"Initialized {self.service_name}")

    def get_service_name(self) -> str:
        return self.service_name

    async def health_check(self) -> dict[str, Any]:
        """Mock service health check"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
            "emails_sent": len(self.sent_emails),
        }

    async def send_email(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        """Mock send email"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        email_id = str(uuid.uuid4())
        email_record = {
            "id": email_id,
            "to": to,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent",
        }

        self.sent_emails.append(email_record)
        logger.info(f"📧 Mock email sent to {to}: {subject}")

        return True

    async def send_template_email(
        self, to: str, template_id: str, variables: dict[str, Any]
    ) -> bool:
        """Mock send templated email"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        subject = f"Template {template_id} Email"
        body = f"Mock templated email with variables: {variables}"

        return await self.send_email(to, subject, body)

    async def verify_email_delivery(self, email_id: str) -> dict[str, Any]:
        """Mock check email delivery status"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Find email in sent list
        email = next((e for e in self.sent_emails if e["id"] == email_id), None)

        if email:
            return {
                "email_id": email_id,
                "status": "delivered",
                "delivered_at": datetime.utcnow().isoformat(),
                "recipient": email["to"],
                "mock": True,
            }
        else:
            return {"email_id": email_id, "status": "not_found", "mock": True}
