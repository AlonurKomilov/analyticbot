# 🔍 Backend Service and API Endpoint Usage Audit Report
============================================================

## 📊 Executive Summary
- **Total API Endpoints Discovered:** 58
- **Frontend API Calls Found:** 35
- **Unused API Endpoints:** 49

## 📋 Part 1: All Discovered Backend API Endpoints

### analytics_advanced.py
- `GET /dashboard/{channel_id}` (line 221)
- `GET /metrics/real-time/{channel_id}` (line 294)
- `GET /alerts/check/{channel_id}` (line 320)
- `GET /recommendations/{channel_id}` (line 346)
- `GET /performance/score/{channel_id}` (line 375)

### analytics_router.py
- `GET /health` (line 266)
- `GET /status` (line 278)
- `GET /channels` (line 300)
- `POST /channels` (line 327)
- `GET /channels/{channel_id}` (line 369)
- `GET /metrics` (line 398)
- `GET /channels/{channel_id}/metrics` (line 453)
- `GET /demo/post-dynamics` (line 514)
- `GET /demo/top-posts` (line 526)
- `GET /demo/best-times` (line 538)
- `GET /demo/ai-recommendations` (line 550)
- `POST /data-processing/analyze` (line 562)
- `POST /predictions/forecast` (line 589)
- `GET /insights/{channel_id}` (line 610)
- `GET /dashboard/{channel_id}` (line 644)
- `POST /refresh/{channel_id}` (line 664)
- `GET /summary/{channel_id}` (line 725)

### analytics_unified.py
- `GET /health` (line 63)
- `GET /dashboard/{channel_id}` (line 136)
- `GET /live-metrics/{channel_id}` (line 231)
- `GET /reports/{channel_id}` (line 271)
- `GET /comparison/{channel_id}` (line 334)

### analytics_v2.py
- `GET /health` (line 45)
- `GET /channels/{channel_id}/overview` (line 51)
- `GET /channels/{channel_id}/growth` (line 118)
- `GET /channels/{channel_id}/reach` (line 164)
- `GET /channels/{channel_id}/top-posts` (line 204)
- `GET /channels/{channel_id}/sources` (line 249)
- `GET /channels/{channel_id}/trending` (line 299)

### exports_v2.py
- `GET /csv/overview/{channel_id}` (line 66)
- `GET /csv/growth/{channel_id}` (line 103)
- `GET /csv/reach/{channel_id}` (line 138)
- `GET /csv/sources/{channel_id}` (line 173)
- `GET /png/growth/{channel_id}` (line 211)
- `GET /png/reach/{channel_id}` (line 248)
- `GET /png/sources/{channel_id}` (line 285)
- `GET /status` (line 325)

### mobile_api.py
- `GET /dashboard/{user_id}` (line 97)
- `POST /analytics/quick` (line 153)
- `GET /metrics/summary/{channel_id}` (line 198)
- `GET /health` (line 238)

### share_v2.py
- `POST /create/{report_type}/{channel_id}` (line 90)
- `GET /report/{share_token}` (line 166)
- `GET /info/{share_token}` (line 286)
- `DELETE /revoke/{share_token}` (line 319)
- `GET /cleanup` (line 343)

### content_protection_routes.py
- `POST /watermark/image` (line 31)
- `POST /watermark/video` (line 115)
- `POST /custom-emoji` (line 193)
- `POST /theft-detection` (line 237)
- `GET /files/{filename}` (line 266)
- `GET /premium-features/{tier}` (line 280)
- `GET /usage/{user_id}` (line 302)

## 🖥️ Part 2: Frontend API Calls

