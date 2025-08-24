# Temporary compat shim: redirect old imports to apps.bot
"""
Compatibility shim for bot module.
Redirects imports from `bot.*` to `apps.bot.*`

This shim will be removed after migration is complete.
"""

import sys
from importlib import import_module

# Create module aliases for backward compatibility
_module_mapping = {
    "bot": "apps.bot",
    "bot.handlers": "apps.bot.handlers",
    "bot.services": "apps.bot.services",
    "bot.middlewares": "apps.bot.middlewares",
    "bot.models": "apps.bot.models",
    "bot.utils": "apps.bot.utils",
    "bot.database": "apps.bot.database",
    "bot.locales": "apps.bot.locales",
    "bot.tasks": "apps.bot.tasks",
    "bot.analytics": "apps.bot.analytics",
    "bot.container": "apps.bot.container",
    "bot.celery_app": "apps.bot.celery_app",
}

for old_module, new_module in _module_mapping.items():
    try:
        sys.modules[old_module] = import_module(new_module)
    except ImportError:
        # Module might not exist yet, that's okay
        pass
