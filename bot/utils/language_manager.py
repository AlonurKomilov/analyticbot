from typing import Any, cast

from aiogram.types import TelegramObject
from aiogram_i18n.managers import BaseManager   # sizda qanday import bo‘lsa, o‘sha qoladi

class LanguageManager(BaseManager):
    def __init__(self, user_repo, config):
        # YANGI: default -> default_locale
        try:
            super().__init__(default_locale=config.DEFAULT_LOCALE)
        except TypeError:
            # Agar eski versiya bo‘lsa, orqaga moslik
            super().__init__(default=config.DEFAULT_LOCALE)

        self.user_repo = user_repo
        self.config = config

    async def get_locale(self, event: TelegramObject, data: dict) -> str:
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if user_id:
            loc = await self.user_repo.get_locale(user_id)
            if loc:
                return loc
        # managerning ichki defaultini qaytaramiz
        return getattr(self, "default_locale", getattr(self, "default", self.config.DEFAULT_LOCALE))