"""
🚀 OPTIMIZED DEPENDENCY CONTAINER
High-performance dependency injection with caching and monitoring
"""
import asyncio
import logging
from typing import Dict, Any, Optional

from dependency_injector import containers, providers
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

# Import existing services
from bot.database.db import db_manager
from bot.database.performance import performance_manager
from bot.database.repositories.user_repository import UserRepository
from bot.database.repositories.channel_repository import ChannelRepository
from bot.database.repositories.analytics_repository import AnalyticsRepository
from bot.database.repositories.scheduler_repository import SchedulerRepository
from bot.database.repositories.plan_repository import PlanRepository

# Import optimized services
from bot.services.optimized_analytics_service import OptimizedAnalyticsService
from bot.services.auth_service import AuthService
from bot.services.guard_service import GuardService
from bot.services.subscription_service import SubscriptionService
from bot.services.scheduler_service import SchedulerService
from bot.services.prometheus_service import prometheus_service

# Import ML services (Phase 2.5)
from bot.services.ml.prediction_service import PredictionService
from bot.services.ml.content_optimizer import ContentOptimizer
from bot.services.ml.churn_predictor import ChurnPredictor
from bot.services.ml.engagement_analyzer import EngagementAnalyzer

from bot.config import settings

logger = logging.getLogger(__name__)


class OptimizedContainer(containers.DeclarativeContainer):
    """🔥 High-performance dependency injection container"""
    
    # Configuration
    config = providers.Configuration()
    
    # Performance components (initialized early)
    performance_manager = providers.Singleton(
        lambda: performance_manager
    )
    
    # Database components
    database_manager = providers.Singleton(
        lambda: db_manager
    )
    
    database_pool = providers.Resource(
        providers.Coroutine(
            db_manager.create_pool
        )
    )
    
    # Bot components with enhanced session
    bot_session = providers.Singleton(
        AiohttpSession,
        connector_limit=100,
        connector_limit_per_host=30,
        connector_ttl_dns_cache=300,
        connector_use_dns_cache=True,
        timeout_read=30,
        timeout_connect=10
    )
    
    bot = providers.Singleton(
        Bot,
        token=settings.BOT_TOKEN.get_secret_value(),
        session=bot_session
    )
    
    dispatcher = providers.Singleton(Dispatcher)
    
    # Repository layer with connection pooling
    user_repository = providers.Singleton(
        UserRepository,
        db_pool=database_pool
    )
    
    channel_repository = providers.Singleton(
        ChannelRepository,
        db_pool=database_pool
    )
    
    analytics_repository = providers.Singleton(
        AnalyticsRepository,
        db_pool=database_pool
    )
    
    scheduler_repository = providers.Singleton(
        SchedulerRepository,
        db_pool=database_pool
    )
    
    plan_repository = providers.Singleton(
        PlanRepository,
        db_pool=database_pool
    )
    
    # Optimized service layer
    optimized_analytics_service = providers.Singleton(
        OptimizedAnalyticsService,
        bot=bot,
        analytics_repository=analytics_repository
    )
    
    # ML/AI Service Layer (Phase 2.5)
    prediction_service = providers.Singleton(
        PredictionService,
        cache_service=providers.Object("performance_manager.cache"),
        db_service=database_manager
    )
    
    content_optimizer = providers.Singleton(
        ContentOptimizer,
        cache_service=providers.Object("performance_manager.cache"),
        analytics_service=optimized_analytics_service
    )
    
    churn_predictor = providers.Singleton(
        ChurnPredictor,
        db_service=database_manager,
        analytics_service=optimized_analytics_service,
        cache_service=providers.Object("performance_manager.cache")
    )
    
    engagement_analyzer = providers.Singleton(
        EngagementAnalyzer,
        prediction_service=prediction_service,
        content_optimizer=content_optimizer,
        churn_predictor=churn_predictor,
        db_service=database_manager,
        cache_service=providers.Object("performance_manager.cache")
    )
    
    auth_service = providers.Singleton(
        AuthService,
        user_repository=user_repository
    )
    
    guard_service = providers.Singleton(
        GuardService,
        user_repository=user_repository,
        channel_repository=channel_repository
    )
    
    subscription_service = providers.Singleton(
        SubscriptionService,
        user_repository=user_repository,
        plan_repository=plan_repository
    )
    
    scheduler_service = providers.Singleton(
        SchedulerService,
        scheduler_repository=scheduler_repository,
        bot=bot
    )
    
    # Monitoring services
    prometheus_service = providers.Singleton(
        lambda: prometheus_service
    )


