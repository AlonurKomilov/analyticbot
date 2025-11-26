"""
User-Friendly Error Messages for Bot Management

Converts technical error messages into user-friendly, actionable messages.
"""



class BotErrorMessages:
    """
    User-friendly error messages for common bot management issues

    Provides clear, actionable error messages instead of technical details.
    """

    # === Bot Token Errors ===
    INVALID_TOKEN = (
        "Invalid bot token. Please check that you copied the full token from @BotFather. "
        "It should look like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    )

    TOKEN_REVOKED = (
        "Your bot token has been revoked. Please create a new bot token from @BotFather "
        "and update your bot settings."
    )

    TOKEN_ALREADY_EXISTS = (
        "You already have a bot configured. Please remove your existing bot before creating a new one."
    )

    # === Verification Errors ===
    BOT_NOT_STARTED = (
        "Please start a conversation with your bot first. Open Telegram, search for your bot, "
        "and click the 'Start' button."
    )

    INSUFFICIENT_PERMISSIONS = (
        "Your bot doesn't have the required permissions. Make sure your bot is an admin "
        "in the channel/group with proper permissions."
    )

    CHAT_NOT_FOUND = (
        "Could not find the specified chat. Please check that the chat ID is correct "
        "and that your bot has access to it."
    )

    # === Connection Errors ===
    NETWORK_ERROR = (
        "Network connection error. Please check your internet connection and try again. "
        "If the problem persists, Telegram servers might be temporarily unavailable."
    )

    RATE_LIMIT_EXCEEDED = (
        "You're sending requests too quickly. Please wait a moment and try again. "
        "Our system automatically manages rate limits to prevent issues."
    )

    TELEGRAM_API_ERROR = (
        "Telegram API is temporarily unavailable. This is usually temporary - "
        "please try again in a few minutes."
    )

    # === Database Errors ===
    DATABASE_ERROR = (
        "A database error occurred. Our team has been notified. "
        "Please try again in a moment."
    )

    BOT_NOT_FOUND = (
        "You don't have a bot configured yet. Please create a bot first using the 'Create Bot' option."
    )

    # === MTProto Errors ===
    MTPROTO_NOT_CONFIGURED = (
        "MTProto (advanced features) is not configured for your bot. "
        "To use channel analytics, please provide your Telegram API credentials."
    )

    INVALID_API_CREDENTIALS = (
        "Invalid Telegram API credentials. Please get your API ID and API Hash from "
        "https://my.telegram.org/apps and try again."
    )

    SESSION_EXPIRED = (
        "Your Telegram session has expired. Please re-authenticate your bot "
        "to continue using advanced features."
    )

    # === Rate Limit Errors ===
    INVALID_RATE_LIMIT = (
        "Invalid rate limit settings. Requests per second must be between 1-100, "
        "and concurrent requests must be between 1-50."
    )

    # === Generic Errors ===
    INTERNAL_ERROR = (
        "An unexpected error occurred. Our team has been notified. "
        "Please try again in a moment."
    )

    UNAUTHORIZED = (
        "You don't have permission to perform this action. "
        "Please make sure you're logged in."
    )


def get_user_friendly_error(error: Exception) -> tuple[int, str]:
    """
    Convert an exception to user-friendly error message

    Args:
        error: The exception that occurred

    Returns:
        Tuple of (status_code, user_friendly_message)

    Example:
        status_code, message = get_user_friendly_error(error)
        raise HTTPException(status_code=status_code, detail=message)
    """
    error_str = str(error).lower()

    # Bot Token Errors (400)
    if any(x in error_str for x in ["invalid token", "token is invalid"]) and "revoked" not in error_str:
        return 400, BotErrorMessages.INVALID_TOKEN

    if "token revoked" in error_str or "token was revoked" in error_str:
        return 401, BotErrorMessages.TOKEN_REVOKED

    if "already exists" in error_str or "duplicate" in error_str:
        return 409, BotErrorMessages.TOKEN_ALREADY_EXISTS

    # Verification Errors (400)
    if "bot was blocked" in error_str or "bot can't initiate" in error_str:
        return 400, BotErrorMessages.BOT_NOT_STARTED

    if "not enough rights" in error_str or "forbidden" in error_str:
        return 403, BotErrorMessages.INSUFFICIENT_PERMISSIONS

    if "chat not found" in error_str or "channel not found" in error_str:
        return 404, BotErrorMessages.CHAT_NOT_FOUND

    # Rate Limit Errors - check before connection errors
    if "429" in error_str or "too many requests" in error_str:
        return 429, BotErrorMessages.RATE_LIMIT_EXCEEDED

    # Rate Limit Validation (different from API rate limits)
    if "rate limit" in error_str and any(x in error_str for x in ["invalid", "must be", "between"]):
        return 400, BotErrorMessages.INVALID_RATE_LIMIT

    # Connection Errors (503) - check after rate limits
    if any(x in error_str for x in ["network", "timeout", "timed out"]) and "connection" in error_str:
        return 503, BotErrorMessages.NETWORK_ERROR

    if "telegram api" in error_str or "bad gateway" in error_str:
        return 503, BotErrorMessages.TELEGRAM_API_ERROR

    # Database Errors (500) - check for database keywords more specifically
    if any(x in error_str for x in ["database error", "db error", "connection pool", "sql error"]):
        return 500, BotErrorMessages.DATABASE_ERROR

    # Not Found - check before generic "not found"
    if "no bot found" in error_str or ("bot" in error_str and "not found" in error_str):
        return 404, BotErrorMessages.BOT_NOT_FOUND

    # MTProto Errors
    if "mtproto" in error_str or "pyrogram" in error_str:
        if "not configured" in error_str or "not initialized" in error_str:
            return 400, BotErrorMessages.MTPROTO_NOT_CONFIGURED
        if "invalid" in error_str:
            return 400, BotErrorMessages.INVALID_API_CREDENTIALS
        if "session" in error_str and "expired" in error_str:
            return 401, BotErrorMessages.SESSION_EXPIRED

    # Authorization - check specifically for "unauthorized"
    if error_str.startswith("unauthorized") or "not authorized" in error_str or error_str == "unauthorized":
        return 401, BotErrorMessages.UNAUTHORIZED

    # Default to internal error
    return 500, BotErrorMessages.INTERNAL_ERROR


def get_validation_error_message(field: str, constraint: str) -> str:
    """
    Get user-friendly message for validation errors

    Args:
        field: The field that failed validation
        constraint: The constraint that was violated

    Returns:
        User-friendly error message
    """
    messages = {
        "bot_token": {
            "required": "Bot token is required. Get it from @BotFather on Telegram.",
            "format": "Invalid bot token format. It should look like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            "min_length": "Bot token is too short. Please check that you copied the full token.",
        },
        "api_id": {
            "required": "Telegram API ID is required for MTProto features.",
            "type": "API ID must be a number. Get it from https://my.telegram.org/apps",
        },
        "api_hash": {
            "required": "Telegram API Hash is required for MTProto features.",
            "format": "Invalid API Hash format. Get it from https://my.telegram.org/apps",
        },
        "max_requests_per_second": {
            "range": "Requests per second must be between 1 and 100.",
            "type": "Requests per second must be a number.",
        },
        "max_concurrent_requests": {
            "range": "Concurrent requests must be between 1 and 50.",
            "type": "Concurrent requests must be a number.",
        },
        "test_chat_id": {
            "required": "Chat ID is required when sending a test message.",
            "format": "Invalid chat ID format. It should be a number or @username.",
        },
    }

    field_messages = messages.get(field, {})
    return field_messages.get(constraint, f"Invalid {field}: {constraint}")