- `${this.baseURL}/api/v1/media/upload-direct`
- `/api/mobile/v1/analytics/quick`
- `/api/v1/content-protection/detection/scan`
- `/api/v1/media/storage-files?limit=${limit}&offset=${offset}`
- `/api/v1/media/upload-direct`
- `/api/v1/superadmin/audit-logs?limit=50`
- `/api/v1/superadmin/stats`
- `/api/v1/superadmin/users/${suspendDialog.user.id}/suspend`
- `/api/v1/superadmin/users/${userId}/reactivate`
- `/api/v1/superadmin/users?limit=100`
- `/api/v2/analytics/advanced/alerts/check/${channelId}`
- `/api/v2/analytics/advanced/dashboard/${channelId}?${params}`
- `/api/v2/analytics/advanced/metrics/real-time/${channelId}`
- `/api/v2/analytics/advanced/performance/score/${channelId}?period=${period}`
- `/api/v2/analytics/advanced/recommendations/${channelId}`
- `/api/v2/analytics/channel-data`
- `/api/v2/analytics/channels/${channelId}/growth?period=${period}`
- `/api/v2/analytics/channels/${channelId}/growth?period=30`
- `/api/v2/analytics/channels/${channelId}/overview`
- `/api/v2/analytics/channels/${channelId}/overview?period=${period}`
- `/api/v2/analytics/channels/${channelId}/overview?period=30`
- `/api/v2/analytics/channels/${channelId}/reach?period=${period}`
- `/api/v2/analytics/channels/${channelId}/reach?period=30`
- `/api/v2/analytics/channels/${channelId}/top-posts?period=${period}`
- `/api/v2/analytics/channels/${channelId}/trending?period=${period}`
- `/api/v2/analytics/channels/${channelId}/trending?period=7`
- `/api/v2/analytics/metrics/performance`
- `/api/v2/analytics/trends/top-posts`
- `/api/v2/exports/csv/${type}/${channelId}?period=${period}`
- `/api/v2/exports/png/${type}/${channelId}?period=${period}`
- `/api/v2/exports/status`
- `/api/v2/share/create/${type}/${channelId}`
- `/api/v2/share/info/${token}`
- `/api/v2/share/report/${token}`
- `/api/v2/share/revoke/${token}`

## ❌ Part 3: Unused API Endpoints

**⚠️ The following endpoints are not called by the frontend:**

### analytics_advanced.py
- `GET /dashboard/{channel_id}` (line 221)
- `GET /metrics/real-time/{channel_id}` (line 294)
- `GET /alerts/check/{channel_id}` (line 320)
- `GET /recommendations/{channel_id}` (line 346)
- `GET /performance/score/{channel_id}` (line 375)

### analytics_router.py
- `GET /health` (line 266)
- `GET /channels` (line 300)
- `POST /channels` (line 327)
- `GET /channels/{channel_id}` (line 369)
- `GET /metrics` (line 398)
- `GET /channels/{channel_id}/metrics` (line 453)
- `GET /demo/post-dynamics` (line 514)
- `GET /demo/best-times` (line 538)
- `GET /demo/ai-recommendations` (line 550)
- `POST /data-processing/analyze` (line 562)
- `POST /predictions/forecast` (line 589)
- `GET /insights/{channel_id}` (line 610)
- `GET /dashboard/{channel_id}` (line 644)
- `POST /refresh/{channel_id}` (line 664)
- `GET /summary/{channel_id}` (line 725)

### analytics_unified.py
- `GET /health` (line 63)
- `GET /dashboard/{channel_id}` (line 136)
- `GET /live-metrics/{channel_id}` (line 231)
- `GET /reports/{channel_id}` (line 271)
- `GET /comparison/{channel_id}` (line 334)

### analytics_v2.py
- `GET /health` (line 45)
- `GET /channels/{channel_id}/sources` (line 249)

### exports_v2.py
- `GET /csv/overview/{channel_id}` (line 66)
- `GET /csv/growth/{channel_id}` (line 103)
- `GET /csv/reach/{channel_id}` (line 138)
- `GET /csv/sources/{channel_id}` (line 173)
- `GET /png/growth/{channel_id}` (line 211)
- `GET /png/reach/{channel_id}` (line 248)
- `GET /png/sources/{channel_id}` (line 285)

### mobile_api.py
- `GET /dashboard/{user_id}` (line 97)
- `GET /metrics/summary/{channel_id}` (line 198)
- `GET /health` (line 238)

### share_v2.py
- `POST /create/{report_type}/{channel_id}` (line 90)
- `GET /report/{share_token}` (line 166)
- `GET /info/{share_token}` (line 286)
- `DELETE /revoke/{share_token}` (line 319)
- `GET /cleanup` (line 343)

