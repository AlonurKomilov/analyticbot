import hashlib
import hmac
from time import time
from urllib.parse import unquote

from fastapi import HTTPException

from apps.bot.config import settings


def validate_init_data(init_data: str, bot_token: str) -> dict:
    """
    Validates the initData string from a Telegram Web App.

    Args:
        init_data: The initData string from the TWA.
        bot_token: Your bot's token.

    Returns:
        A dictionary with the user data if validation is successful.

    Raises:
        HTTPException: If validation fails.
    """
    try:
        data_params = sorted(
            [
                x.split("=", 1)
                for x in init_data.split("&")
                if x.startswith("user=") or x.startswith("auth_date=")
            ],
            key=lambda x: x[0],
        )
        data_check_string = "\n".join([f"{k}={v}" for k, v in data_params])
        received_hash = None
        for param in init_data.split("&"):
            if param.startswith("hash="):
                received_hash = param.split("=", 1)[1]
                break
        if received_hash is None:
            raise ValueError("Hash not found in initData")
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if calculated_hash != received_hash:
            raise ValueError("Hash mismatch")
        try:
            auth_date_str = next((v for k, v in data_params if k == "auth_date"))
            auth_date = int(auth_date_str)
            max_age = getattr(settings, "WEBAPP_AUTH_MAX_AGE", 3600)
            if time() - auth_date > max_age:
                raise ValueError("Auth date expired")
        except StopIteration:
            raise ValueError("auth_date missing")
        user_data_str = [x for x in init_data.split("&") if x.startswith("user=")][0]
        user_data_json = unquote(user_data_str.split("=", 1)[1])
        import json

        return json.loads(user_data_json)
    except (ValueError, IndexError, KeyError) as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: Invalid initData. {e}")
