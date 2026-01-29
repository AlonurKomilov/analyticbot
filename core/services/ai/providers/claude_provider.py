"""
Anthropic Claude Provider Implementation
==========================================

Adapter for Claude models (Claude 3.5 Sonnet, Opus, Haiku)
"""

from anthropic import AsyncAnthropic

from core.services.ai.base_provider import BaseAIProvider
from core.services.ai.models import (
    AIMessage,
    AIProviderConfig,
    AIResponse,
    ProviderInfo,
)


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider implementation."""

    # Pricing per 1M tokens (USD) - Updated Dec 2024
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    }

    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    def __init__(self, config: AIProviderConfig):
        """Initialize Claude provider."""
        super().__init__(config)
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            timeout=config.timeout,
        )

    async def complete(
        self,
        messages: list[AIMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AIResponse:
        """Generate completion using Claude API."""
        # Extract system message (Claude requires it separately)
        system_message = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                user_messages.append({"role": msg.role, "content": msg.content})

        try:
            response = await self.client.messages.create(
                model=self.config.model,
                system=system_message,
                messages=user_messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                **self.config.extra_params,
            )

            usage = response.usage
            cost = self.calculate_cost(usage.input_tokens, usage.output_tokens)

            return AIResponse(
                content=response.content[0].text,
                model=response.model,
                provider="claude",
                tokens_used=usage.input_tokens + usage.output_tokens,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cost_usd=cost,
                finish_reason=response.stop_reason,
                raw_response=response,
            )
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate tokens for Claude.
        Claude uses ~3.5 characters per token on average.
        """
        # More accurate would be to use anthropic.count_tokens()
        # but this requires async call, so we estimate
        return int(len(text) / 3.5)

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on Claude pricing."""
        # Get pricing for model (with fallback)
        model_key = self.config.model
        if model_key not in self.PRICING:
            # Try to match base model name
            for key in self.PRICING:
                if key in model_key or model_key in key:
                    model_key = key
                    break
            else:
                # Default to Sonnet pricing
                model_key = "claude-3-5-sonnet"

        pricing = self.PRICING[model_key]

        # Calculate cost per million tokens
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    @property
    def provider_info(self) -> ProviderInfo:
        """Get Claude provider information."""
        return ProviderInfo(
            name="claude",
            display_name="Anthropic Claude",
            available_models=self.AVAILABLE_MODELS,
            default_model="claude-3-5-sonnet-20241022",
            supports_streaming=True,
            requires_system_message=True,
        )
