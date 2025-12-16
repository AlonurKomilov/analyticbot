# 🛒 Marketplace Developer Guide

## Overview

This document provides standardized requirements and patterns for creating marketplace items (Services, Themes, Widgets, Components, Bundles) that integrate fully with the AnalyticBot platform.

---

## 📁 Project Structure

```
marketplace/
├── items/                    # One-time purchase items
│   ├── themes/              # UI themes
│   ├── widgets/             # Dashboard widgets  
│   └── ai-models/           # AI-powered tools
├── services/                 # Subscription services
│   ├── bot/                 # Bot enhancement services
│   ├── mtproto/             # MTProto services
│   └── ai/                  # AI subscription services
└── bundles/                  # Item bundles
```

---

## 🎯 Item Types & Requirements Matrix

| Type | Pricing | Requires Config Page | Requires Backend | Activation Method |
|------|---------|---------------------|------------------|-------------------|
| **Theme** | One-time | ❌ | ❌ | CSS/Theme Provider |
| **Widget** | One-time | ⚠️ Optional | ⚠️ Optional | Dashboard Component |
| **AI Model** | One-time | ✅ Settings | ✅ API Endpoint | Feature Gate |
| **Bot Service** | Subscription | ✅ Full Config | ✅ Bot Handler | Feature Gate + Usage |
| **MTProto Service** | Subscription | ✅ Full Config | ✅ MTProto Handler | Feature Gate + Usage |
| **Bundle** | One-time | ❌ | ❌ | Contains other items |

---

## 📋 Required Files Checklist

### For ALL Marketplace Items:

```
□ Database seed entry (migration or seed file)
□ Unique `service_key` / `unique_key` identifier
□ Marketplace card metadata (name, description, icon, color)
□ Category assignment
□ Pricing configuration
□ Feature list for marketing
```

### For Subscription Services (Bot/MTProto):

```
□ Backend handler/processor
□ Frontend config page component
□ Settings schema (what user can configure)
□ Usage quota definition (if applicable)
□ Feature gate integration
□ Service icon (for dashboard power-ups display)
□ Per-chat/per-channel configuration support
```

### For Themes:

```
□ Theme definition file (colors, typography, components)
□ Preview screenshot
□ Light/Dark mode variants (if applicable)
□ MUI theme overrides
```

### For Widgets:

```
□ Widget React component
□ Widget size/layout definition
□ Data source configuration
□ Dashboard registration
```

---

## 🔑 Service Key Naming Convention

```
{category}_{feature_name}

Examples:
- bot_anti_spam
- bot_welcome_messages
- mtproto_history_access
- ai_content_optimizer
- theme_dark_pro
- widget_analytics_realtime
```

**Rules:**
- All lowercase
- Underscores for word separation
- Category prefix required
- Max 50 characters
- Must be unique across ALL marketplace items

---

## 📊 Database Schema Requirements

### Marketplace Services (Subscription)

```sql
-- Required fields for marketplace_services
INSERT INTO marketplace_services (
    -- Identity
    service_key,           -- UNIQUE identifier (e.g., 'bot_anti_spam')
    name,                  -- Display name
    short_description,     -- Max 100 chars for cards
    description,           -- Full description (markdown supported)
    
    -- Categorization
    category,              -- 'bot_service' | 'mtproto_services' | 'ai_services'
    
    -- Visual
    icon,                  -- Icon name (MUI icon or custom)
    color,                 -- Hex color for theming
    
    -- Pricing
    price_credits_monthly, -- Monthly subscription cost
    price_credits_yearly,  -- Yearly subscription cost (optional discount)
    
    -- Quotas (optional)
    usage_quota_daily,     -- Daily usage limit (null = unlimited)
    usage_quota_monthly,   -- Monthly usage limit
    
    -- Feature List
    features,              -- JSONB array of feature strings
    
    -- Metadata
    is_active,             -- Enable/disable in marketplace
    is_featured,           -- Show in featured section
    is_popular,            -- Show "Popular" badge
    sort_order,            -- Display order
    
    -- Timestamps
    created_at,
    updated_at
);
```

### Marketplace Items (One-Time)

```sql
-- Required fields for marketplace_items
INSERT INTO marketplace_items (
    -- Identity
    unique_key,            -- UNIQUE identifier
    name,
    slug,                  -- URL-friendly name
    description,
    
    -- Categorization
    category,              -- 'themes' | 'widgets' | 'ai_models'
    
    -- Visual
    icon_url,
    preview_images,        -- JSONB array of image URLs
    
    -- Pricing
    price_credits,         -- One-time price
    
    -- Technical
    version,
    download_url,          -- For downloadable items
    
    -- Metadata
    is_active,
    is_featured,
    sort_order
);
```

