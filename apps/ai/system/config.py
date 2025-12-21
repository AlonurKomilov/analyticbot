"""
AI System Configuration
=======================

Environment-based configuration for the System AI.
All settings are controlled via .env files (not user configurable).
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AIApprovalMode(str, Enum):
    """Approval mode for AI decisions"""
    
    AUTO = "auto"           # Execute all decisions automatically
    REVIEW = "review"       # Review recommended for risky actions
    APPROVAL = "approval"   # All actions require approval
    DISABLED = "disabled"   # AI disabled


@dataclass
class SystemAIConfig:
    """
    System AI Configuration (from environment variables)
    
    Configure via .env.development or .env.production:
    
    AI_SYSTEM_ENABLED=true
    AI_SYSTEM_AUTO_SCALE=true
    AI_SYSTEM_DRY_RUN=false
    AI_SYSTEM_APPROVAL_MODE=review
    AI_SYSTEM_MAX_WORKERS=10
    AI_SYSTEM_MEMORY_LIMIT_MB=4096
    AI_SYSTEM_CPU_THRESHOLD=80
    AI_SYSTEM_MONITORING_INTERVAL=60
    AI_SYSTEM_LLM_ENABLED=false
    AI_SYSTEM_LLM_MODEL=gpt-4
    """
    
    # Core settings
    enabled: bool = True
    dry_run: bool = False
    approval_mode: AIApprovalMode = AIApprovalMode.REVIEW
    
    # Auto-scaling settings
    auto_scale_enabled: bool = True
    max_workers: int = 10
    min_workers: int = 1
    
    # Resource thresholds
    cpu_threshold_high: float = 80.0
    cpu_threshold_low: float = 30.0
    memory_limit_mb: int = 4096
    memory_threshold_percent: float = 85.0
    
    # Monitoring
    monitoring_interval_seconds: int = 60
    health_check_interval_seconds: int = 30
    
    # Safety limits
    max_decisions_per_hour: int = 20
    max_actions_per_hour: int = 10
    max_restarts_per_hour: int = 5
    
    # LLM settings (Phase 3)
    llm_enabled: bool = False
    llm_model: str = "gpt-4"
    llm_api_key: str = ""
    
    # Logging
    log_level: str = "INFO"
    log_decisions: bool = True
    log_actions: bool = True
    
    @classmethod
    def from_env(cls) -> "SystemAIConfig":
        """Load configuration from environment variables"""
        
        def get_bool(key: str, default: bool) -> bool:
            return os.getenv(key, str(default)).lower() in ("true", "1", "yes")
        
        def get_int(key: str, default: int) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except ValueError:
                return default
        
        def get_float(key: str, default: float) -> float:
            try:
                return float(os.getenv(key, str(default)))
            except ValueError:
                return default
        
        approval_mode_str = os.getenv("AI_SYSTEM_APPROVAL_MODE", "review").lower()
        try:
            approval_mode = AIApprovalMode(approval_mode_str)
        except ValueError:
            approval_mode = AIApprovalMode.REVIEW
        
        config = cls(
            # Core
            enabled=get_bool("AI_SYSTEM_ENABLED", True),
            dry_run=get_bool("AI_SYSTEM_DRY_RUN", False),
            approval_mode=approval_mode,
            
            # Auto-scaling
            auto_scale_enabled=get_bool("AI_SYSTEM_AUTO_SCALE", True),
            max_workers=get_int("AI_SYSTEM_MAX_WORKERS", 10),
            min_workers=get_int("AI_SYSTEM_MIN_WORKERS", 1),
            
            # Resource thresholds
            cpu_threshold_high=get_float("AI_SYSTEM_CPU_THRESHOLD_HIGH", 80.0),
            cpu_threshold_low=get_float("AI_SYSTEM_CPU_THRESHOLD_LOW", 30.0),
            memory_limit_mb=get_int("AI_SYSTEM_MEMORY_LIMIT_MB", 4096),
            memory_threshold_percent=get_float("AI_SYSTEM_MEMORY_THRESHOLD", 85.0),
            
            # Monitoring
            monitoring_interval_seconds=get_int("AI_SYSTEM_MONITORING_INTERVAL", 60),
            health_check_interval_seconds=get_int("AI_SYSTEM_HEALTH_CHECK_INTERVAL", 30),
            
            # Safety
            max_decisions_per_hour=get_int("AI_SYSTEM_MAX_DECISIONS_PER_HOUR", 20),
            max_actions_per_hour=get_int("AI_SYSTEM_MAX_ACTIONS_PER_HOUR", 10),
            max_restarts_per_hour=get_int("AI_SYSTEM_MAX_RESTARTS_PER_HOUR", 5),
            
            # LLM
            llm_enabled=get_bool("AI_SYSTEM_LLM_ENABLED", False),
            llm_model=os.getenv("AI_SYSTEM_LLM_MODEL", "gpt-4"),
            llm_api_key=os.getenv("AI_SYSTEM_LLM_API_KEY", ""),
            
            # Logging
            log_level=os.getenv("AI_SYSTEM_LOG_LEVEL", "INFO"),
            log_decisions=get_bool("AI_SYSTEM_LOG_DECISIONS", True),
            log_actions=get_bool("AI_SYSTEM_LOG_ACTIONS", True),
        )
        
        logger.info(
            f"🤖 System AI config loaded: enabled={config.enabled}, "
            f"approval_mode={config.approval_mode.value}, "
            f"auto_scale={config.auto_scale_enabled}"
        )
        
        return config


# Global singleton
_config: SystemAIConfig | None = None


def get_system_ai_config() -> SystemAIConfig:
    """Get system AI configuration (singleton)"""
    global _config
    if _config is None:
        _config = SystemAIConfig.from_env()
    return _config


def reload_system_ai_config() -> SystemAIConfig:
    """Reload configuration from environment"""
    global _config
    _config = SystemAIConfig.from_env()
    return _config