class PerformanceAwareContainer:
    """🔍 Container with performance monitoring and health checks"""
    
    def __init__(self):
        self.container = OptimizedContainer()
        self._initialized = False
        self._health_status: Dict[str, Any] = {}
        self._performance_metrics: Dict[str, float] = {}
    
    async def initialize(self) -> None:
        """🚀 Initialize all services with performance monitoring"""
        if self._initialized:
            logger.info("📦 Container already initialized")
            return
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info("🔧 Initializing optimized container...")
            
            # Initialize performance components first
            await self._initialize_performance_layer()
            
            # Initialize database layer
            await self._initialize_database_layer()
            
            # Initialize service layer
            await self._initialize_service_layer()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Run health checks
            await self._initial_health_check()
            
            self._initialized = True
            
            init_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"✅ Optimized container initialized in {init_time:.3f}s")
            
        except Exception as e:
            logger.error(f"❌ Container initialization failed: {e}")
            raise
    
    async def _initialize_performance_layer(self):
        """Initialize performance optimization layer"""
        try:
            # Initialize performance manager
            await performance_manager.initialize()
            logger.info("🚀 Performance layer initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Performance layer initialization failed: {e}")
            # Continue without performance optimizations
    
    async def _initialize_database_layer(self):
        """Initialize database connections with optimization"""
        try:
            # Initialize database pool
            await self.container.database_pool.provided()
            
            # Verify connection health
            if not await db_manager.health_check():
                raise Exception("Database health check failed")
            
            logger.info("🗄️ Database layer initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def _initialize_service_layer(self):
        """Initialize service layer components"""
        try:
            # Pre-warm service instances
            services = [
                'user_repository',
                'channel_repository', 
                'analytics_repository',
                'scheduler_repository',
                'plan_repository'
            ]
            
            for service_name in services:
                service = getattr(self.container, service_name)()
                logger.debug(f"📝 Initialized {service_name}")
            
            # Initialize ML services (Phase 2.5)
            await self._initialize_ml_services()
            
            logger.info("🔧 Service layer initialized")
            
        except Exception as e:
            logger.error(f"❌ Service layer initialization failed: {e}")
            raise
    
    async def _initialize_ml_services(self):
        """🤖 Initialize ML/AI services (Phase 2.5)"""
        try:
            logger.info("🤖 Initializing ML/AI services...")
            
            # Initialize prediction service
            prediction_service = self.container.prediction_service()
            await prediction_service.initialize_models()
            logger.debug("✅ Prediction service initialized")
            
            # Initialize churn predictor
            churn_predictor = self.container.churn_predictor()
            await churn_predictor.initialize_model()
            logger.debug("✅ Churn predictor initialized")
            
            # Initialize content optimizer (no async init needed)
            content_optimizer = self.container.content_optimizer()
            logger.debug("✅ Content optimizer initialized")
            
            # Initialize engagement analyzer (orchestrator)
            engagement_analyzer = self.container.engagement_analyzer()
            logger.debug("✅ Engagement analyzer initialized")
            
            logger.info("🚀 ML/AI services initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ ML services initialization failed: {e}")
            # Continue without ML services for backward compatibility
            
        except Exception as e:
            logger.error(f"❌ Service layer initialization failed: {e}")
            raise
    
    async def _initialize_monitoring(self):
        """Initialize monitoring and metrics collection"""
        try:
            # Initialize Prometheus if available
            prometheus_service.start_http_server()
            logger.info("📊 Monitoring initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Monitoring initialization failed: {e}")
    
    async def _initial_health_check(self):
        """Run comprehensive health check on all components"""
        health_checks = {
            'database': db_manager.health_check(),
            'cache': self._check_cache_health(),
            'bot': self._check_bot_health(),
            'ml_services': self._check_ml_services_health()
        }
        
        results = await asyncio.gather(
            *health_checks.values(),
            return_exceptions=True
        )
        
        self._health_status = dict(zip(health_checks.keys(), results))
        
        # Log health status
        for component, status in self._health_status.items():
            if isinstance(status, Exception):
                logger.warning(f"⚠️ {component} health check failed: {status}")
            elif status:
                logger.info(f"✅ {component} healthy")
            else:
                logger.warning(f"⚠️ {component} unhealthy")
    
    async def _check_cache_health(self) -> bool:
        """Check cache connectivity"""
        try:
            return performance_manager.cache._is_connected
        except:
            return False
    
    async def _check_bot_health(self) -> bool:
        """Check bot connectivity"""
        try:
            bot = self.container.bot()
            me = await bot.get_me()
            return bool(me)
        except:
            return False
    
    async def _check_ml_services_health(self) -> Dict[str, Any]:
        """🤖 Check ML services health"""
        try:
            ml_health = {}
            
            # Check prediction service
            try:
                prediction_service = self.container.prediction_service()
                ml_health['prediction_service'] = await prediction_service.health_check()
            except Exception as e:
                ml_health['prediction_service'] = {'status': 'error', 'error': str(e)}
            
            # Check content optimizer
            try:
                content_optimizer = self.container.content_optimizer()
                ml_health['content_optimizer'] = await content_optimizer.health_check()
            except Exception as e:
                ml_health['content_optimizer'] = {'status': 'error', 'error': str(e)}
            
            # Check churn predictor
            try:
                churn_predictor = self.container.churn_predictor()
                ml_health['churn_predictor'] = await churn_predictor.health_check()
            except Exception as e:
                ml_health['churn_predictor'] = {'status': 'error', 'error': str(e)}
            
            # Check engagement analyzer
            try:
                engagement_analyzer = self.container.engagement_analyzer()
                ml_health['engagement_analyzer'] = await engagement_analyzer.health_check()
            except Exception as e:
                ml_health['engagement_analyzer'] = {'status': 'error', 'error': str(e)}
            
            return ml_health
            
        except Exception as e:
            return {'status': 'error', 'error': f'ML services health check failed: {e}'}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all components"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        # Refresh health checks
        await self._initial_health_check()
        
        return {
            "initialized": self._initialized,
            "components": self._health_status,
            "overall_healthy": all(
                isinstance(status, bool) and status 
                for status in self._health_status.values()
            )
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from all components"""
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            metrics = {}
            
            # Database metrics
            if db_manager.pool:
                metrics["database"] = await db_manager.get_performance_stats()
            
            # Performance manager metrics
            if performance_manager:
                metrics["performance"] = await performance_manager.get_performance_stats()
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self):
        """🏁 Graceful shutdown of all components"""
        if not self._initialized:
            return
        
        logger.info("🏁 Shutting down container...")
        
        shutdown_tasks = []
        
        # Close database connections
        if db_manager.pool:
            shutdown_tasks.append(db_manager.close_pool())
        
        # Close performance manager
        shutdown_tasks.append(performance_manager.close())
        
        # Close bot session
        try:
            bot = self.container.bot()
            if bot.session:
                shutdown_tasks.append(bot.session.close())
        except:
            pass
        
        # Execute all shutdowns concurrently
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self._initialized = False
        logger.info("✅ Container shutdown completed")
    
    def __getattr__(self, name):
        """Delegate attribute access to the container"""
        if not self._initialized:
            logger.warning(f"⚠️ Accessing {name} before container initialization")
        
        return getattr(self.container, name)


# Global optimized container instance
container = PerformanceAwareContainer()
