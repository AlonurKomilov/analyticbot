# Quick Start: Multi-Provider AI System

Get started with the multi-provider AI system in 5 minutes!

## 1. Install Dependencies

```bash
cd /home/abcdev/projects/analyticbot
venv/bin/pip install openai anthropic tiktoken cryptography
```

## 2. Verify Environment

Check that encryption key is set in `.env.development`:

```bash
grep API_KEY_ENCRYPTION_KEY .env.development
```

Should show:
```
API_KEY_ENCRYPTION_KEY=ug7XYttYRDeVa_OY-5Whgsy7dyCcW1EODf9gB90006o=
```

## 3. Run Tests

```bash
export API_KEY_ENCRYPTION_KEY="ug7XYttYRDeVa_OY-5Whgsy7dyCcW1EODf9gB90006o="
venv/bin/python tests/test_ai_providers.py
```

Expected output:
```
✅ Encryption/Decryption works correctly!
✅ Registered Providers: 2 (OpenAI, Claude)
```

## 4. Start the API Server

```bash
make dev-start
# or
venv/bin/uvicorn apps.api.main:app --reload --port 8000
```

## 5. Test API Endpoints

### List Available Providers
```bash
curl http://localhost:8000/user/ai/providers/available
```

**Response:**
```json
{
  "providers": [
    {
      "name": "openai",
      "display_name": "OpenAI",
      "default_model": "gpt-4o-mini",
      "available_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", ...]
    },
    {
      "name": "claude",
      "display_name": "Anthropic Claude",
      "default_model": "claude-3-5-sonnet-20241022",
      "available_models": ["claude-3-5-sonnet-20241022", ...]
    }
  ]
}
```

### Add Your API Key

```bash
curl -X POST http://localhost:8000/user/ai/providers/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "provider": "openai",
    "api_key": "sk-proj-YOUR_OPENAI_KEY",
    "model": "gpt-4o-mini",
    "monthly_budget": 50.00
  }'
```

**Response:**
```json
{
  "provider": "openai",
  "display_name": "OpenAI",
  "model": "gpt-4o-mini",
  "api_key_preview": "sk-proj-YOUR...",
  "monthly_budget": 50.00,
  "is_default": true,
  "message": "Provider added successfully"
}
```

### List Your Providers

```bash
curl http://localhost:8000/user/ai/providers/mine \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Analyze a Channel (with AI!)

```bash
curl -X POST http://localhost:8000/user/ai/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "channel_id": 123,
    "analysis_type": "engagement"
  }'
```

**Response:**
```json
{
  "insights": [
    "Peak engagement occurs between 6-9 PM",
    "Video content gets 3x more engagement than text",
    "Subscribers are most active on weekends"
  ],
  "model": "gpt-4o-mini",
  "tokens_used": 450,
  "cost": 0.00027,
  "provider": "openai"
}
```

### Check Spending

```bash
curl http://localhost:8000/user/ai/providers/openai/spending \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "provider": "openai",
  "monthly_budget": 50.00,
  "current_spending": 0.00027,
  "remaining_budget": 49.99973,
  "usage_percentage": 0.00054,
  "period": "2024-12"
}
```

## 6. Add More Providers (Optional)

### Claude
```bash
curl -X POST http://localhost:8000/user/ai/providers/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "provider": "claude",
    "api_key": "sk-ant-YOUR_CLAUDE_KEY",
    "model": "claude-3-5-sonnet-20241022",
    "monthly_budget": 100.00
  }'
```

### Set as Default
```bash
curl -X PUT http://localhost:8000/user/ai/providers/claude/set-default \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 7. Remove a Provider

```bash
curl -X DELETE http://localhost:8000/user/ai/providers/openai \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Architecture Overview

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   API Router            │
│ /user/ai/providers/*    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  UserAIAgent            │
│  - Get provider         │
│  - Make AI call         │
│  - Track usage          │
└────────┬────────────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌─────────┐  ┌──────────────────┐
│ OpenAI  │  │ Claude           │
│Provider │  │ Provider         │
└─────────┘  └──────────────────┘
    │              │
    ▼              ▼
┌────────────────────────────────┐
│     AI API (OpenAI/Anthropic)  │
└────────────────────────────────┘
```

## Database Schema

```sql
-- User API Keys (encrypted)
user_ai_providers
├── user_id
├── provider (openai, claude, gemini...)
├── encrypted_api_key
├── model
├── monthly_budget
└── is_default

-- Monthly Spending
user_ai_spending
├── user_id
├── provider
├── year_month (2024-12)
├── tokens_used
└── cost_usd
```

## Supported Providers

### OpenAI
- **Models:** GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Pricing:** $0.15-$30 per 1M tokens
- **API Key:** Get from https://platform.openai.com/api-keys

### Anthropic Claude
- **Models:** Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Pricing:** $0.25-$75 per 1M tokens
- **API Key:** Get from https://console.anthropic.com/

### Coming Soon
- Google Gemini
- xAI Grok
- Mistral AI
- Cohere

## Security Notes

✅ **All API keys are encrypted** with Fernet (AES-128)  
✅ **Keys never appear in responses** (preview only: first 10 chars)  
✅ **Budget protection** prevents overspending  
✅ **API validation** before saving keys  

## Troubleshooting

### "API_KEY_ENCRYPTION_KEY not set"
Add to `.env.development`:
```bash
API_KEY_ENCRYPTION_KEY=ug7XYttYRDeVa_OY-5Whgsy7dyCcW1EODf9gB90006o=
```

### "Invalid API key"
- Verify key format (starts with `sk-proj-` for OpenAI, `sk-ant-` for Claude)
- Check key has sufficient permissions
- Test manually: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

### "Budget exceeded"
- Check current spending: `GET /user/ai/providers/{provider}/spending`
- Increase monthly_budget or wait for monthly reset

## Next Steps

1. **Frontend Integration:** Build UI for provider management
2. **Add More Providers:** Gemini, Grok, Mistral
3. **Advanced Features:** Model comparison, cost optimization
4. **Analytics:** Track provider performance over time

## Documentation

- **Full Guide:** [MULTI_PROVIDER_AI_SYSTEM.md](./MULTI_PROVIDER_AI_SYSTEM.md)
- **API Reference:** http://localhost:8000/docs (FastAPI Swagger)
- **Test Suite:** `tests/test_ai_providers.py`

---

**System Status:** ✅ Production-Ready  
**Real AI:** ✅ No mocks, everything works!  
**Encryption:** ✅ All API keys encrypted  
**Cost Tracking:** ✅ Automatic spending monitoring