### content_protection_routes.py
- `POST /watermark/image` (line 31)
- `POST /watermark/video` (line 115)
- `POST /custom-emoji` (line 193)
- `POST /theft-detection` (line 237)
- `GET /files/{filename}` (line 266)
- `GET /premium-features/{tier}` (line 280)
- `GET /usage/{user_id}` (line 302)

## 💡 Recommendations

### Unused API Endpoints
Consider reviewing the following unused endpoints:

1. **Verify Usage**: Double-check if these endpoints are used elsewhere (mobile apps, external integrations, etc.)
2. **Remove Dead Code**: If confirmed unused, consider removing to reduce maintenance overhead
3. **Document**: If kept for future use, ensure they are properly documented

- **GET /dashboard/{channel_id}** - analytics_advanced.py:221
- **GET /metrics/real-time/{channel_id}** - analytics_advanced.py:294
- **GET /alerts/check/{channel_id}** - analytics_advanced.py:320
- **GET /recommendations/{channel_id}** - analytics_advanced.py:346
- **GET /performance/score/{channel_id}** - analytics_advanced.py:375
- **GET /health** - analytics_router.py:266
- **GET /channels** - analytics_router.py:300
- **POST /channels** - analytics_router.py:327
- **GET /channels/{channel_id}** - analytics_router.py:369
- **GET /metrics** - analytics_router.py:398
- **GET /channels/{channel_id}/metrics** - analytics_router.py:453
- **GET /demo/post-dynamics** - analytics_router.py:514
- **GET /demo/best-times** - analytics_router.py:538
- **GET /demo/ai-recommendations** - analytics_router.py:550
- **POST /data-processing/analyze** - analytics_router.py:562
- **POST /predictions/forecast** - analytics_router.py:589
- **GET /insights/{channel_id}** - analytics_router.py:610
- **GET /dashboard/{channel_id}** - analytics_router.py:644
- **POST /refresh/{channel_id}** - analytics_router.py:664
- **GET /summary/{channel_id}** - analytics_router.py:725
- **GET /health** - analytics_unified.py:63
- **GET /dashboard/{channel_id}** - analytics_unified.py:136
- **GET /live-metrics/{channel_id}** - analytics_unified.py:231
- **GET /reports/{channel_id}** - analytics_unified.py:271
- **GET /comparison/{channel_id}** - analytics_unified.py:334
- **GET /health** - analytics_v2.py:45
- **GET /channels/{channel_id}/sources** - analytics_v2.py:249
- **GET /csv/overview/{channel_id}** - exports_v2.py:66
- **GET /csv/growth/{channel_id}** - exports_v2.py:103
- **GET /csv/reach/{channel_id}** - exports_v2.py:138
- **GET /csv/sources/{channel_id}** - exports_v2.py:173
- **GET /png/growth/{channel_id}** - exports_v2.py:211
- **GET /png/reach/{channel_id}** - exports_v2.py:248
- **GET /png/sources/{channel_id}** - exports_v2.py:285
- **GET /dashboard/{user_id}** - mobile_api.py:97
- **GET /metrics/summary/{channel_id}** - mobile_api.py:198
- **GET /health** - mobile_api.py:238
- **POST /create/{report_type}/{channel_id}** - share_v2.py:90
- **GET /report/{share_token}** - share_v2.py:166
- **GET /info/{share_token}** - share_v2.py:286
- **DELETE /revoke/{share_token}** - share_v2.py:319
- **GET /cleanup** - share_v2.py:343
- **POST /watermark/image** - content_protection_routes.py:31
- **POST /watermark/video** - content_protection_routes.py:115
- **POST /custom-emoji** - content_protection_routes.py:193
- **POST /theft-detection** - content_protection_routes.py:237
- **GET /files/{filename}** - content_protection_routes.py:266
- **GET /premium-features/{tier}** - content_protection_routes.py:280
- **GET /usage/{user_id}** - content_protection_routes.py:302

## 📝 Notes

- This audit focused on direct frontend-to-backend API calls
- Some endpoints might be used by external services, mobile apps, or webhooks
- Consider conducting periodic audits as the codebase evolves
