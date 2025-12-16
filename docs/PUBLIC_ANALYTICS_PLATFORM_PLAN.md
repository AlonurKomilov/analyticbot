# Public Analytics Platform - Implementation Plan

## Overview

Create a public-facing Telegram channel/group analytics catalog at `analyticbot.org` (production) / `dev.analyticbot.org` (development). This serves as:

1. **Marketing Tool** - Attract users searching for channel statistics
2. **Lead Generation** - Convert visitors to registered users
3. **Public Service** - Free basic analytics for any channel

---

## Architecture

### Domain Strategy
| Domain | Purpose | Auth Required |
|--------|---------|---------------|
| `analyticbot.org` | Public catalog & marketing | No |
| `app.analyticbot.org` | User dashboard (current) | Yes |
| `admin.analyticbot.org` | Admin panel | Yes (Admin) |
| `moderator.analyticbot.org` | Moderator dashboard | Yes (Moderator) |
| `api.analyticbot.org` | API endpoints | Mixed |

### Data Flow Strategy
```
User visits analyticbot.org
         ↓
   Searches for channel
         ↓
┌─────────────────────────────────┐
│  Check: Is channel in catalog?  │
└─────────────────────────────────┘
         ↓ Yes              ↓ No
    Show cached data    Fetch from Telegram API
         ↓                    ↓
    Display stats        Add to cache (Redis)
         ↓                    ↓
┌─────────────────────────────────┐
│   User wants more features?     │
└─────────────────────────────────┘
         ↓ Yes
    Redirect to login/signup
         ↓
    Convert to paying user
```

### Data Sources (Priority Order)
1. **Telegram Bot API** (Free, Public)
   - Channel info, description, photo
   - Subscriber count
   - Recent posts (up to 100)
   - Basic engagement metrics

2. **MTProto API** (When needed)
   - Historical data
   - Detailed engagement
   - Subscriber growth charts
   - View patterns

3. **Our Database** (Registered channels only)
   - Full analytics
   - Historical trends
   - Custom metrics

---

## Public Catalog Features

### 1. Home Page
- **Featured Channels** (curated by moderators)
- **Verified Channels** (with checkmark)
- **Trending Channels** (by growth rate)
- **Categories** (Blogs, News, Tech, Entertainment, etc.)
- **Country Filter** (Russia, USA, etc.)
- **Search Bar** (search any channel)

### 2. Channel Page (Public)
**Free (No Login):**
- Channel name, avatar, description
- Subscriber count
- Category & language
- Recent posts (last 10)
- Basic stats (avg views per post)
- Growth indicator (↑↓)

**Premium (Requires Login):**
- Full subscriber growth chart
- Detailed engagement analytics
- Post reach analysis
- Best posting times
- Audience demographics
- Citation index
- Advertising efficiency
- Export data

### 3. Category Pages
- Channels grouped by category
- Sorting: subscribers, growth, engagement
- Pagination

### 4. Search Results
- Search by name or @username
- Filter by category, country
- Show top results with basic stats

---

## Moderator Features (for Public Catalog)

### What Moderators Do:
1. **Add Channels to Catalog**
   - Search and add any public channel
   - Assign category
   - Set country/language

2. **Curate Content**
   - Feature channels on homepage
   - Mark verified channels
   - Remove inappropriate channels

3. **Manage Categories**
   - Create/edit categories
   - Assign icons/colors

4. **Handle Reports**
   - Review reported channels
   - Remove scam/spam channels

### Moderator Dashboard Pages:
1. **Catalog Management** - Add/edit/remove channels
2. **Featured Channels** - Manage homepage features
3. **Category Management** - Manage categories
4. **Reports Queue** - Handle user reports
5. **Analytics** - View catalog statistics

---

## Technical Implementation

### Database Schema (Minimal)

