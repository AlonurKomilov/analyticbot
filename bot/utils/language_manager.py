from __future__ import annotations

from typing import Any, Optional
from inspect import signature

from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram_i18n.managers import BaseManager


def _extract_user_id(event: TelegramObject) -> Optional[int]:
    """Message/CallbackQuery va umumiy TelegramObject dan user_id ni xavfsiz ajratib olish."""
    if isinstance(event, Message) and event.from_user:
        return event.from_user.id
    if isinstance(event, CallbackQuery) and event.from_user:
        return event.from_user.id
    # Generic fallback (agar boshqa turdagi obyekt bo‘lsa)
    from_user = getattr(event, "from_user", None)
    return getattr(from_user, "id", None)


class LanguageManager(BaseManager):
    def __init__(self, user_repo: Any, config: Any):
        # aiogram-i18n versiyasiga mos holda init param nomi (default vs default_locale)
        sig = signature(BaseManager.__init__)
        kwargs = (
            {"default_locale": config.DEFAULT_LOCALE}
            if "default_locale" in sig.parameters
            else {"default": config.DEFAULT_LOCALE}
        )
        super().__init__(**kwargs)

        self.user_repo = user_repo
        self.config = config

    async def get_locale(self, event: TelegramObject, data: dict) -> str:  # type: ignore[override]
        """Foydalanuvchi tilini repodan olish, bo‘lmasa defaultga tushish."""
        user_id = _extract_user_id(event)
        if user_id:
            # Repozitoriydagi odatiy metod nomlaridan foydalanib ko‘ramiz
            for method in ("get_locale", "get_user_locale", "get_language", "get_user_language"):
                if hasattr(self.user_repo, method):
                    try:
                        value = await getattr(self.user_repo, method)(user_id)
                        if value:
                            return str(value)
                    except Exception:
                        # Repozitoriy ichidagi xatolar botni to‘xtatmasin
                        pass

        # Managerning ichki defaultiga qaytamiz (default_locale yoki default)
        return getattr(self, "default_locale", getattr(self, "default", self.config.DEFAULT_LOCALE))

    async def set_locale(self, locale: str, event: TelegramObject, data: dict) -> None:  # type: ignore[override]
        """
        BaseManager talab qiladigan abstrakt metod.
        Agar repozitoriyda mos saqlash metodi bo‘lsa — chaqiramiz, bo‘lmasa no-op.
        """
        user_id = _extract_user_id(event)
        if not user_id:
            return

        for method in ("set_locale", "set_user_locale", "save_locale", "update_locale", "set_language", "update_language"):
            if hasattr(self.user_repo, method):
                try:
                    await getattr(self.user_repo, method)(user_id, locale)
                except Exception:
                    pass
                return  # topildi va urindi — chiqamiz
        # Mos metod yo‘q bo‘lsa jim turamiz (no-op)
        return