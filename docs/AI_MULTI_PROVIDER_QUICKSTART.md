# 🚀 AI Multi-Provider System - Quick Start

## What's Different Now?

**Before:** Only OpenAI support  
**Now:** Support for ALL major AI providers + user's own API keys

---

## 🎯 Vision

Users can:
1. **Choose their AI provider**: OpenAI, Claude, Gemini, Grok, Qwen, etc.
2. **Add their own API keys**: Full control and privacy
3. **Set spending limits**: Monthly budget per provider
4. **Switch anytime**: Use different providers for different tasks

---

## 🏗️ Architecture

```
User AI Agent
     ↓
Provider Registry (Auto-detect user's preference)
     ↓
┌─────────┬─────────┬─────────┬─────────┐
│ OpenAI  │ Claude  │ Gemini  │  Grok   │
│ Adapter │ Adapter │ Adapter │ Adapter │
└─────────┴─────────┴─────────┴─────────┘
```

**Key Principle:** Abstract interface = Easy to add new providers

---

## 📊 Database Changes

### New Tables

**1. `user_ai_providers`** - User's API keys (encrypted)
```sql
user_id | provider_name | api_key_encrypted | model_preference | is_default
--------|---------------|-------------------|------------------|------------
100005  | openai        | gAAAAA...         | gpt-4-turbo      | true
100005  | claude        | gAAAAA...         | claude-3-opus    | false
```

**2. `user_ai_spending`** - Budget tracking
```sql
user_id | provider_name | month      | total_cost_usd | request_count
--------|---------------|------------|----------------|---------------
100005  | openai        | 2024-12-01 | 15.50          | 450
```

**3. Update `user_ai_config`**
```sql
ALTER TABLE user_ai_config 
ADD COLUMN default_provider VARCHAR(50) DEFAULT 'system';
```

- `'system'` = Use platform's API keys (paid by us)
- `'openai'` = Use user's OpenAI key
- `'claude'` = Use user's Claude key

---

## 🔌 Supported Providers

### Launch (Phase 4)
- ✅ **OpenAI** - GPT-4 Turbo, GPT-4o, GPT-3.5
- ✅ **Claude** - Claude 3.5 Sonnet, Opus, Haiku
- ✅ **Gemini** - Gemini 1.5 Pro, Flash

### Future (Easy to add)
- ⏳ **Grok** - xAI's models
- ⏳ **Qwen** - Alibaba's models
- ⏳ **Llama** - Meta's open models
- ⏳ **Mistral** - European AI
- ⏳ **Custom** - User's own endpoints

---

## 💻 Code Example

### User adds their Claude API key:

```python
# Frontend
await api.post('/user/ai/providers/add', {
  provider: 'claude',
  apiKey: 'sk-ant-...',
  model: 'claude-3-5-sonnet-20241022',
  monthlyBudget: 50.00,
  setAsDefault: true
})
```

### Backend processes request:

```python
# Encrypt and save
encrypted_key = encryption.encrypt(request.api_key)

await db.execute("""
  INSERT INTO user_ai_providers 
  (user_id, provider_name, api_key_encrypted, model_preference, is_default)
  VALUES ($1, $2, $3, $4, $5)
""", user_id, 'claude', encrypted_key, 'claude-3-5-sonnet', True)
```

### Agent uses it automatically:

```python
# User calls analyze_channel()
agent = UserAIAgent(user_id=100005)
result = await agent.analyze_channel(channel_id=123)

# Agent automatically:
# 1. Checks user_ai_providers for default provider
# 2. Decrypts API key
# 3. Creates ClaudeProvider instance
# 4. Sends request to Claude API
# 5. Tracks cost and usage
# 6. Returns unified response
```

---

## 🎨 Frontend UI

### Settings Page: AI Providers

```
┌─────────────────────────────────────────────┐
│  Your AI Providers                          │
├─────────────────────────────────────────────┤
│                                             │
│  ✅ Claude 3.5 Sonnet (Default)            │
│     Model: claude-3-5-sonnet-20241022       │
│     Budget: $50/month | Used: $12.30        │
│     [Edit] [Remove]                         │
│                                             │
│  ✅ OpenAI GPT-4 Turbo                     │
│     Model: gpt-4-turbo-preview              │
│     Budget: $30/month | Used: $8.50         │
│     [Edit] [Set as Default] [Remove]        │
│                                             │
│  [+ Add New Provider]                       │
│                                             │
└─────────────────────────────────────────────┘

Available Providers:
  • OpenAI (GPT-4, GPT-3.5)
  • Claude (Sonnet, Opus, Haiku)
  • Gemini (Pro, Flash)
  • Grok (Beta)
```

