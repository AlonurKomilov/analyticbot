"""
⚡ Performance Optimization Configuration

Advanced performance tuning settings for production deployment
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field

class PerformanceConfig(BaseSettings):
    """
    🚀 Performance Configuration
    
    Production-optimized settings for maximum performance
    """
    
    # Connection Pool Settings
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=30, description="Maximum overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool connection timeout")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Connection recycle time")
    
    # HTTP Client Settings
    HTTP_CONNECTOR_LIMIT: int = Field(default=100, description="HTTP connector limit")
    HTTP_CONNECTOR_LIMIT_PER_HOST: int = Field(default=30, description="HTTP limit per host")
    HTTP_TIMEOUT_CONNECT: int = Field(default=10, description="HTTP connect timeout")
    HTTP_TIMEOUT_READ: int = Field(default=30, description="HTTP read timeout")
    HTTP_DNS_CACHE_TTL: int = Field(default=300, description="DNS cache TTL")
    
    # Cache Settings
    REDIS_POOL_SIZE: int = Field(default=50, description="Redis connection pool size")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, description="Redis retry on timeout")
    CACHE_DEFAULT_TTL: int = Field(default=3600, description="Default cache TTL")
    CACHE_MAX_CONNECTIONS: int = Field(default=100, description="Maximum cache connections")
    
    # Async Settings
    ASYNCIO_TASK_LIMIT: int = Field(default=1000, description="Maximum concurrent asyncio tasks")
    ASYNCIO_SEMAPHORE_LIMIT: int = Field(default=50, description="Asyncio semaphore limit")
    WORKER_CONCURRENCY: int = Field(default=10, description="Worker concurrency level")
    
    # Memory Management
    MEMORY_THRESHOLD_WARNING: float = Field(default=0.8, description="Memory warning threshold")
    MEMORY_THRESHOLD_CRITICAL: float = Field(default=0.95, description="Memory critical threshold")
    GC_THRESHOLD_0: int = Field(default=700, description="Garbage collection threshold 0")
    GC_THRESHOLD_1: int = Field(default=10, description="Garbage collection threshold 1")
    GC_THRESHOLD_2: int = Field(default=10, description="Garbage collection threshold 2")
    
    # ML/AI Performance Settings
    ML_BATCH_SIZE: int = Field(default=32, description="ML model batch size")
    ML_WORKER_THREADS: int = Field(default=4, description="ML processing threads")
    ML_MEMORY_LIMIT_MB: int = Field(default=1024, description="ML memory limit in MB")
    ML_CACHE_SIZE: int = Field(default=1000, description="ML model cache size")
    
    # API Performance
    API_RATE_LIMIT_PER_MINUTE: int = Field(default=1000, description="API rate limit per minute")
    API_BURST_LIMIT: int = Field(default=50, description="API burst limit")
    API_RESPONSE_TIMEOUT: int = Field(default=30, description="API response timeout")
    API_KEEP_ALIVE_TIMEOUT: int = Field(default=65, description="Keep alive timeout")
    
    # Monitoring Settings
    METRICS_COLLECTION_INTERVAL: int = Field(default=60, description="Metrics collection interval")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval")
    LOG_BUFFER_SIZE: int = Field(default=1000, description="Log buffer size")
    PERFORMANCE_SAMPLING_RATE: float = Field(default=0.1, description="Performance sampling rate")
    
    # Optimization Flags
    ENABLE_ASYNC_OPTIMIZATION: bool = Field(default=True, description="Enable async optimizations")
    ENABLE_CACHE_COMPRESSION: bool = Field(default=True, description="Enable cache compression")
    ENABLE_CONNECTION_POOLING: bool = Field(default=True, description="Enable connection pooling")
    ENABLE_QUERY_OPTIMIZATION: bool = Field(default=True, description="Enable query optimization")
    ENABLE_MEMORY_OPTIMIZATION: bool = Field(default=True, description="Enable memory optimization")
    
    # Security vs Performance Balance
    SECURITY_PERFORMANCE_MODE: str = Field(
        default="balanced", 
        description="Security vs performance mode: strict, balanced, performance"
    )
    
    # Environment Specific
    ENVIRONMENT: str = Field(default="production", description="Environment type")
    DEBUG_MODE: bool = Field(default=False, description="Enable debug mode")
    PROFILING_ENABLED: bool = Field(default=False, description="Enable performance profiling")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Environment-specific configurations
PERFORMANCE_PROFILES: Dict[str, Dict[str, Any]] = {
    "development": {
        "DB_POOL_SIZE": 5,
        "HTTP_CONNECTOR_LIMIT": 20,
        "CACHE_DEFAULT_TTL": 300,
        "DEBUG_MODE": True,
        "PROFILING_ENABLED": True,
    },
    "testing": {
        "DB_POOL_SIZE": 3,
        "HTTP_CONNECTOR_LIMIT": 10,
        "CACHE_DEFAULT_TTL": 60,
        "MEMORY_THRESHOLD_WARNING": 0.9,
        "ML_BATCH_SIZE": 8,
    },
    "production": {
        "DB_POOL_SIZE": 50,
        "HTTP_CONNECTOR_LIMIT": 200,
        "CACHE_DEFAULT_TTL": 3600,
        "ML_BATCH_SIZE": 64,
        "API_RATE_LIMIT_PER_MINUTE": 5000,
        "ENABLE_CACHE_COMPRESSION": True,
        "ENABLE_QUERY_OPTIMIZATION": True,
    },
    "high_load": {
        "DB_POOL_SIZE": 100,
        "HTTP_CONNECTOR_LIMIT": 500,
        "REDIS_POOL_SIZE": 200,
        "WORKER_CONCURRENCY": 20,
        "ML_WORKER_THREADS": 8,
        "API_RATE_LIMIT_PER_MINUTE": 10000,
    }
}

def get_performance_config(environment: Optional[str] = None) -> PerformanceConfig:
    """
    Get performance configuration for specific environment
    
    Args:
        environment: Environment name (development, testing, production, high_load)
        
    Returns:
        Configured PerformanceConfig instance
    """
    config = PerformanceConfig()
    
    if environment and environment in PERFORMANCE_PROFILES:
        profile = PERFORMANCE_PROFILES[environment]
        for key, value in profile.items():
            setattr(config, key, value)
    
    return config

# Global performance configuration
perf_config = get_performance_config(os.getenv("ENVIRONMENT", "production"))
