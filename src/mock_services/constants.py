"""
Mock Services Constants

Centralized constants for all mock services.
Replaces the missing src.api_service.__mocks__.constants
"""

# Demo mode constants
DEFAULT_DEMO_CHANNEL_ID = "demo_channel_123"
DEMO_API_DELAY_MS = 100
DEMO_SUCCESS_RATE = 0.95
DEMO_POSTS_COUNT = 50
DEMO_METRICS_DAYS = 30

# Email constants
EMAIL_DELAY_MS = 50
EMAIL_SUCCESS_RATE = 0.98

# Payment constants  
PAYMENT_DELAY_MS = 150
PAYMENT_SUCCESS_RATE = 0.92
SUPPORTED_CURRENCIES = ["usd", "eur", "gbp"]

# Telegram constants
TELEGRAM_API_DELAY_MS = 120
TELEGRAM_SUCCESS_RATE = 0.94

# Auth constants
AUTH_DELAY_MS = 80
AUTH_SUCCESS_RATE = 0.99

# AI constants
AI_RESPONSE_DELAY_MS = 200
AI_SUCCESS_RATE = 0.90