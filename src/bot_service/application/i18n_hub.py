"""Central I18N hub compatible with current aiogram version.

aiogram 3.10.0 in this environment does not expose `aiogram.i18n.I18n`.
Fallback: minimal wrapper using SafeFluentRuntimeCore already present.

If you upgrade aiogram and gain native I18n support, you can replace this
file with a thin adapter around the official class.
"""

from __future__ import annotations

from pathlib import Path

from src.bot_service.utils.simple_i18n_core import SimpleI18nCore

try:
    from src.bot_service.config import settings

    _default_locale = settings.DEFAULT_LOCALE
except Exception:
    _default_locale = "en"

# Use absolute path for locales
_BASE_DIR = Path(__file__).parent
_LOCALES_PATH = _BASE_DIR


class _MiniI18n:
    def __init__(self, path: str, default_locale: str):
        self.path = path
        self.default_locale = default_locale
        # Use our simple I18N core
        self.core = SimpleI18nCore(path_template=f"{path}/{{locale}}")
        self._loaded: bool = False

    def _ensure(self):
        if self._loaded:
            return
        try:
            # Force reload of locales
            self.core.locales = self.core.find_locales()
            self._loaded = True
            print(f"I18N: Loaded locales: {list(self.core.locales.keys())}")
        except Exception as e:
            print(f"I18N: Failed to load locales: {e}")

    def gettext(self, key: str, locale: str | None = None, **kwargs):
        self._ensure()
        loc = locale or self.default_locale
        try:
            result = self.core.get(key, loc, **kwargs)
            if result != key:  # Only log if translation was found
                print(f"I18N: Found key '{key}' for locale '{loc}': {result[:50]}...")
            else:
                print(f"I18N: Key '{key}' not found for locale '{loc}'")
            return result
        except Exception as e:
            print(f"I18N: Error getting key '{key}' for locale '{loc}': {e}")
            return key

    def get(self, key: str, *a, **kw):
        return self.gettext(key, *a, **kw)


I18N_HUB = _MiniI18n(path=str(_LOCALES_PATH), default_locale=_default_locale)
__all__ = ["I18N_HUB"]