---

## 💰 Pricing Comparison

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|-------|----------------------|------------------------|
| OpenAI | GPT-4 Turbo | $10 | $30 |
| OpenAI | GPT-3.5 Turbo | $0.50 | $1.50 |
| Claude | 3.5 Sonnet | $3 | $15 |
| Claude | 3 Haiku | $0.25 | $1.25 |
| Gemini | 1.5 Pro | $1.25 | $5 |
| Gemini | 1.5 Flash | $0.075 | $0.30 |

**Users can choose based on:**
- Cost (Gemini Flash cheapest)
- Quality (Claude Opus best for writing)
- Speed (GPT-3.5 fastest)
- Features (GPT-4 best for code)

---

## 🔐 Security

### API Key Encryption

```python
from cryptography.fernet import Fernet

# In .env file:
API_KEY_ENCRYPTION_KEY=gAAAAA...  # Generated once

# Encrypt before saving
cipher = Fernet(settings.API_KEY_ENCRYPTION_KEY)
encrypted = cipher.encrypt(user_api_key.encode())

# Decrypt when using
decrypted = cipher.decrypt(encrypted_key.encode())
```

### Validation

```python
# Test API key before saving
async def validate_api_key(provider: str, api_key: str):
    """Test if API key works."""
    provider_class = AIProviderRegistry.get_provider(provider)
    test_provider = provider_class(AIProviderConfig(
        api_key=api_key,
        model=provider_class.available_models[0]
    ))
    
    # Make a minimal test request
    response = await test_provider.complete([
        AIMessage(role="user", content="test")
    ], max_tokens=5)
    
    return response.content is not None
```

---

## 📱 API Endpoints

### Provider Management

```
GET    /user/ai/providers/available
       → List all supported providers and models

GET    /user/ai/providers/mine
       → List user's configured providers

POST   /user/ai/providers/add
       Body: {provider, apiKey, model, monthlyBudget, setAsDefault}
       → Add new provider API key

PUT    /user/ai/providers/{provider}/set-default
       → Set as default provider

PUT    /user/ai/providers/{provider}/update
       Body: {model, monthlyBudget}
       → Update provider settings

DELETE /user/ai/providers/{provider}
       → Remove provider

GET    /user/ai/providers/{provider}/spending
       → Get spending stats for provider
```

---

## 🚀 Implementation Timeline

### Day 5: Abstraction Layer
- ✅ Create `BaseAIProvider` interface
- ✅ Create `AIProviderRegistry`
- ✅ Set up encryption system
- ✅ Define unified response format

### Day 6: Provider Adapters
- ✅ OpenAI adapter
- ✅ Claude adapter
- ✅ Gemini adapter
- ✅ Token counting
- ✅ Cost calculation

### Day 7: User Management
- ✅ Database migration
- ✅ Repository for API keys
- ✅ API endpoints
- ✅ Key validation
- ✅ Budget tracking

### Day 8: Integration
- ✅ Update UserAIAgent
- ✅ Implement channel analysis
- ✅ Test all providers
- ✅ Frontend integration

---

## ✅ Benefits

### For Users
- 💰 **Save Money**: Use cheaper providers (Gemini Flash = $0.075 vs GPT-4 = $10)
- 🔒 **Privacy**: Their data processed with their own keys
- 🎯 **Choice**: Pick best provider for each task
- 📊 **Budget Control**: Set spending limits
- 🚀 **No Lock-in**: Switch providers anytime

### For Platform
- 💸 **No AI Costs**: Users bring their own keys
- 📈 **Scalable**: No single provider dependency
- 🌍 **Global**: Support regional providers (Qwen in China, etc.)
- 🔮 **Future-Proof**: Easy to add new AI companies

---

## 🎯 Next Steps

1. ✅ Review multi-provider architecture
2. ⏳ Run migration for `user_ai_providers` table
3. ⏳ Implement base provider interface
4. ⏳ Add OpenAI + Claude adapters
5. ⏳ Create provider management endpoints
6. ⏳ Update frontend settings page

**Ready to build the most flexible AI system!** 🚀
