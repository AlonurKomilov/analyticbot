from aiogram_i18n import I18nMiddleware

from src.bot_service.locales.i18n_hub import I18N_HUB

i18n_middleware = I18nMiddleware(I18N_HUB, default_locale="en")
