from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.exceptions import KeyNotFoundError


class SafeFluentRuntimeCore(FluentRuntimeCore):
    def get(self, key: str, locale: str | None = None, /, **kwargs) -> str:
        try:
            return super().get(key, locale, **kwargs)
        except KeyNotFoundError:
            # Kalit topilmasa bot yiqilmasin — kalitning o'zini qaytaramiz
            return key
