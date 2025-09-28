"""
Bot Container - Compatibility Wrapper for Clean Architecture
Delegates all operations to apps/bot/di.py (clean dependency-injector container)

This eliminates the god container pattern while maintaining compatibility.
"""
from __future__ import annotations

import logging
from typing import Any, TypeVar, cast

from apps.bot.di import configure_bot_container
from apps.bot.utils.punctuated import Singleton
from apps.bot.config import Settings

logger = logging.getLogger(__name__)

try:
    from aiogram.client.bot import Bot as _AioBot
except Exception:
    from aiogram import Bot as _AioBot
    
from aiogram import Bot as _ClientBot
from aiogram import Dispatcher as _AioDispatcher
from asyncpg.pool import Pool as AsyncPGPool
from sqlalchemy.ext.asyncio import async_sessionmaker

from infra.db.repositories.analytics_repository import AsyncpgAnalyticsRepository
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.schedule_repository import AsyncpgScheduleRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository


class Container:
    """
    Legacy compatibility wrapper that delegates to clean DI container.
    
    This eliminates the god container pattern by forwarding all requests
    to the properly structured apps/bot/di.py container.
    """
    
    def __init__(self):
        # Initialize clean DI container
        self._clean_container = configure_bot_container()
        self.config = Singleton(Settings)
        logger.debug("Initialized compatibility wrapper for clean DI container")
    
    # === Bot Client Access ===
    
    def bot(self):
        """Legacy bot access - delegates to clean container"""
        return self._clean_container.bot_client()
    
    def resolve(self, cls):
        """
        Legacy resolve method - maps to clean container services
        Maintains compatibility while using clean architecture
        """
        try:
            # Map legacy class requests to clean DI container methods
            class_name = cls.__name__ if hasattr(cls, '__name__') else str(cls)
            
            # Bot client mapping
            if class_name in ['Bot', '_AioBot', '_ClientBot']:
                return self._clean_container.bot_client()
            elif class_name == '_AioDispatcher':
                return self._clean_container.dispatcher()
                
            # Repository mapping  
            elif class_name == 'AsyncpgUserRepository':
                return self._clean_container.user_repo()
            elif class_name == 'AsyncpgChannelRepository':
                return self._clean_container.channel_repo()
            elif class_name == 'AsyncpgAnalyticsRepository':
                return self._clean_container.analytics_repo()
            elif class_name == 'AsyncpgScheduleRepository':
                return self._clean_container.schedule_repo()
            elif class_name == 'AsyncpgPlanRepository':
                return self._clean_container.plan_repo()
                
            # Service mapping
            elif class_name == 'GuardService':
                return self._clean_container.guard_service()
            elif class_name == 'SubscriptionService':
                return self._clean_container.subscription_service()
            elif class_name == 'SchedulerService':
                return self._clean_container.scheduler_service()
            elif class_name == 'AnalyticsService':
                return self._clean_container.analytics_service()
            elif class_name == 'AlertingService':
                return self._clean_container.alerting_service()
            elif class_name == 'ChannelManagementService':
                return self._clean_container.channel_management_service()
                
            # Fallback: try to create instance directly
            else:
                logger.debug(f"Fallback: creating instance of {class_name} directly")
                return cls()
                
        except Exception as e:
            logger.warning(f"Failed to resolve {class_name} via clean container: {e}")
            try:
                return cls()
            except Exception:
                logger.error(f"Failed to create fallback instance of {class_name}")
                return None
    
    def register(self, cls, factory=None, instance=None):
        """
        Legacy register method - no-op for compatibility
        All registration is handled by the clean DI container
        """
        logger.debug(f"Legacy register call for {cls.__name__ if hasattr(cls, '__name__') else cls} - delegated to clean container")
        pass
    
    # === Legacy Repository Methods ===
    
    def user_repository(self):
        """Legacy repository access"""
        return self._clean_container.user_repo()
    
    def channel_repository(self):
        """Legacy repository access"""
        return self._clean_container.channel_repo()
        
    def scheduler_repository(self):
        """Legacy repository access"""
        return self._clean_container.schedule_repo()
        
    def analytics_repository(self):
        """Legacy repository access"""
        return self._clean_container.analytics_repo()
        
    def plan_repository(self):
        """Legacy repository access"""
        return self._clean_container.plan_repo()
    
    # === Legacy Service Methods ===
    
    def guard_service(self):
        """Legacy service access"""
        return self._clean_container.guard_service()
        
    def subscription_service(self):
        """Legacy service access"""
        return self._clean_container.subscription_service()
        
    def scheduler_service(self):
        """Legacy service access"""
        return self._clean_container.scheduler_service()
        
    def analytics_service(self):
        """Legacy service access"""
        return self._clean_container.analytics_service()
        
    def alerting_service(self):
        """Legacy service access"""
        return self._clean_container.alerting_service()
    
    def channel_management_service(self):
        """Legacy service access"""
        return self._clean_container.channel_management_service()
        
    def channel_service(self):
        """Legacy alias for channel_management_service"""
        return self.channel_management_service()
    
    # === Legacy Database Access ===
    
    async def asyncpg_pool(self):
        """Legacy pool access"""
        try:
            return await self._clean_container.asyncpg_pool()
        except Exception as e:
            logger.warning(f"Failed to get asyncpg pool: {e}")
            return None
    
    def db_session(self):
        """Legacy db_session method - not supported in clean architecture"""
        logger.warning("db_session() method is deprecated in clean architecture")
        return None


# Legacy container instance
container = Container()

# Legacy type variable and function
_T = TypeVar("_T")

def _resolve(key: type[_T]) -> _T:
    """Legacy resolve function"""
    return cast(_T, container.resolve(key))

# Legacy compatibility aliases
OptimizedContainer = Container


class MLCompatibilityLayer:
    """ML service compatibility layer"""

    def __init__(self, container: Container):
        self._container = container

    @property
    def prediction_service(self):
        """ML service compatibility"""
        try:
            return self._container._clean_container.prediction_service()
        except Exception:
            return None

    @property
    def content_optimizer(self):
        """ML service compatibility"""
        try:
            return self._container._clean_container.content_optimizer()
        except Exception:
            return None

    @property
    def churn_predictor(self):
        """ML service compatibility"""
        try:
            return self._container._clean_container.churn_predictor()
        except Exception:
            return None

    @property
    def engagement_analyzer(self):
        """ML service compatibility"""
        try:
            return self._container._clean_container.engagement_analyzer()
        except Exception:
            return None


class OptimizedContainerCompat(Container):
    """Enhanced compatibility wrapper with ML services"""

    def __init__(self):
        super().__init__()
        self._ml_compat = MLCompatibilityLayer(self)

    def __getattr__(self, name):
        """Delegate ML service access"""
        if hasattr(self._ml_compat, name):
            return getattr(self._ml_compat, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# Update OptimizedContainer to enhanced version
OptimizedContainer = OptimizedContainerCompat
