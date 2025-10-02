# 📡 AnalyticBot API Documentation

**Version**: 2.0  
**Last Updated**: October 2, 2025  
**Base URL**: `https://api.analyticbot.com`  
**API Type**: RESTful API with FastAPI  

---

## 📖 **Table of Contents**

1. [Quick Start](#-quick-start)
2. [Authentication](#-authentication)
3. [Core Endpoints](#-core-endpoints)
4. [Analytics & Statistics](#-analytics--statistics)
5. [Channel Management](#-channel-management)
6. [AI & Insights](#-ai--insights)
7. [Administration](#-administration)
8. [Error Handling](#-error-handling)
9. [Rate Limiting](#-rate-limiting)
10. [Code Examples](#-code-examples)

---

## 🚀 **Quick Start**

### **Base API Information**
- **Framework**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT Bearer tokens
- **Data Format**: JSON request/response
- **Rate Limiting**: 1000 requests/hour per user
- **Documentation**: Available at `/docs` (Swagger) and `/redoc`

### **Quick Test Request**
```bash
curl -X GET "https://api.analyticbot.com/health/" \
     -H "accept: application/json"
```

### **Authentication Example**
```bash
curl -X POST "https://api.analyticbot.com/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

---

## 🔐 **Authentication**

### **Authentication Methods**

| Method | Endpoint | Description | Required Headers |
|--------|----------|-------------|------------------|
| **Login** | `POST /auth/login` | Authenticate user and get JWT token | `Content-Type: application/json` |
| **Register** | `POST /auth/register` | Create new user account | `Content-Type: application/json` |
| **Refresh** | `POST /auth/refresh` | Refresh expired JWT token | `Authorization: Bearer <token>` |
| **Logout** | `POST /auth/logout` | Invalidate current token | `Authorization: Bearer <token>` |

### **JWT Token Usage**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Authentication Flow**

#### **1. Login Request**
```json
POST /auth/login
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

#### **2. Login Response**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "username": "user@example.com",
      "role": "user"
    }
  },
  "message": "Login successful",
  "timestamp": "2025-10-02T10:30:00Z"
}
```

#### **3. Protected Endpoint Usage**
```bash
curl -X GET "https://api.analyticbot.com/channels" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🏗️ **Core Endpoints**

### **🔍 Health & System**

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/health/` | GET | Basic health check | ❌ No |
| `/health/detailed` | GET | Detailed system health | ❌ No |
| `/health/ready` | GET | Kubernetes readiness probe | ❌ No |
| `/health/live` | GET | Kubernetes liveness probe | ❌ No |
| `/system/performance` | GET | Performance metrics | ✅ Yes |
| `/system/initial-data` | GET | Application startup data | ✅ Yes |

#### **Health Check Example**
```json
GET /health/
{
  "status": "healthy",
  "timestamp": "2025-10-02T10:30:00Z",
  "version": "2.0.0",
  "uptime": 3600
}
```

### **👤 User Profile**

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/auth/me` | GET | Get current user profile | ✅ Yes |
| `/auth/profile/permissions` | GET | Get user permissions | ✅ Yes |
| `/auth/mfa/status` | GET | MFA status | ✅ Yes |

---

## 📊 **Analytics & Statistics**

### **📈 Core Statistics**

| Endpoint | Method | Description | Parameters |
|----------|---------|-------------|------------|
| `/statistics/overview/{channel_id}` | GET | Channel overview metrics | `channel_id`, `period?` |
| `/statistics/growth/{channel_id}` | GET | Growth analytics | `channel_id`, `days?` |
| `/statistics/metrics/{channel_id}` | GET | Detailed metrics | `channel_id`, `metrics?` |
| `/statistics/top-posts/{channel_id}` | GET | Top performing posts | `channel_id`, `limit?` |
| `/statistics/sources/{channel_id}` | GET | Traffic sources | `channel_id`, `period?` |

#### **Channel Overview Example**
```json
GET /statistics/overview/123
{
  "success": true,
  "data": {
    "channel_id": 123,
    "period": "7d",
    "metrics": {
      "total_subscribers": 15420,
      "subscriber_growth": 234,
      "total_views": 45600,
      "avg_engagement": 0.074,
      "top_post_views": 2340
    },
    "growth_rate": 0.015,
    "engagement_trend": "increasing"
  },
  "timestamp": "2025-10-02T10:30:00Z"
}
```

### **📊 Reports & Analytics**

| Endpoint | Method | Description | Response Format |
|----------|---------|-------------|-----------------|
| `/statistics/analytical/{channel_id}` | GET | Analytical report | JSON |
| `/statistics/comparison/{channel_id}` | GET | Comparison analytics | JSON |
| `/statistics/trends/top-posts` | GET | Trending posts analysis | JSON |
| `/statistics/performance-summary/{channel_id}` | GET | Performance summary | JSON |

### **🔥 Live Analytics**

| Endpoint | Method | Description | Real-time |
|----------|---------|-------------|-----------|
| `/analytics-live/metrics/{channel_id}` | GET | Real-time metrics | ✅ Yes |
| `/analytics-live/performance/{channel_id}` | GET | Live performance data | ✅ Yes |
| `/analytics-live/monitor/{channel_id}` | GET | Live monitoring | ✅ Yes |
| `/analytics-live/live-metrics/{channel_id}` | GET | Streaming metrics | ✅ Yes |

---

## 📺 **Channel Management**

### **📋 Channel Operations**

| Endpoint | Method | Description | Auth Level |
|----------|---------|-------------|------------|
| `/channels` | GET | List user channels | User |
| `/channels` | POST | Create new channel | User |
| `/channels/{channel_id}` | GET | Get channel details | User |
| `/channels/{channel_id}` | PUT | Update channel | Owner |
| `/channels/{channel_id}` | DELETE | Delete channel | Owner |
| `/channels/{channel_id}/activate` | POST | Activate channel | Owner |
| `/channels/{channel_id}/deactivate` | POST | Deactivate channel | Owner |
| `/channels/{channel_id}/status` | GET | Channel status | User |

#### **Create Channel Example**
```json
POST /channels
{
  "name": "My Analytics Channel",
  "telegram_id": "@my_channel",
  "description": "Channel for analytics tracking",
  "category": "technology",
  "language": "en"
}
```

#### **Channel Response**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "name": "My Analytics Channel",
    "telegram_id": "@my_channel",
    "status": "active",
    "created_at": "2025-10-02T10:30:00Z",
    "subscriber_count": 0,
    "analytics_enabled": true
  },
  "message": "Channel created successfully"
}
```

---

## 🤖 **AI & Insights**

### **🧠 AI Services**

| Endpoint | Method | Description | AI Model |
|----------|---------|-------------|----------|
| `/ai-services/content/analyze` | POST | Content optimization | GPT-4 |
| `/ai-services/churn/analyze` | POST | Churn prediction | Custom ML |
| `/ai-services/security/analyze` | POST | Security analysis | Custom |
| `/ai-services/stats` | GET | AI service statistics | - |

#### **Content Analysis Example**
```json
POST /ai-services/content/analyze
{
  "channel_id": 123,
  "content": "Your post content here",
  "analysis_type": "optimization"
}
```

#### **AI Analysis Response**
```json
{
  "success": true,
  "data": {
    "optimization_score": 0.85,
    "suggestions": [
      "Add more engaging hashtags",
      "Optimize posting time to 18:00-20:00",
      "Include call-to-action"
    ],
    "sentiment": "positive",
    "readability_score": 0.78,
    "predicted_engagement": 0.094
  },
  "processing_time_ms": 234
}
```

### **🔮 Predictive Insights**

| Endpoint | Method | Description | Prediction Type |
|----------|---------|-------------|-----------------|
| `/insights/recommendations/{channel_id}` | GET | Content recommendations | ML-based |
| `/insights/forecast` | POST | Growth forecasting | Time series |
| `/insights/best-times/{channel_id}` | GET | Optimal posting times | Behavioral |
| `/insights/growth-forecast/{channel_id}` | GET | Growth predictions | Statistical |

### **🎯 Engagement Analytics**

| Endpoint | Method | Description | Analysis Type |
|----------|---------|-------------|---------------|
| `/insights/channels/{channel_id}/engagement` | GET | Engagement analysis | Comprehensive |
| `/insights/channels/{channel_id}/audience` | GET | Audience insights | Demographic |
| `/insights/channels/{channel_id}/trending` | GET | Trending content | Real-time |
| `/insights/engagement-patterns/{channel_id}` | GET | Engagement patterns | Behavioral |

---

## 👑 **Administration**

### **🔧 Admin Channels**

| Endpoint | Method | Description | Admin Level |
|----------|---------|-------------|-------------|
| `/admin/channels` | GET | List all channels | Admin |
| `/admin/channels/{channel_id}` | DELETE | Delete any channel | Super Admin |
| `/admin/channels/{channel_id}/suspend` | POST | Suspend channel | Admin |
| `/admin/channels/{channel_id}/unsuspend` | POST | Unsuspend channel | Admin |

### **👥 Admin Users**

| Endpoint | Method | Description | Admin Level |
|----------|---------|-------------|-------------|
| `/admin/users/{user_id}/channels` | GET | User's channels | Admin |
| `/superadmin/users` | GET | List all users | Super Admin |
| `/superadmin/users/{user_id}/suspend` | POST | Suspend user | Super Admin |
| `/superadmin/users/{user_id}/reactivate` | POST | Reactivate user | Super Admin |

### **📊 System Administration**

| Endpoint | Method | Description | Admin Level |
|----------|---------|-------------|-------------|
| `/admin/system/stats` | GET | System statistics | Admin |
| `/admin/system/audit/recent` | GET | Recent audit logs | Admin |
| `/superadmin/stats` | GET | Complete system stats | Super Admin |
| `/superadmin/audit-logs` | GET | Full audit logs | Super Admin |
| `/superadmin/config` | GET | System configuration | Super Admin |
| `/superadmin/config/{key}` | PUT | Update configuration | Super Admin |

---

## 📤 **Data Export**

### **📄 CSV Exports**

| Endpoint | Method | Description | Format |
|----------|---------|-------------|---------|
| `/exports/csv/overview/{channel_id}` | GET | Overview data export | CSV |
| `/exports/csv/growth/{channel_id}` | GET | Growth data export | CSV |
| `/exports/csv/reach/{channel_id}` | GET | Reach data export | CSV |
| `/exports/csv/sources/{channel_id}` | GET | Sources data export | CSV |

### **🖼️ Image Exports**

| Endpoint | Method | Description | Format |
|----------|---------|-------------|---------|
| `/exports/png/growth/{channel_id}` | GET | Growth chart | PNG |
| `/exports/png/reach/{channel_id}` | GET | Reach chart | PNG |
| `/exports/png/sources/{channel_id}` | GET | Sources chart | PNG |

---

## 🔗 **Sharing & Links**

### **📎 Share Management**

| Endpoint | Method | Description | Access Level |
|----------|---------|-------------|--------------|
| `/sharing/create/{report_type}/{channel_id}` | POST | Create share link | Owner |
| `/sharing/report/{share_token}` | GET | Access shared report | Public |
| `/sharing/info/{share_token}` | GET | Share link info | Public |
| `/sharing/revoke/{share_token}` | DELETE | Revoke share link | Owner |
| `/sharing/cleanup` | GET | Cleanup expired links | Admin |

---

## ⚠️ **Error Handling**

### **Standard Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error details",
    "field": "field_name" // For validation errors
  },
  "timestamp": "2025-10-02T10:30:00Z"
}
```

### **HTTP Status Codes**

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| **200** | Success | Request completed successfully |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid request data or parameters |
| **401** | Unauthorized | Missing or invalid authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource does not exist |
| **422** | Validation Error | Request data validation failed |
| **429** | Rate Limited | Too many requests |
| **500** | Server Error | Internal server error |

### **Common Error Examples**

#### **Authentication Error**
```json
HTTP 401 Unauthorized
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Authentication token is invalid or expired",
    "details": "Please login again to get a new token"
  },
  "timestamp": "2025-10-02T10:30:00Z"
}
```

#### **Validation Error**
```json
HTTP 422 Unprocessable Entity
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": "channel_id must be a positive integer",
    "field": "channel_id"
  },
  "timestamp": "2025-10-02T10:30:00Z"
}
```

#### **Rate Limit Error**
```json
HTTP 429 Too Many Requests
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": "Rate limit: 1000 requests per hour. Reset in 1800 seconds"
  },
  "timestamp": "2025-10-02T10:30:00Z"
}
```

---

## 🚦 **Rate Limiting**

### **Rate Limit Rules**

| User Type | Requests/Hour | Requests/Minute | Burst Limit |
|-----------|---------------|-----------------|-------------|
| **Free User** | 1,000 | 50 | 100 |
| **Premium User** | 5,000 | 200 | 500 |
| **Admin** | 10,000 | 500 | 1,000 |
| **API Client** | 50,000 | 2,000 | 5,000 |

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 875
X-RateLimit-Reset: 1633024800
X-RateLimit-Retry-After: 1800
```

---

## 💻 **Code Examples**

### **Python Example**
```python
import requests
import json

# Authentication
auth_response = requests.post('https://api.analyticbot.com/auth/login', 
    json={'username': 'user@example.com', 'password': 'password'})
token = auth_response.json()['data']['access_token']

# Headers for authenticated requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Get channel analytics
response = requests.get('https://api.analyticbot.com/statistics/overview/123', 
    headers=headers)
analytics = response.json()

print(f"Subscriber growth: {analytics['data']['metrics']['subscriber_growth']}")
```

### **JavaScript/Node.js Example**
```javascript
const axios = require('axios');

// Authentication
const authResponse = await axios.post('https://api.analyticbot.com/auth/login', {
  username: 'user@example.com',
  password: 'password'
});

const token = authResponse.data.data.access_token;

// Configure axios with token
const api = axios.create({
  baseURL: 'https://api.analyticbot.com',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Get channel list
const channelsResponse = await api.get('/channels');
console.log('Channels:', channelsResponse.data.data);

// Get analytics for first channel
const channelId = channelsResponse.data.data[0].id;
const analyticsResponse = await api.get(`/statistics/overview/${channelId}`);
console.log('Analytics:', analyticsResponse.data.data);
```

### **cURL Examples**

#### **Complete Workflow**
```bash
#!/bin/bash

# 1. Login and get token
TOKEN=$(curl -s -X POST "https://api.analyticbot.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}' \
  | jq -r '.data.access_token')

# 2. Get channels
curl -s -X GET "https://api.analyticbot.com/channels" \
  -H "Authorization: Bearer $TOKEN" | jq '.data'

# 3. Get analytics for channel 123
curl -s -X GET "https://api.analyticbot.com/statistics/overview/123" \
  -H "Authorization: Bearer $TOKEN" | jq '.data'

# 4. Create new channel
curl -s -X POST "https://api.analyticbot.com/channels" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Channel",
    "telegram_id": "@new_channel",
    "description": "Test channel"
  }' | jq '.data'
```

---

## 🔗 **Additional Resources**

### **Interactive Documentation**
- **Swagger UI**: `https://api.analyticbot.com/docs`
- **ReDoc**: `https://api.analyticbot.com/redoc`
- **OpenAPI Spec**: `https://api.analyticbot.com/openapi.json`

### **SDKs and Libraries**
- **Python SDK**: `pip install analyticbot-sdk`
- **JavaScript SDK**: `npm install @analyticbot/sdk`
- **Go SDK**: Available on GitHub
- **Postman Collection**: [Download here](./docs/postman/)

### **Support & Community**
- **GitHub Repository**: [https://github.com/AlonurKomilov/analyticbot](https://github.com/AlonurKomilov/analyticbot)
- **API Status Page**: `https://status.analyticbot.com`
- **Developer Discord**: Community support channel
- **Email Support**: `api-support@analyticbot.com`

---

## 📋 **Summary**

### **API Capabilities**
- ✅ **Complete Analytics**: Comprehensive channel analytics and insights
- ✅ **Real-time Data**: Live metrics and monitoring
- ✅ **AI-Powered**: Machine learning insights and predictions
- ✅ **Admin Management**: Full administrative capabilities
- ✅ **Data Export**: Multiple export formats (CSV, PNG)
- ✅ **Sharing**: Secure report sharing and collaboration

### **Authentication & Security**
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Role-based Access**: User, Admin, Super Admin levels
- ✅ **Rate Limiting**: Protection against abuse
- ✅ **Data Validation**: Comprehensive input validation

### **Developer Experience**
- ✅ **RESTful Design**: Standard HTTP methods and status codes
- ✅ **JSON API**: Consistent request/response format
- ✅ **Interactive Docs**: Swagger and ReDoc documentation
- ✅ **Code Examples**: Multiple programming languages
- ✅ **Error Handling**: Descriptive error messages

---

**API Version**: 2.0  
**Last Updated**: October 2, 2025  
**Documentation Version**: 1.0  
**Support**: For API questions, create an issue on GitHub or contact api-support@analyticbot.com