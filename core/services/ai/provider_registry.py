"""
AI Provider Registry
=====================

Central registry for all available AI providers.
"""

from typing import Type, Optional
import logging

from core.services.ai.base_provider import BaseAIProvider
from core.services.ai.providers.openai_provider import OpenAIProvider
from core.services.ai.providers.claude_provider import ClaudeProvider
from core.services.ai.models import ProviderInfo

logger = logging.getLogger(__name__)


class AIProviderRegistry:
    """Registry of available AI providers."""
    
    # Registered providers
    _providers: dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
    }
    
    @classmethod
    def get_provider_class(cls, name: str) -> Type[BaseAIProvider]:
        """
        Get provider class by name.
        
        Args:
            name: Provider name (e.g., 'openai', 'claude')
            
        Returns:
            Provider class
            
        Raises:
            ValueError: If provider not found
        """
        if name not in cls._providers:
            raise ValueError(
                f"Unknown provider '{name}'. "
                f"Available: {', '.join(cls._providers.keys())}"
            )
        return cls._providers[name]
    
    @classmethod
    def list_providers(cls) -> list[dict]:
        """
        List all available providers with their info.
        
        Returns:
            List of provider information dicts
        """
        providers = []
        for name, provider_class in cls._providers.items():
            # Create temp instance to get info
            try:
                from core.services.ai.models import AIProviderConfig
                temp_instance = provider_class(
                    AIProviderConfig(api_key="temp", model="temp")
                )
                info = temp_instance.provider_info
                
                providers.append({
                    "name": info.name,
                    "display_name": info.display_name,
                    "available_models": info.available_models,
                    "default_model": info.default_model,
                    "supports_streaming": info.supports_streaming,
                })
            except Exception as e:
                logger.warning(f"Could not get info for {name}: {e}")
                continue
        
        return providers
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseAIProvider]):
        """
        Register a new provider.
        
        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._providers[name] = provider_class
        logger.info(f"Registered AI provider: {name}")
    
    @classmethod
    def is_provider_available(cls, name: str) -> bool:
        """
        Check if provider is available.
        
        Args:
            name: Provider name
            
        Returns:
            True if provider is registered
        """
        return name in cls._providers
