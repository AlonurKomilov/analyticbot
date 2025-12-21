"""
Base AI Provider Interface
===========================

Abstract base class for all AI provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

from core.services.ai.models import AIMessage, AIResponse, AIProviderConfig, ProviderInfo

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AIProviderConfig):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration including API key
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """
        Generate AI completion.
        
        Args:
            messages: List of messages in conversation
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            AIResponse with generated content
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in USD for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        pass
    
    @property
    @abstractmethod
    def provider_info(self) -> ProviderInfo:
        """Get provider information."""
        pass
    
    async def test_connection(self) -> bool:
        """
        Test if API key is valid.
        
        Returns:
            True if connection successful
        """
        try:
            response = await self.complete(
                messages=[AIMessage(role="user", content="test")],
                max_tokens=5
            )
            return response.content is not None
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
