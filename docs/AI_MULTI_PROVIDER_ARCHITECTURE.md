# AI Multi-Provider Architecture

## 🎯 Vision

Create a **flexible, multi-provider AI system** that supports:
- OpenAI (GPT-4, GPT-4o, GPT-3.5)
- Anthropic Claude (Claude 3.5 Sonnet, Claude 3 Opus)
- Google Gemini (Gemini Pro, Gemini Flash)
- xAI Grok
- Alibaba Qwen
- **User's own API keys** for any provider

Users choose their preferred AI provider and add their own API keys, giving them:
✅ Cost control
✅ Provider flexibility
✅ Privacy (their own keys)
✅ Model selection

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│          User AI Agent (apps/ai/user/)          │
│  - analyze_channel()                            │
│  - suggest_content()                            │
│  - get_posting_recommendations()                │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────▼─────────┐
         │  AI Provider     │
         │  Abstraction     │
         │  Layer           │
         └────────┬─────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐   ┌───▼────┐
│OpenAI │   │ Claude  │   │ Gemini  │   │  Grok  │
│Adapter│   │ Adapter │   │ Adapter │   │ Adapter│
└───────┘   └─────────┘   └─────────┘   └────────┘
```

### Key Components

1. **AI Provider Interface** - Abstract base class
2. **Provider Adapters** - One per AI provider
3. **Provider Registry** - Dynamic provider management
4. **User API Keys** - Encrypted storage in database
5. **Unified Response Format** - Consistent API regardless of provider

---

## 📊 Database Schema Updates

### New Table: `user_ai_providers`

```sql
CREATE TABLE user_ai_providers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL,  -- 'openai', 'claude', 'gemini', 'grok', etc.
    api_key_encrypted TEXT NOT NULL,     -- Encrypted API key
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,    -- User's default provider
    model_preference VARCHAR(100),       -- e.g., 'gpt-4-turbo', 'claude-3-opus'
    config JSONB,                        -- Provider-specific settings
    monthly_budget DECIMAL(10,2),        -- Optional spending limit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, provider_name)
);

CREATE INDEX idx_user_ai_providers_user_id ON user_ai_providers(user_id);
CREATE INDEX idx_user_ai_providers_active ON user_ai_providers(user_id, is_active);
```

### Update: `user_ai_config` table

Add column for default provider preference:
```sql
ALTER TABLE user_ai_config 
ADD COLUMN default_provider VARCHAR(50) DEFAULT 'system';
-- 'system' = use system keys, or specific provider name
```

---

## 🔌 Provider Interface Design

### Base Interface

```python
# core/services/ai/base_provider.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AIMessage:
    """Unified message format."""
    role: str  # 'system', 'user', 'assistant'
    content: str

@dataclass
class AIResponse:
    """Unified response format."""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost_usd: float
    finish_reason: str
    raw_response: Any

@dataclass
class AIProviderConfig:
    """Provider configuration."""
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30

class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: AIProviderConfig):
        self.config = config
    
    @abstractmethod
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion."""
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """List of available models."""
        pass
```

---

## 🔧 Provider Implementations

### 1. OpenAI Adapter

```python
# core/services/ai/providers/openai_provider.py

from openai import AsyncOpenAI
import tiktoken

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider."""
    
    name = "openai"
    available_models = [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4o",
    ]
    
    # Pricing per 1M tokens (as of Dec 2024)
    PRICING = {
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=config.api_key)
        self.encoding = tiktoken.encoding_for_model(config.model)
    
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )
        
        usage = response.usage
        cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            provider=self.name,
            tokens_used=usage.total_tokens,
            cost_usd=cost,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response,
        )
```

### 2. Claude Adapter

```python
# core/services/ai/providers/claude_provider.py

from anthropic import AsyncAnthropic

