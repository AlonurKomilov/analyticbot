from __future__ import annotations

from typing import Any, Protocol

from aiogram.types import CallbackQuery, Message, TelegramObject


# Define a Protocol for the base manager to avoid type issues
class BaseManagerProtocol(Protocol):
    """Protocol defining the base manager interface"""

    default_locale: str | None

    def __init__(self, default_locale: str | None = None) -> None: ...
    async def get_locale(self, *args: Any, **kwargs: Any) -> str: ...
    async def set_locale(self, *args: Any, **kwargs: Any) -> None: ...


# aiogram-i18n 1.4: public yo'l – managers.base
try:
    from aiogram_i18n.managers.base import (
        BaseManager as _BaseManager,  # type: ignore[import-untyped]
    )
except Exception:
    # Fallback stub (Pylance uchun), runtime-da ishlatilmaydi
    class _BaseManager:  # type: ignore[no-redef]
        """Fallback base manager for type checking when aiogram_i18n not available"""

        default_locale: str | None = None

        def __init__(self, default_locale: str | None = None) -> None:
            self.default_locale = default_locale

        async def get_locale(self, *args: Any, **kwargs: Any) -> str:
            return "en"

        async def set_locale(self, *args: Any, **kwargs: Any) -> None:
            return None


def _extract_user_id(event: TelegramObject) -> int | None:
    if isinstance(event, Message) and event.from_user is not None:
        return event.from_user.id
    if isinstance(event, CallbackQuery):
        user = getattr(event, "from_user", None)
        if user is not None:
            return user.id
    msg = getattr(event, "message", None)
    if isinstance(msg, Message) and msg.from_user is not None:
        return msg.from_user.id
    return None


class LanguageManager(_BaseManager):
    """
    DB'dan locale o'qiydi/yozadi.
    aiogram-i18n (>=1.4) chaqiruvlari:
      - get_locale(event=..., **data)
      - set_locale(event=..., locale=..., **data)
    """

    def __init__(self, user_repo: Any, config: Any) -> None:
        # public API: default_locale parametri
        try:
            super().__init__(default_locale=getattr(config, "DEFAULT_LOCALE", "en"))  # type: ignore[misc]
        except Exception:
            # stub holatida:
            self.default_locale = getattr(config, "DEFAULT_LOCALE", "en")
        self.user_repo = user_repo

    async def get_locale(self, event: TelegramObject, **_: Any) -> str:  # type: ignore[override]
        user_id = _extract_user_id(event)
        if user_id:
            for method in (
                "get_locale",
                "get_user_locale",
                "get_language",
                "get_user_language",
            ):
                if hasattr(self.user_repo, method):
                    try:
                        loc = await getattr(self.user_repo, method)(user_id)
                        if loc:
                            return str(loc)
                    except Exception:
                        pass
            if hasattr(self.user_repo, "get_user"):
                try:
                    user = await self.user_repo.get_user(user_id)
                    loc = getattr(user, "locale", None)
                    if loc:
                        return str(loc)
                except Exception:
                    pass
        return getattr(self, "default_locale", None) or "en"

    async def set_locale(self, event: TelegramObject, locale: str, **_: Any) -> None:  # type: ignore[override]
        user_id = _extract_user_id(event)
        if not user_id:
            return
        for method in (
            "set_locale",
            "set_user_locale",
            "save_locale",
            "update_locale",
            "set_language",
            "update_language",
        ):
            if hasattr(self.user_repo, method):
                try:
                    await getattr(self.user_repo, method)(user_id, locale)
                except Exception:
                    pass
                return
