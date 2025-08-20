"""Central I18N hub compatible with current aiogram version.

aiogram 3.10.0 in this environment does not expose `aiogram.i18n.I18n`.
Fallback: minimal wrapper using SafeFluentRuntimeCore already present.

If you upgrade aiogram and gain native I18n support, you can replace this
file with a thin adapter around the official class.
"""

from __future__ import annotations

from pathlib import Path

from bot.utils.safe_i18n_core import SafeFluentRuntimeCore

try:  # settings may fail if env variables are absent during tooling
    from bot.config import settings  # type: ignore

    _default_locale = settings.DEFAULT_LOCALE
except Exception:  # pragma: no cover
    _default_locale = "en"

_LOCALES_PATH = Path("bot/locales")


class _MiniI18n:
    def __init__(self, path: str, default_locale: str):
        self.path = path
        self.default_locale = default_locale
        self.core = SafeFluentRuntimeCore(path=f"{path}/{{locale}}")
        self._loaded: bool = False
        self.locales: dict[str, dict[str, str]] = {}

    def _ensure(self):
        if self._loaded:
            return
        try:
            self.core.locales.update(self.core.find_locales())
            self._loaded = True
        except Exception:
            pass

    def gettext(self, key: str, locale: str | None = None, **kwargs):
        self._ensure()
        loc = locale or self.default_locale
        try:
            return self.core.get(key, loc, **kwargs)
        except Exception:
            return key

    def get(self, key: str, *a, **kw):  # alias
        return self.gettext(key, *a, **kw)


I18N_HUB = _MiniI18n(path=str(_LOCALES_PATH), default_locale=_default_locale)

__all__ = ["I18N_HUB"]
