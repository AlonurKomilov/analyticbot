"""
AI Provider Base Models
=======================

Data models for multi-provider AI system.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AIMessage:
    """Unified message format across all providers."""
    role: str  # 'system', 'user', 'assistant'
    content: str
    name: Optional[str] = None  # For multi-agent scenarios


@dataclass
class AIResponse:
    """Unified AI completion response."""
    content: str
    model: str
    provider: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    finish_reason: str  # 'stop', 'length', 'content_filter', etc.
    raw_response: Any = None  # Original provider response


@dataclass
class AIProviderConfig:
    """Configuration for AI provider."""
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30
    extra_params: dict = field(default_factory=dict)


@dataclass
class ProviderInfo:
    """Information about an AI provider."""
    name: str
    display_name: str
    available_models: list[str]
    default_model: str
    supports_streaming: bool = False
    requires_system_message: bool = True