---

## 🖥️ Frontend Integration Requirements

### 1. Service Config Page Template

Every subscription service MUST have a config page at:
```
apps/frontend/apps/user/src/pages/services/configs/{ServiceName}Config.tsx
```

**Required Structure:**

```typescript
/**
 * {ServiceName} Configuration
 * Service Key: {service_key}
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, Switch, Button, Alert, CircularProgress } from '@mui/material';
import { apiClient } from '@/api/client';

// 1. Define settings interface matching backend schema
interface ServiceSettings {
  enabled: boolean;
  // ... service-specific settings
}

interface Props {
  chatId: number;  // Per-chat configuration
}

export const {ServiceName}Config: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<ServiceSettings>({
    enabled: false,
    // defaults
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // 2. Fetch current settings on mount
  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get(`/bot/moderation/${chatId}/settings`);
        // Map response to local state
      } catch (err) {
        setError('Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettings();
  }, [chatId]);

  // 3. Save handler
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await apiClient.patch(`/bot/moderation/${chatId}/settings`, settings);
      setSuccess(true);
    } catch (err) {
      setError('Failed to save');
    } finally {
      setIsSaving(false);
    }
  };

  // 4. Render config UI
  return (
    <Box>
      {/* Service-specific settings controls */}
      <Button onClick={handleSave}>Save Settings</Button>
    </Box>
  );
};
```

### 2. Register in ServiceConfigPage

Add to `SERVICE_CONFIG_MAP` in `ServiceConfigPage.tsx`:

```typescript
const SERVICE_CONFIG_MAP: Record<string, React.FC<{ chatId: number }>> = {
  // ... existing
  your_service_key: YourServiceConfig,
};
```

### 3. Add Service Icon Mapping

In `ActiveServicesCard.tsx`:

```typescript
const SERVICE_ICON_MAP: Record<string, React.ReactNode> = {
  // ... existing
  your_service_key: <YourIcon fontSize="small" />,
};
```

### 4. Service Details for Config Page

In `ServiceConfigPage.tsx`:

```typescript
const SERVICE_DETAILS: Record<string, { features: string[]; description: string }> = {
  // ... existing
  your_service_key: {
    description: 'Detailed description of what this service does.',
    features: [
      'Feature 1',
      'Feature 2',
      'Feature 3',
    ],
  },
};
```

---

## ⚙️ Backend Integration Requirements

### 1. Bot Service Handler

Location: `apps/bot/handlers/services/`

```python
# apps/bot/handlers/services/{service_name}_handler.py

from core.services.feature_gate_service import FeatureGateService

class YourServiceHandler:
    """
    Handler for {service_name} service
    Service Key: {service_key}
    """
    
    SERVICE_KEY = "your_service_key"
    
    def __init__(self, feature_gate: FeatureGateService):
        self.feature_gate = feature_gate
    
    async def check_access(self, user_id: int) -> bool:
        """Check if user has active subscription"""
        return await self.feature_gate.check_subscription(
            user_id=user_id,
            service_key=self.SERVICE_KEY
        )
    
    async def process(self, event, settings: dict) -> bool:
        """
        Main processing logic
        Returns True if action was taken
        """
        # Check access first
        if not await self.check_access(event.user_id):
            return False
        
        # Check quota if applicable
        can_use = await self.feature_gate.check_and_consume_quota(
            user_id=event.user_id,
            service_key=self.SERVICE_KEY
        )
        if not can_use:
            return False
        
        # Service logic here
        pass
```

### 2. Settings Schema

Add to moderation settings model:

```python
# core/models/moderation_settings.py

class ModerationSettings(Base):
    # ... existing fields
    
    # Your service settings
    your_service_enabled = Column(Boolean, default=False)
    your_service_option1 = Column(String, nullable=True)
    your_service_option2 = Column(Integer, default=10)
```

### 3. API Endpoints

If your service needs custom endpoints beyond standard settings:

```python
# apps/api/routers/your_service_router.py

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/your-service", tags=["Your Service"])

@router.get("/{chat_id}/custom-data")
async def get_custom_data(chat_id: int):
    """Custom endpoint for your service"""
    pass

@router.post("/{chat_id}/custom-action")
async def custom_action(chat_id: int, payload: YourPayload):
    """Custom action for your service"""
    pass
```

Register in `apps/api/main.py`:
```python
app.include_router(your_service_router)
```

---

## 🎨 Theme Development Requirements

### Theme Definition File