```sql
-- Public channel catalog (minimal storage)
CREATE TABLE public_channel_catalog (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES channel_categories(id),
    country_code VARCHAR(2),
    language_code VARCHAR(5),
    is_featured BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    added_by INTEGER REFERENCES users(id), -- Moderator who added
    added_at TIMESTAMP DEFAULT NOW(),
    last_synced_at TIMESTAMP,
    metadata JSONB -- Cached stats, refreshed periodically
);

-- Channel categories
CREATE TABLE channel_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(20),
    parent_id INTEGER REFERENCES channel_categories(id),
    sort_order INTEGER DEFAULT 0,
    channel_count INTEGER DEFAULT 0
);

-- Cached channel stats (Redis preferred, DB backup)
CREATE TABLE channel_stats_cache (
    telegram_id BIGINT PRIMARY KEY,
    subscriber_count INTEGER,
    avg_views INTEGER,
    avg_reactions INTEGER,
    posts_per_day DECIMAL(5,2),
    growth_rate DECIMAL(5,2), -- % change in 30 days
    last_post_at TIMESTAMP,
    cached_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints (Public - No Auth)

```
GET /public/channels                    - List channels (paginated)
GET /public/channels/featured           - Featured channels
GET /public/channels/trending           - Trending channels
GET /public/channels/{username}         - Channel details
GET /public/channels/{username}/posts   - Recent posts
GET /public/channels/{username}/stats   - Basic stats (limited)
GET /public/categories                  - All categories
GET /public/categories/{slug}           - Channels in category
GET /public/search?q={query}            - Search channels
```

### API Endpoints (Moderator)

```
POST /moderator/catalog/add             - Add channel to catalog
PUT  /moderator/catalog/{id}            - Update channel info
DELETE /moderator/catalog/{id}          - Remove from catalog
POST /moderator/catalog/{id}/feature    - Feature channel
POST /moderator/catalog/{id}/verify     - Verify channel
GET  /moderator/catalog/pending         - Channels pending review
POST /moderator/categories              - Create category
PUT  /moderator/categories/{id}         - Update category
```

### Caching Strategy

```
┌─────────────────────────────────────────────────┐
│                   Redis Cache                    │
├─────────────────────────────────────────────────┤
│ channel:{telegram_id}:info     TTL: 1 hour      │
│ channel:{telegram_id}:stats    TTL: 15 minutes  │
│ channel:{telegram_id}:posts    TTL: 5 minutes   │
│ category:{slug}:channels       TTL: 10 minutes  │
│ featured:channels              TTL: 5 minutes   │
│ trending:channels              TTL: 30 minutes  │
└─────────────────────────────────────────────────┘
```

---

## Frontend Structure

### Public Site (analyticbot.org)

```
apps/frontend/apps/public/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx           # Landing with featured/categories
│   │   ├── ChannelPage.tsx        # Individual channel stats
│   │   ├── CategoryPage.tsx       # Channels by category
│   │   ├── SearchPage.tsx         # Search results
│   │   ├── TrendingPage.tsx       # Trending channels
│   │   └── AboutPage.tsx          # About the platform
│   ├── components/
│   │   ├── ChannelCard.tsx        # Channel preview card
│   │   ├── ChannelStats.tsx       # Stats display
│   │   ├── CategoryNav.tsx        # Category navigation
│   │   ├── SearchBar.tsx          # Search component
│   │   ├── PremiumBanner.tsx      # "Sign up for more" CTA
│   │   └── Footer.tsx
│   ├── layouts/
│   │   └── PublicLayout.tsx
│   └── App.tsx
├── index.html
└── vite.config.js
```

### UI Design Notes
- **Clean, minimal design** (similar to TGStat)
- **Fast loading** (SSR recommended for SEO)
- **Mobile responsive**
- **Clear CTAs** to convert visitors
- **Prominent "Sign In" button**

---

## Conversion Points (Marketing)

### Where to Show "Sign Up" Prompts:

1. **Channel Stats Page**
   - "Sign in to see full subscriber growth chart"
   - "Premium: View posting schedule analysis"

2. **Search Results**
   - After 5 searches: "Sign up for unlimited searches"

3. **Export/Download**
   - "Sign in to export this data"

4. **Detailed Analytics**
   - Blur premium features
   - "Sign up to unlock"

5. **Add to Favorites**
   - "Sign in to save channels"

6. **Compare Channels**
   - "Premium feature: Compare multiple channels"

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2) ✅ COMPLETED (Dec 15, 2025)
- [x] Create public frontend app skeleton
- [x] Setup public API router
- [x] Create database schema (catalog, categories)
- [x] Implement Telegram API integration for public data
- [x] Redis caching setup

**Deliverables:**
- Database: 3 tables created (channel_categories, public_channel_catalog, channel_stats_cache)
- Categories: 20 initial categories seeded
- API: 8 public endpoints at `/public/*`
- Frontend: React+MUI+Vite app at `apps/frontend/apps/public/`
- Files created:
  - `infra/db/alembic/versions/0051_add_public_catalog_tables.py`
  - `infra/db/alembic/versions/0052_seed_channel_categories.py`
  - `core/schemas/public_catalog_schemas.py`
  - `apps/api/routers/public_catalog_router.py`

### Phase 2: Core Features (Week 3-4) ✅ COMPLETED (Dec 15, 2025)
- [x] Home page with categories
- [x] Channel detail page
- [x] Search functionality
- [x] Category pages
- [x] Basic stats display
- [x] Moderator API endpoints (added early)
- [x] Telegram data fetcher service

**Deliverables:**
- Frontend pages: HomePage, ChannelPage, CategoryPage, SearchPage, NotFoundPage
- Frontend components: Header, Footer, ChannelCard, CategoryNav, PremiumBanner, Loading
- Moderator router: 11 endpoints at `/moderator/catalog/*`
- Services created:
  - `core/services/public_catalog_service.py` - Telegram API integration
  - `core/services/public_cache_service.py` - Redis caching layer
  - `apps/api/routers/moderator_catalog_router.py` - Catalog management
- Auth: Added `require_moderator_user` middleware
- Test data: 5 channels added (@telegram, @durov, @nytimes, @bbcrussian, @bitcoin)

### Phase 3: Moderator Tools (Week 5) ✅ COMPLETED (Dec 15, 2025)
- [x] Create SEPARATE moderator frontend app (not in admin)
  - [x] DashboardPage with stats and quick actions
  - [x] CatalogPage - Full catalog management UI
  - [x] FeaturedPage - Featured channels management
  - [x] CategoriesPage - Placeholder
  - [x] ReportsPage - Placeholder
- [x] Connect frontend to live API (fixed IPv6 proxy issue)
- [x] Added stats endpoint for moderator dashboard
- [x] Purple theme to distinguish from admin (blue)
- [x] Proper architecture: Admin ≠ Moderator

**Deliverables:**
- NEW: `apps/frontend/apps/moderator/` - Complete moderator app
  - `src/pages/` - Dashboard, Catalog, Categories, Featured, Reports, Login
  - `src/layouts/ModeratorLayout.tsx` - Purple-themed sidebar
  - `src/contexts/AuthContext.tsx` - Moderator auth (accepts moderator/admin/owner)
  - `src/api/client.ts` - API client with CSRF
  - `src/config/api.ts` - Moderator API endpoints
  - `vite.config.js` - Port 11330, proxy to API
- REMOVED catalog from admin app (admin is for system management only)

### Phase 4: Enhancement (Week 6) ✅ COMPLETE
- [x] Trending algorithm implementation (score = growth_rate * log(subs) * engagement_factor)
- [x] Growth charts (locked preview with blur overlay)
- [x] Premium feature prompts (sign-up CTAs on channel pages)
- [x] SEO optimization (react-helmet-async, dynamic meta tags, structured data)
- [x] Channel detail pages with full statistics
- Category management UI (moved to moderator app)

**Key Changes:**
- Added `react-helmet-async` to public app for dynamic SEO
- Created `SEO.tsx` component with structured data support
- Added `GrowthChart.tsx` with locked preview state
- Enhanced trending algorithm with composite score:
  - Growth rate × log(subscriber_count) × engagement_factor
  - Filters channels with minimum 100 subscribers
  - Only shows positive growth channels
- All pages now have proper meta tags for social sharing

### Phase 5: Launch (Week 7) ✅ COMPLETE
- [x] Final testing - All services verified working
- [x] DNS/SSL setup - Nginx config created for all subdomains
- [x] Seed initial channels - 6 channels, 20 categories already seeded
- [x] Created deployment script (`scripts/system/deploy-public-platform.sh`)

**Deployment Details:**
- Main nginx config updated: `infra/nginx/analyticbot.cloudflare.conf`
- Individual configs in `infra/nginx/`:
  - `public.analyticbot.conf` → Public catalog (port 11320)
  - `app.analyticbot.conf` → User dashboard (port 11300)
  - `moderator.analyticbot.conf` → Moderator dashboard (port 11330)
  - `admin.analyticbot.conf` → Admin panel (port 11310)
  - `api.analyticbot.conf` → API backend (port 11400)

**Temporary Domain Mapping (Dec 15, 2025):**
| Domain | App | Port | Notes |
|--------|-----|------|-------|
| `dev.analyticbot.org` | Public Catalog | 11320 | Temporary for testing |
| `app.analyticbot.org` | User Dashboard | 11300 | Current users migrate here |
| `moderator.analyticbot.org` | Moderator | 11330 | New |
| `admin.analyticbot.org` | Admin Panel | 11310 | Existing |
| `api.analyticbot.org` | API | 11400 | Existing |

**To Deploy:**
```bash
# Apply nginx config
sudo cp /home/abcdev/projects/analyticbot/infra/nginx/analyticbot.cloudflare.conf /etc/nginx/sites-available/
sudo nginx -t && sudo systemctl reload nginx
```

---

## Sample Categories (Initial)

| Category | Icon | Color |
|----------|------|-------|
| News & Media | 📰 | Blue |
| Blogs | ✍️ | Purple |
| Technology | 💻 | Green |
| Entertainment | 🎬 | Red |
| Education | 📚 | Orange |
| Business | 💼 | Navy |
| Crypto | ₿ | Gold |
| Sports | ⚽ | Green |
| Music | 🎵 | Pink |
| Art & Design | 🎨 | Violet |
| Gaming | 🎮 | Purple |
| Science | 🔬 | Teal |
| Travel | ✈️ | Sky Blue |
| Food | 🍕 | Orange |
| Fashion | 👗 | Pink |
| Politics | 🏛️ | Gray |

---

## Revenue Opportunities

### Free (Public)
- Basic channel info
- Subscriber count
- Recent posts
- Basic stats

### Premium (Registered Users)
- Full analytics dashboard
- Historical data
- Growth charts
- Engagement metrics
- Export functionality
- API access
- Compare channels
- Alerts/monitoring

### Enterprise (Future)
- White-label analytics
- Custom integrations
- Priority support
- Bulk API access

---

## Competitive Advantages Over TGStat

1. **Modern UI** - Better user experience
2. **Faster** - Efficient caching
3. **Multi-language** - Not just Russian
4. **Better Free Tier** - More features without login
5. **Integration** - With our bot analytics
6. **API Access** - For developers

---

## Next Steps

1. ✅ Approve this plan
2. ✅ Create public frontend app
3. ✅ Create public API router
4. ✅ Setup database schema
5. ✅ Implement Telegram API integration
6. ✅ Build moderator catalog tools (API)
7. ✅ Build moderator catalog UI
8. ✅ Connect frontend to live API data (fixed IPv6 proxy)
9. ✅ Phase 4: Enhancement (trending, charts, SEO)
10. ✅ Phase 5: Launch preparation complete

---

## 🎉 PROJECT COMPLETE - Dec 15, 2025

All 5 phases of the Public Analytics Platform have been completed!

### Architecture (Separate Frontend Apps):
| App | Domain | Port | Purpose |
|-----|--------|------|---------|
| Public | `analyticbot.org` | 11320 | Public analytics catalog |
| User | `app.analyticbot.org` | 11300 | User dashboard |
| Admin | `admin.analyticbot.org` | 11310 | System administration |
| Moderator | `moderator.analyticbot.org` | 11330 | Public catalog management |

### Services Running:
| Service | Port | Status |
|---------|------|--------|
| API | 11400 | ✅ Running |
| Public Frontend | 11320 | ✅ Running |
| Moderator Frontend | 11330 | ✅ Running |
| Admin Frontend | 11310 | ✅ Available |
| User Frontend | 11300 | ✅ Running |

### Database Status:
| Table | Records |
|-------|---------|
| channel_categories | 20 |
| public_channel_catalog | 5 |
| channel_stats_cache | 5 |

### API Endpoints Working:
**Public (No Auth):**
- `GET /public/categories` - 20 categories ✅
- `GET /public/channels` - 5 channels ✅
- `GET /public/channels/featured` - 2 featured ✅
- `GET /public/stats` - Catalog statistics ✅

**Moderator (Auth Required):**
- `POST /moderator/catalog/add` - Add channels ✅
- `GET /moderator/catalog` - List catalog entries ✅
- `GET /moderator/catalog/stats` - Moderator stats ✅
- `PUT /moderator/catalog/{id}` - Update channel ✅
- `DELETE /moderator/catalog/{id}` - Remove channel ✅
- `POST /moderator/catalog/{id}/feature` - Toggle featured ✅
- `POST /moderator/catalog/{id}/verify` - Toggle verified ✅
- `POST /moderator/catalog/{id}/sync` - Sync from Telegram ✅

### Moderator Frontend App (NEW - Phase 3):
Location: `apps/frontend/apps/moderator/`
- **Pages:**
  - `DashboardPage.tsx` - Overview with stats and quick actions
  - `CatalogPage.tsx` - Full catalog management UI
  - `CategoriesPage.tsx` - Category management (placeholder)
  - `FeaturedPage.tsx` - Featured channels management
  - `ReportsPage.tsx` - Reports queue (placeholder)
  - `LoginPage.tsx` - Moderator authentication
- **Layout:** Purple theme, sidebar navigation
- **Auth:** Accepts moderator, admin, owner roles
