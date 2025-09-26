"""
SMTP Email Service Implementation
================================

Simple SMTP email service for sending emails.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional


logger = logging.getLogger(__name__)


class SMTPEmailService:
    """SMTP Email Service for sending emails"""
    
    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.use_tls = use_tls
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        is_html: bool = False
    ) -> bool:
        """Send an email"""
        try:
            # Use configured user as default sender
            sender = from_email or self.smtp_user or "noreply@analyticbot.com"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # Attach body
            body_part = MIMEText(body, 'html' if is_html else 'plain')
            msg.attach(body_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                text = msg.as_string()
                server.sendmail(sender, to_emails, text)
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_verification_email(self, email: str, verification_token: str) -> bool:
        """Send email verification email"""
        verification_url = f"https://analyticbot.com/verify-email?token={verification_token}"
        
        subject = "Verify Your Email - AnalyticBot"
        body = f"""
        <h2>Welcome to AnalyticBot!</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <a href="{verification_url}">Verify Email Address</a>
        <p>If you didn't create an account, please ignore this email.</p>
        """
        
        return await self.send_email([email], subject, body, is_html=True)
    
    async def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"https://analyticbot.com/reset-password?token={reset_token}"
        
        subject = "Reset Your Password - AnalyticBot"
        body = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}">Reset Password</a>
        <p>If you didn't request a password reset, please ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        """
        
        return await self.send_email([email], subject, body, is_html=True)