```typescript
// themes/your-theme/index.ts

import { createTheme, ThemeOptions } from '@mui/material/styles';

export const yourThemeOptions: ThemeOptions = {
  palette: {
    mode: 'dark', // or 'light'
    primary: {
      main: '#667eea',
      light: '#8b9ff0',
      dark: '#4a5bc4',
    },
    secondary: {
      main: '#764ba2',
    },
    background: {
      default: '#0a0a0f',
      paper: '#12121a',
    },
    // ... full palette
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    // ... typography overrides
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    // ... component overrides
  },
};

export const yourTheme = createTheme(yourThemeOptions);
```

### Theme Metadata

```typescript
export const themeMetadata = {
  id: 'theme_your_theme',
  name: 'Your Theme Name',
  description: 'A beautiful theme with...',
  author: 'Developer Name',
  version: '1.0.0',
  previewImage: '/themes/your-theme/preview.png',
  tags: ['dark', 'modern', 'gradient'],
};
```

---

## 📦 Widget Development Requirements

### Widget Component Template

```typescript
// widgets/your-widget/YourWidget.tsx

import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

export interface YourWidgetProps {
  // Widget configuration
  size: 'small' | 'medium' | 'large';
  refreshInterval?: number;
}

export interface YourWidgetData {
  // Data structure
}

export const YourWidget: React.FC<YourWidgetProps> = ({ size, refreshInterval }) => {
  // Widget implementation
  return (
    <Card>
      <CardContent>
        {/* Widget content */}
      </CardContent>
    </Card>
  );
};

// Widget metadata for dashboard
export const widgetMetadata = {
  id: 'widget_your_widget',
  name: 'Your Widget',
  description: 'Displays...',
  sizes: ['small', 'medium', 'large'],
  defaultSize: 'medium',
  category: 'analytics', // analytics | social | tools
  dataSource: '/api/your-widget/data', // API endpoint
  refreshable: true,
  configurable: true,
};
```

### Widget Registration

```typescript
// widgets/registry.ts

import { YourWidget, widgetMetadata } from './your-widget/YourWidget';

export const widgetRegistry = {
  // ... existing widgets
  [widgetMetadata.id]: {
    component: YourWidget,
    metadata: widgetMetadata,
  },
};
```

---

## ✅ Pre-Launch Checklist

Before submitting a new marketplace item:

### Database
- [ ] Seed data created with all required fields
- [ ] Unique key is globally unique
- [ ] Category is valid
- [ ] Pricing is set correctly
- [ ] Features array is populated

### Backend (for Services)
- [ ] Handler class created
- [ ] Feature gate integration tested
- [ ] Settings schema updated
- [ ] API endpoints created (if needed)
- [ ] Unit tests written

### Frontend
- [ ] Config page component created
- [ ] Icon mapping added
- [ ] Service details added
- [ ] Config exported in index.ts
- [ ] Responsive design tested

### Testing
- [ ] Purchase flow tested
- [ ] Activation verified
- [ ] Settings save/load works
- [ ] Per-chat configuration works
- [ ] Expiration handling works
- [ ] Usage quota tracking (if applicable)

### Documentation
- [ ] User-facing description written
- [ ] Feature list accurate
- [ ] Screenshots/preview images

---

## 🔄 Integration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     MARKETPLACE ITEM LIFECYCLE                   │
└─────────────────────────────────────────────────────────────────┘

1. DISCOVERY
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │  Marketplace │ ──► │ Item Details │ ──► │   Purchase   │
   │     Page     │     │    Modal     │     │   Dialog     │
   └──────────────┘     └──────────────┘     └──────────────┘

2. PURCHASE
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │   Credits    │ ──► │   Backend    │ ──► │ Subscription │
   │   Deducted   │     │  Processing  │     │   Created    │
   └──────────────┘     └──────────────┘     └──────────────┘

3. ACTIVATION (Services)
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │   Dashboard  │ ──► │   Config     │ ──► │   Service    │
   │  Power-Ups   │     │    Page      │     │   Active!    │
   └──────────────┘     └──────────────┘     └──────────────┘

4. USAGE
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │    User      │ ──► │ Feature Gate │ ──► │   Handler    │
   │   Action     │     │    Check     │     │  Executes    │
   └──────────────┘     └──────────────┘     └──────────────┘

5. RENEWAL/EXPIRY
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │   Auto or    │ ──► │   Credits    │ ──► │  Renewed or  │
   │   Manual     │     │   Check      │     │   Expired    │
   └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 📞 Support

For questions about marketplace development:
- Review existing service implementations as examples
- Check `apps/frontend/apps/user/src/pages/services/configs/` for config page patterns
- Check `core/services/` for backend service patterns

---

*Last Updated: December 2025*
