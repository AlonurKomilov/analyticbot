# Public Analytics Platform - Phase 1 Implementation Plan

## Current State Assessment

### ✅ What Exists
| Component | Status | Details |
|-----------|--------|---------|
| **Frontend Apps** | 2 apps | `admin/`, `user/` in `apps/frontend/apps/` |
| **API Structure** | 50+ routers | `apps/api/routers/` |
| **Database** | PostgreSQL 16 | 66 tables, Docker on port 10100 |
| **Redis** | Running | Docker on port 10200 |
| **Telegram Bot API** | ✅ | `infra/telegram/telegram_service_impl.py` (aiogram) |
| **MTProto API** | ✅ | `apps/mtproto/` with Pyrogram/Telethon support |
| **Cache Adapter** | ✅ | `infra/cache/redis_cache_adapter.py` |
| **Channels Table** | ✅ | 14 columns (id, user_id, title, username, subscriber_count, etc.) |

### ❌ What Needs to Be Created
| Component | Location | Priority |
|-----------|----------|----------|
| Public Frontend App | `apps/frontend/apps/public/` | High |
| Public API Router | `apps/api/routers/public_catalog_router.py` | High |
| Channel Categories Table | Database migration | High |
| Public Channel Catalog Table | Database migration | High |
| Channel Stats Cache Table | Database (backup for Redis) | Medium |
| Public Data Service | `core/services/public_catalog_service.py` | High |

---

## Phase 1 Tasks (Week 1-2)

### Day 1-2: Database Schema

#### Task 1.1: Create Alembic Migration
**File:** `alembic/versions/xxxx_add_public_catalog_tables.py`

```sql
-- Channel Categories
CREATE TABLE channel_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(20),
    parent_id INTEGER REFERENCES channel_categories(id),
    sort_order INTEGER DEFAULT 0,
    channel_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Public Channel Catalog
CREATE TABLE public_channel_catalog (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    avatar_url VARCHAR(500),
    category_id INTEGER REFERENCES channel_categories(id),
    country_code VARCHAR(2),
    language_code VARCHAR(5),
    is_featured BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    added_by INTEGER REFERENCES users(id),
    added_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Channel Stats Cache (Backup for Redis)
CREATE TABLE channel_stats_cache (
    telegram_id BIGINT PRIMARY KEY,
    subscriber_count INTEGER,
    avg_views INTEGER,
    avg_reactions INTEGER,
    posts_per_day DECIMAL(5,2),
    growth_rate DECIMAL(5,2),
    last_post_at TIMESTAMP,
    cached_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_catalog_category ON public_channel_catalog(category_id);
CREATE INDEX idx_catalog_featured ON public_channel_catalog(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_catalog_username ON public_channel_catalog(username);
CREATE INDEX idx_categories_slug ON channel_categories(slug);
```

#### Task 1.2: Seed Initial Categories
Insert categories from the plan (News, Tech, Blogs, Entertainment, etc.)

---

### Day 2-3: API Layer

#### Task 2.1: Create Public API Router
**File:** `apps/api/routers/public_catalog_router.py`

**Endpoints (No Auth Required):**
```
GET /public/categories              - List all categories
GET /public/channels                - List channels (paginated)
GET /public/channels/featured       - Featured channels
GET /public/channels/trending       - Trending by growth rate
GET /public/channels/{username}     - Channel details + basic stats
GET /public/channels/{username}/posts - Recent posts (limit 10)
GET /public/search                  - Search by name/username
```

**Response Models:**
- `PublicCategoryResponse`
- `PublicChannelListResponse`
- `PublicChannelDetailResponse`
- `PublicPostsResponse`

#### Task 2.2: Create Pydantic Schemas
**File:** `core/schemas/public_catalog_schemas.py`

```python
class PublicCategory(BaseModel):
    id: int
    name: str
    slug: str
    icon: str | None
    color: str | None
    channel_count: int

class PublicChannelBasic(BaseModel):
    telegram_id: int
    username: str | None
    title: str
    avatar_url: str | None
    category: PublicCategory | None
    subscriber_count: int | None
    is_verified: bool

class PublicChannelDetail(PublicChannelBasic):
    description: str | None
    avg_views: int | None
    growth_rate: float | None
    last_post_at: datetime | None
```

---

### Day 3-4: Service Layer

#### Task 3.1: Create Public Catalog Service
**File:** `core/services/public_catalog_service.py`

**Responsibilities:**
1. Fetch channel data from Telegram API
2. Cache to Redis (with TTL)
3. Fallback to database cache
4. Aggregate stats from multiple sources

**Methods:**
```python
class PublicCatalogService:
    async def get_categories() -> list[PublicCategory]
    async def get_channels(category_id, page, per_page) -> PaginatedChannels
    async def get_featured_channels(limit) -> list[PublicChannel]
    async def get_trending_channels(limit) -> list[PublicChannel]
    async def get_channel_by_username(username) -> PublicChannelDetail | None
    async def get_channel_posts(username, limit) -> list[PublicPost]
    async def search_channels(query, limit) -> list[PublicChannel]
    async def sync_channel_from_telegram(telegram_id) -> bool
```

#### Task 3.2: Create Telegram Public Data Fetcher
**File:** `core/services/telegram_public_fetcher.py`

