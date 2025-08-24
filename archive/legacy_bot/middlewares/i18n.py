from aiogram_i18n import I18nMiddleware
from bot.locales.i18n_hub import I18N_HUB

# I18nMiddleware obyektini yaratish va eksport qilish
# Tilni boshqarish logikasi run_bot.py ichidagi LanguageManager'da amalga oshiriladi
i18n_middleware = I18nMiddleware(I18N_HUB, default_locale="en")
