import os
from unittest.mock import patch

from apps.bot.config import Settings


def test_settings_load_from_env():
    """
    Tests that the Settings class correctly loads DATABASE_URL from env vars.
    """
    env_vars = {
        "BOT_TOKEN": "test_token",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "POSTGRES_DB": "test_db",
        "POSTGRES_PORT": "5432",
        "DATABASE_URL": "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "TWA_HOST_URL": "http://localhost:5173",
        "STORAGE_CHANNEL_ID": "-12345",
    }
    with patch.dict(os.environ, env_vars):
        settings = Settings()
        assert str(settings.DATABASE_URL) == env_vars["DATABASE_URL"]