class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider."""
    
    name = "claude"
    available_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    PRICING = {
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    }
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client = AsyncAnthropic(api_key=config.api_key)
    
    async def complete(
        self,
        messages: list[AIMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        # Extract system message
        system_msg = next((m.content for m in messages if m.role == "system"), None)
        user_msgs = [m for m in messages if m.role != "system"]
        
        response = await self.client.messages.create(
            model=self.config.model,
            system=system_msg,
            messages=[{"role": m.role, "content": m.content} for m in user_msgs],
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )
        
        cost = self.calculate_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )
        
        return AIResponse(
            content=response.content[0].text,
            model=response.model,
            provider=self.name,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            cost_usd=cost,
            finish_reason=response.stop_reason,
            raw_response=response,
        )
```

### 3. Gemini Adapter

```python
# core/services/ai/providers/gemini_provider.py

import google.generativeai as genai

class GeminiProvider(BaseAIProvider):
    """Google Gemini provider."""
    
    name = "gemini"
    available_models = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro",
    ]
    
    PRICING = {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }
```

### 4. Grok Adapter

```python
# core/services/ai/providers/grok_provider.py

class GrokProvider(BaseAIProvider):
    """xAI Grok provider."""
    
    name = "grok"
    available_models = [
        "grok-beta",
        "grok-vision-beta",
    ]
```

---

## 🔐 API Key Management

### Encryption

```python
# core/security/encryption.py

from cryptography.fernet import Fernet
from config.settings import settings

class APIKeyEncryption:
    """Encrypt/decrypt user API keys."""
    
    def __init__(self):
        # Store encryption key in environment variable
        self.cipher = Fernet(settings.API_KEY_ENCRYPTION_KEY)
    
    def encrypt(self, api_key: str) -> str:
        """Encrypt API key."""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt(self, encrypted_key: str) -> str:
        """Decrypt API key."""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

### Repository

```python
# core/repositories/user_ai_providers_repository.py

class UserAIProvidersRepository:
    """Manage user's AI provider API keys."""
    
    async def add_provider(
        self,
        user_id: int,
        provider_name: str,
        api_key: str,  # Will be encrypted
        model: str,
        is_default: bool = False,
    ) -> dict:
        """Add or update user's AI provider."""
        encrypted_key = self.encryption.encrypt(api_key)
        # ... save to database
    
    async def get_active_provider(self, user_id: int) -> Optional[dict]:
        """Get user's active/default provider."""
        # ... query database
    
    async def decrypt_api_key(self, user_id: int, provider_name: str) -> str:
        """Get decrypted API key for provider."""
        # ... fetch and decrypt
```

---

## 🎨 Provider Registry

```python
# core/services/ai/provider_registry.py

from typing import Type
from core.services.ai.base_provider import BaseAIProvider
from core.services.ai.providers.openai_provider import OpenAIProvider
from core.services.ai.providers.claude_provider import ClaudeProvider
from core.services.ai.providers.gemini_provider import GeminiProvider
from core.services.ai.providers.grok_provider import GrokProvider

class AIProviderRegistry:
    """Registry of available AI providers."""
    
    _providers: dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "grok": GrokProvider,
    }
    
    @classmethod
    def get_provider(cls, name: str) -> Type[BaseAIProvider]:
        """Get provider class by name."""
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name]
    
    @classmethod
    def list_providers(cls) -> list[dict]:
        """List all available providers."""
        return [
            {
                "name": name,
                "display_name": provider.name,
                "models": provider.available_models,
            }
            for name, provider in cls._providers.items()
        ]
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseAIProvider]):
        """Register a custom provider."""
        cls._providers[name] = provider_class
```

---

## 🚀 Usage in User AI Agent

```python
# apps/ai/user/agent.py

from core.services.ai.provider_registry import AIProviderRegistry
from core.services.ai.base_provider import AIMessage, AIProviderConfig
from core.repositories.user_ai_providers_repository import UserAIProvidersRepository

class UserAIAgent:
    """User AI Agent with multi-provider support."""
    
    async def _get_provider(self):
        """Get user's configured AI provider."""
        # Check if user has their own API key
        user_provider = await self.providers_repo.get_active_provider(self.user_id)
        
        if user_provider:
            # Use user's own API key
            provider_class = AIProviderRegistry.get_provider(user_provider["provider_name"])
            api_key = await self.providers_repo.decrypt_api_key(
                self.user_id,
                user_provider["provider_name"]
            )
            
            config = AIProviderConfig(
                api_key=api_key,
                model=user_provider["model_preference"],
                temperature=self.config.settings.temperature,
            )
            
            return provider_class(config)
        else:
            # Use system default (paid by us)
            return await self._get_system_provider()
    
    async def analyze_channel(self, channel_id: int, analysis_type: str):
        """Analyze channel using user's preferred AI provider."""
        provider = await self._get_provider()
        
        messages = [
            AIMessage(role="system", content="You are a Telegram channel analyst..."),
            AIMessage(role="user", content=f"Analyze channel {channel_id}..."),
        ]
        
        response = await provider.complete(messages)
        
        # Track usage
        await self.usage_repo.increment_usage(
            user_id=self.user_id,
            tokens=response.tokens_used,
            cost=response.cost_usd,
        )
        
        return {
            "insights": self._parse_insights(response.content),
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used,
        }