**Uses existing `AiogramTelegramService` to:**
- Get channel info (title, description, avatar)
- Get member count
- Get recent messages (via MTProto if needed)

---

### Day 4-5: Redis Caching

#### Task 4.1: Create Public Cache Service
**File:** `core/services/public_cache_service.py`

**Cache Keys & TTLs:**
```python
CACHE_KEYS = {
    "channel_info": "public:channel:{telegram_id}:info",      # TTL: 1 hour
    "channel_stats": "public:channel:{telegram_id}:stats",    # TTL: 15 min
    "channel_posts": "public:channel:{telegram_id}:posts",    # TTL: 5 min
    "categories": "public:categories",                        # TTL: 30 min
    "featured": "public:featured",                            # TTL: 5 min
    "trending": "public:trending",                            # TTL: 30 min
}

class PublicCacheService:
    async def get_channel_info(telegram_id) -> dict | None
    async def set_channel_info(telegram_id, data)
    async def get_channel_stats(telegram_id) -> dict | None
    async def set_channel_stats(telegram_id, data)
    async def invalidate_channel(telegram_id)
```

---

### Day 5-7: Frontend App

#### Task 5.1: Create Public Frontend Skeleton
**Directory:** `apps/frontend/apps/public/`

```
apps/frontend/apps/public/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx           # Landing + featured + categories
│   │   ├── ChannelPage.tsx        # Single channel stats
│   │   ├── CategoryPage.tsx       # Channels in category
│   │   ├── SearchPage.tsx         # Search results
│   │   └── NotFoundPage.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx         # Nav + search bar + login button
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   ├── channel/
│   │   │   ├── ChannelCard.tsx    # Card for listing
│   │   │   ├── ChannelStats.tsx   # Stats display
│   │   │   └── RecentPosts.tsx
│   │   ├── category/
│   │   │   └── CategoryNav.tsx
│   │   ├── search/
│   │   │   └── SearchBar.tsx
│   │   └── common/
│   │       ├── PremiumBanner.tsx  # "Sign up for more" CTA
│   │       └── Loading.tsx
│   ├── services/
│   │   └── publicApi.ts           # API client
│   ├── types/
│   │   └── public.ts              # TypeScript types
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.js
```

#### Task 5.2: Configure Vite for Public App
- Port: 11320 (new port for public app)
- API proxy to localhost:11400

#### Task 5.3: Basic Pages Implementation
1. **HomePage** - Category grid + featured channels
2. **ChannelPage** - Channel info + basic stats + "login for more"
3. **CategoryPage** - Paginated channel list

---

## Implementation Order

| Step | Task | Estimated Time |
|------|------|----------------|
| 1 | Database migration (categories + catalog + cache) | 2 hours |
| 2 | Seed initial categories | 30 min |
| 3 | Create Pydantic schemas | 1 hour |
| 4 | Create public API router (basic endpoints) | 3 hours |
| 5 | Create public catalog service | 4 hours |
| 6 | Create Redis cache service | 2 hours |
| 7 | Create frontend app skeleton | 2 hours |
| 8 | Implement HomePage | 3 hours |
| 9 | Implement ChannelPage | 3 hours |
| 10 | Implement CategoryPage + SearchPage | 4 hours |
| 11 | Test & integrate | 3 hours |

**Total Estimated: ~28 hours (4-5 working days)**

---

## Files to Create (Phase 1)

### Backend
1. `alembic/versions/xxx_add_public_catalog_tables.py` - Migration
2. `core/schemas/public_catalog_schemas.py` - Pydantic models
3. `apps/api/routers/public_catalog_router.py` - API endpoints
4. `core/services/public_catalog_service.py` - Business logic
5. `core/services/public_cache_service.py` - Redis caching
6. `core/services/telegram_public_fetcher.py` - Telegram data fetch

### Frontend
7. `apps/frontend/apps/public/package.json`
8. `apps/frontend/apps/public/vite.config.js`
9. `apps/frontend/apps/public/index.html`
10. `apps/frontend/apps/public/src/main.tsx`
11. `apps/frontend/apps/public/src/App.tsx`
12. `apps/frontend/apps/public/src/pages/*.tsx` (5 pages)
13. `apps/frontend/apps/public/src/components/**/*.tsx` (10+ components)
14. `apps/frontend/apps/public/src/services/publicApi.ts`
15. `apps/frontend/apps/public/src/types/public.ts`

---

## Configuration Changes

### 1. API Router Registration
Add to `apps/api/main.py`:
```python
from apps.api.routers.public_catalog_router import router as public_router
app.include_router(public_router, prefix="/public", tags=["Public Catalog"])
```

### 2. Nginx Configuration
Add server block for `analyticbot.org` → public frontend (port 11320)

### 3. Environment Variables
```env
PUBLIC_FRONTEND_PORT=11320
PUBLIC_CACHE_TTL_CHANNEL_INFO=3600
PUBLIC_CACHE_TTL_CHANNEL_STATS=900
PUBLIC_CACHE_TTL_CHANNEL_POSTS=300
```

---

## Ready to Start?

Let me know and I'll begin implementing:
1. ⬜ Database migration
2. ⬜ API router & schemas
3. ⬜ Services (catalog + cache)
4. ⬜ Frontend app skeleton
5. ⬜ Basic pages (Home, Channel, Category)
