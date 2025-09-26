"""
Mock Telegram Service for centralized mock services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import random

from .base_service import BaseMockService


class MockTelegramService(BaseMockService):
    """Mock Telegram Service for testing and development"""
    
    def get_service_name(self) -> str:
        return "MockTelegramService"
    
    def send_message(self, chat_id: int, text: str, **kwargs) -> Dict[str, Any]:
        """Mock send message to Telegram"""
        return {
            "ok": True,
            "result": {
                "message_id": random.randint(1000, 9999),
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "AnalyticBot",
                    "username": "analyticbot"
                },
                "chat": {
                    "id": chat_id,
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": text
            }
        }
    
    def send_photo(self, chat_id: int, photo: str, caption: str = None) -> Dict[str, Any]:
        """Mock send photo to Telegram"""
        return {
            "ok": True,
            "result": {
                "message_id": random.randint(1000, 9999),
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "AnalyticBot",
                    "username": "analyticbot"
                },
                "chat": {
                    "id": chat_id,
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "photo": [
                    {
                        "file_id": "mock_file_id_123",
                        "file_unique_id": "mock_unique_123",
                        "width": 1280,
                        "height": 720,
                        "file_size": 85000
                    }
                ],
                "caption": caption
            }
        }
    
    def send_document(self, chat_id: int, document: str, caption: str = None) -> Dict[str, Any]:
        """Mock send document to Telegram"""
        return {
            "ok": True,
            "result": {
                "message_id": random.randint(1000, 9999),
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "AnalyticBot",
                    "username": "analyticbot"
                },
                "chat": {
                    "id": chat_id,
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "document": {
                    "file_name": "analytics_report.pdf",
                    "mime_type": "application/pdf",
                    "file_id": "mock_doc_file_id_456",
                    "file_unique_id": "mock_doc_unique_456",
                    "file_size": 250000
                },
                "caption": caption
            }
        }
    
    def get_chat(self, chat_id: int) -> Dict[str, Any]:
        """Mock get chat information"""
        return {
            "ok": True,
            "result": {
                "id": chat_id,
                "type": "private",
                "username": f"user_{abs(chat_id)}",
                "first_name": f"User {abs(chat_id)}",
                "last_name": "Demo"
            }
        }
    
    def get_me(self) -> Dict[str, Any]:
        """Mock get bot information"""
        return {
            "ok": True,
            "result": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "AnalyticBot",
                "username": "analyticbot",
                "can_join_groups": True,
                "can_read_all_group_messages": True,
                "supports_inline_queries": False
            }
        }
    
    def set_webhook(self, url: str) -> Dict[str, Any]:
        """Mock set webhook"""
        return {
            "ok": True,
            "result": True,
            "description": f"Webhook was set to {url}"
        }
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """Mock get webhook info"""
        return {
            "ok": True,
            "result": {
                "url": "https://example.com/webhook",
                "has_custom_certificate": False,
                "pending_update_count": 0,
                "max_connections": 40
            }
        }
    
    def send_keyboard(self, chat_id: int, text: str, keyboard: List[List[Dict]]) -> Dict[str, Any]:
        """Mock send message with inline keyboard"""
        return {
            "ok": True,
            "result": {
                "message_id": random.randint(1000, 9999),
                "from": {
                    "id": 123456789,
                    "is_bot": True,
                    "first_name": "AnalyticBot",
                    "username": "analyticbot"
                },
                "chat": {
                    "id": chat_id,
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": text,
                "reply_markup": {
                    "inline_keyboard": keyboard
                }
            }
        }
    
    def answer_callback_query(self, callback_query_id: str, text: str = None) -> Dict[str, Any]:
        """Mock answer callback query"""
        return {
            "ok": True,
            "result": True
        }