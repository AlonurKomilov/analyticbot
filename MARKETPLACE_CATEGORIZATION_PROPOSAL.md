# 🏷️ Marketplace Service Categorization Proposal

## Current State
- **10 services** across 3 backend categories
- Single "Services" category in frontend
- No subcategory filtering

## Service Breakdown

### Bot Moderation Services (6)
| Service Key | Name | Subcategory | Price (Monthly) |
|-------------|------|-------------|-----------------|
| `bot_anti_spam` | Anti-Spam Protection | spam_prevention | 50 credits |
| `bot_auto_delete_joins` | Auto-Delete Join/Leave | chat_cleanup | 30 credits |
| `bot_banned_words` | Banned Words Filter | content_filter | 40 credits |
| `bot_welcome_messages` | Welcome Messages | engagement | 20 credits |
| `bot_invite_tracking` | Invite Link Tracking | analytics | 35 credits |
| `bot_warning_system` | Warning System | enforcement | 45 credits |

### MTProto Services (3)
| Service Key | Name | Subcategory | Price (Monthly) |
|-------------|------|-------------|-----------------|
| `mtproto_history_access` | MTProto History Access | data_access | 100 credits |
| `mtproto_bulk_export` | Bulk Message Export | bulk_operations | 150 credits |
| `mtproto_auto_collect` | MTProto Auto-Collection | automation | 80 credits |

### Analytics Services (1)
| Service Key | Name | Subcategory | Price (Monthly) |
|-------------|------|-------------|-----------------|
| `bot_analytics_advanced` | Advanced Bot Analytics | insights | 60 credits |

---

## 🎯 Recommended Approach: Multi-Tag System

### Implementation Plan

**1. Database: Add tags column to marketplace_services**
```sql
ALTER TABLE marketplace_services 
ADD COLUMN tags TEXT[] DEFAULT '{}';

-- Update existing services with tags
UPDATE marketplace_services SET tags = ARRAY['moderation', 'security'] WHERE service_key = 'bot_anti_spam';
UPDATE marketplace_services SET tags = ARRAY['moderation', 'cleanup'] WHERE service_key = 'bot_auto_delete_joins';
UPDATE marketplace_services SET tags = ARRAY['moderation', 'content'] WHERE service_key = 'bot_banned_words';
UPDATE marketplace_services SET tags = ARRAY['moderation', 'engagement'] WHERE service_key = 'bot_welcome_messages';
UPDATE marketplace_services SET tags = ARRAY['moderation', 'analytics'] WHERE service_key = 'bot_invite_tracking';
UPDATE marketplace_services SET tags = ARRAY['moderation', 'enforcement'] WHERE service_key = 'bot_warning_system';
UPDATE marketplace_services SET tags = ARRAY['mtproto', 'data_access'] WHERE service_key = 'mtproto_history_access';
UPDATE marketplace_services SET tags = ARRAY['mtproto', 'export'] WHERE service_key = 'mtproto_bulk_export';
UPDATE marketplace_services SET tags = ARRAY['mtproto', 'automation'] WHERE service_key = 'mtproto_auto_collect';
UPDATE marketplace_services SET tags = ARRAY['analytics', 'insights'] WHERE service_key = 'bot_analytics_advanced';
```

**2. Frontend: Sub-navigation under Services category**
```
Premium Services
  ├─ All (10)
  ├─ 🛡️ Moderation (6)
  ├─ 📡 MTProto (3)
  ├─ 📊 Analytics (1)
  └─ 🤖 AI (0) - Coming Soon
```

**3. UI: Secondary filter pills**
```tsx
// When "Services" category is selected, show sub-filters
<Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
  <Chip label="All Services" />
  <Chip label="🛡️ Moderation (6)" />
  <Chip label="📡 MTProto (3)" />
  <Chip label="📊 Analytics (1)" />
  <Chip label="🤖 AI (Coming Soon)" disabled />
</Box>
```

---

## Alternative: Backend Category Mapping

**Option A: Use existing `category` field**
Current backend categories:
- `bot_moderation` → 🛡️ Bot Moderation
- `mtproto_access` → 📡 MTProto Tools
- `bot_analytics` → 📊 Analytics & Insights

**Option B: Create service type filter**
Map services to user-friendly types:
- **Security** (anti-spam, banned words, warnings)
- **Community** (welcome, auto-delete, invite tracking)
- **Data Tools** (all MTProto services)
- **Analytics** (bot analytics, invite tracking)

---

## User Experience Flow

### Before (Current)
```
Marketplace → Services (10 items all mixed together)
```

### After (Recommended)
```
Marketplace → Services → [All | Moderation | MTProto | Analytics | AI]
                          ↓
                    6 moderation services shown
```

---

## Benefits

✅ **Scalability**: Easy to add new service types without UI changes
✅ **Discoverability**: Users find relevant services faster
✅ **Professional**: Matches modern marketplace UX (Slack, Zapier, Shopify)
✅ **Flexibility**: Services can belong to multiple categories via tags
✅ **Future-proof**: AI services slot in naturally

---

## Quick Win: No Database Changes

**Implement frontend-only filtering using existing `category` field:**

```typescript
const SERVICE_CATEGORIES = {
  bot_moderation: { label: 'Bot Moderation', icon: '🛡️', color: '#E91E63' },
  mtproto_access: { label: 'MTProto Tools', icon: '📡', color: '#2196F3' },
  bot_analytics: { label: 'Analytics', icon: '📊', color: '#673AB7' },
  // Future
  ai_services: { label: 'AI Services', icon: '🤖', color: '#9C27B0' },
};
```

Filter services by `item.category` when user selects subcategory.

---

## Recommendation

**Phase 1 (Quick Win - 30 minutes):**
- Add secondary filter for service categories using existing `category` field
- Show "🛡️ Moderation (6) | 📡 MTProto (3) | 📊 Analytics (1)" under Services

**Phase 2 (Future Enhancement):**
- Add `tags` column to database
- Support multi-tag filtering
- Add tags to service cards as badges

**Start with Phase 1?** ✅
