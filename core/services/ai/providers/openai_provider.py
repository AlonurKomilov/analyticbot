"""
OpenAI Provider Implementation
================================

Adapter for OpenAI GPT models (GPT-4, GPT-3.5, etc.)
"""

import tiktoken
from openai import AsyncOpenAI
from typing import Optional

from core.services.ai.base_provider import BaseAIProvider
from core.services.ai.models import AIMessage, AIResponse, AIProviderConfig, ProviderInfo


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider implementation."""
    
    # Pricing per 1M tokens (USD) - Updated Dec 2024
    PRICING = {
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-32k": {"input": 60.00, "output": 120.00},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},
    }
    
    AVAILABLE_MODELS = [
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4",
        "gpt-3.5-turbo",
    ]
    
    def __init__(self, config: AIProviderConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            timeout=config.timeout,
        )
        
        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(config.model)
        except KeyError:
            # Fallback to cl100k_base for newer models
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion using OpenAI API."""
        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=openai_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                **self.config.extra_params
            )
            
            usage = response.usage
            cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                tokens_used=usage.total_tokens,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost_usd=cost,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
            )
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Rough estimate: ~4 chars per token
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on OpenAI pricing."""
        # Get pricing for model (with fallback)
        model_key = self.config.model
        if model_key not in self.PRICING:
            # Try to match base model name
            for key in self.PRICING:
                if key in model_key:
                    model_key = key
                    break
            else:
                # Default to gpt-4-turbo pricing
                model_key = "gpt-4-turbo"
        
        pricing = self.PRICING[model_key]
        
        # Calculate cost per million tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    @property
    def provider_info(self) -> ProviderInfo:
        """Get OpenAI provider information."""
        return ProviderInfo(
            name="openai",
            display_name="OpenAI",
            available_models=self.AVAILABLE_MODELS,
            default_model="gpt-4o-mini",
            supports_streaming=True,
            requires_system_message=True,
        )