```

---

## 📱 API Endpoints

### Manage AI Providers

```python
# apps/api/routers/user_ai_providers_router.py

@router.get("/providers/available")
async def list_available_providers():
    """List all supported AI providers."""
    return AIProviderRegistry.list_providers()

@router.post("/providers/add")
async def add_ai_provider(
    request: AddProviderRequest,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
):
    """Add user's own AI API key."""
    # Validate API key by testing it
    await validate_api_key(request.provider, request.api_key)
    
    # Save encrypted
    await repo.add_provider(
        user_id=user_id,
        provider_name=request.provider,
        api_key=request.api_key,
        model=request.model,
        is_default=request.set_as_default,
    )
    
    return {"success": True, "provider": request.provider}

@router.get("/providers/mine")
async def list_my_providers(
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
):
    """List user's configured providers."""
    providers = await repo.get_user_providers(user_id)
    
    # Don't return actual API keys
    return [
        {
            "provider": p["provider_name"],
            "model": p["model_preference"],
            "is_default": p["is_default"],
            "api_key_preview": p["api_key_encrypted"][:10] + "...",
        }
        for p in providers
    ]

@router.delete("/providers/{provider_name}")
async def remove_provider(
    provider_name: str,
    user_id: int = Depends(get_current_user_id),
    repo = Depends(get_user_ai_providers_repo),
):
    """Remove a configured provider."""
    await repo.remove_provider(user_id, provider_name)
    return {"success": True}
```

---

## 🎯 Updated Phase 4 Plan

### Phase 4: Multi-Provider AI System (4 days)

#### Day 1: Provider Abstraction Layer
- Create `BaseAIProvider` interface
- Implement provider registry
- Create unified response format
- Set up encryption for API keys

#### Day 2: Core Provider Adapters
- Implement OpenAI adapter
- Implement Claude adapter
- Implement Gemini adapter
- Add token counting & cost calculation

#### Day 3: User Provider Management
- Create `user_ai_providers` table migration
- Create `UserAIProvidersRepository`
- Add API endpoints for managing providers
- Implement API key validation

#### Day 4: Integration & Testing
- Update `UserAIAgent` to use providers
- Implement channel analysis with multi-provider
- Add content generation
- Test all providers

---

## 💰 Cost Management

### User Budget Tracking

```python
# In user_ai_providers table
monthly_budget DECIMAL(10,2)  -- Optional spending limit

# Track spending
CREATE TABLE user_ai_spending (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    provider_name VARCHAR(50),
    month DATE,  -- First day of month
    total_cost_usd DECIMAL(10,2) DEFAULT 0,
    request_count INT DEFAULT 0,
    UNIQUE(user_id, provider_name, month)
);
```

### Budget Alerts

```python
async def check_budget(user_id: int, provider: str, cost: float):
    """Check if user is within budget."""
    spending = await get_monthly_spending(user_id, provider)
    budget = await get_user_budget(user_id, provider)
    
    if budget and spending + cost > budget:
        raise BudgetExceededError(
            f"Monthly budget of ${budget} exceeded"
        )
```

---

## 🔒 Security Considerations

1. **API Key Encryption**: Use Fernet (symmetric encryption)
2. **Key Rotation**: Support periodic re-encryption
3. **Validation**: Test API keys before saving
4. **Scope Limiting**: Store only necessary permissions
5. **Audit Logging**: Track all API key usage

---

## 📊 Frontend Integration

Users can manage their AI providers in settings:

```typescript
// AI Provider Settings Page
interface AIProvider {
  name: string;
  displayName: string;
  models: string[];
  isConfigured: boolean;
  isDefault: boolean;
}

// Add Provider Modal
<AddProviderModal>
  <Select provider="openai" />
  <Input apiKey="sk-..." type="password" />
  <Select model="gpt-4-turbo" />
  <Input monthlyBudget="$50" optional />
  <Checkbox setAsDefault />
</AddProviderModal>
```

---

## ✅ Benefits

1. **User Control**: Users bring their own API keys
2. **Cost Savings**: No need to subsidize AI costs for all users
3. **Flexibility**: Users choose their preferred provider
4. **Privacy**: User data processed with their own keys
5. **Scalability**: No single provider dependency
6. **Future-Proof**: Easy to add new providers

---

## 🚀 Next Steps

1. Create database migration for `user_ai_providers`
2. Implement base provider interface
3. Add OpenAI + Claude adapters (most popular)
4. Create provider management API endpoints
5. Update frontend settings page

**This architecture is production-ready and scales to millions of users!**
