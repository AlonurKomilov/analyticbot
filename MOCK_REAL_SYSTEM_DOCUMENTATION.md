# Mock/Real System Architecture Documentation

## Overview

This project implements a comprehensive adapter pattern for clean separation between mock and real data sources. The architecture provides seamless switching between development (mock) and production (real) environments without code changes, enabling efficient development, testing, and deployment workflows.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Frontend System](#frontend-system)
3. [Backend System](#backend-system)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Design Principles

- **Clean Separation**: Mock and real implementations are completely isolated
- **Runtime Switching**: Change data sources without code modifications
- **Centralized Configuration**: Single source of truth for system settings
- **Type Safety**: Full TypeScript/JavaScript type support
- **Performance**: Minimal overhead and optimized data handling
- **Scalability**: Easy to add new data sources and providers

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                         │
├─────────────────────────────────────────────────────────────┤
│  React Hooks  │  Data Services  │  Configuration Manager    │
│  useDataSource│  DataService    │  DataSourceManager        │
│  useAnalytics │  MockService    │  MockConfig              │
├─────────────────────────────────────────────────────────────┤
│                      Backend Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Adapter Factory │  Implementations │  Services             │
│  PaymentFactory  │  MockAdapter     │  PaymentService       │
│  AnalyticsFactory│  StripeAdapter   │  AnalyticsService     │
│                 │  TelegramAdapter │  ModernAnalyticsService│
└─────────────────────────────────────────────────────────────┘
```

## Frontend System

### Core Components

#### 1. DataSourceManager (Singleton)
Central coordinator for data source management.

```javascript
import { DataSourceManager } from './utils/dataSourceManager.js';

const manager = new DataSourceManager();
await manager.switchToSource('mock');
```

#### 2. React Hooks
Type-safe hooks for component integration.

```javascript
import { useDataSource, useAnalytics } from './hooks/useDataSource.js';

function MyComponent() {
  const { currentDataSource, isUsingMock, switchDataSource } = useDataSource();
  const { channelOverview, loading, error } = useAnalytics(channelId, days);
  
  return (
    <div>
      <p>Data Source: {currentDataSource}</p>
      {loading ? <Spinner /> : <AnalyticsDisplay data={channelOverview} />}
    </div>
  );
}
```

#### 3. Data Services
Factory pattern for API/mock switching.

```javascript
import { dataServiceFactory } from './services/dataService.js';

const dataService = dataServiceFactory.getCurrentService();
const analytics = await dataService.getChannelAnalytics(channelId, period);
```

### Configuration Files

#### mockConfig.js
```javascript
export const mockConfig = {
  enabled: true,
  apiEndpoint: 'http://localhost:3001/api/mock',
  realtimeUpdates: true,
  responseDelay: { min: 100, max: 500 },
  errorSimulation: { enabled: false, rate: 0.05 },
  logging: { enabled: true, level: 'info' }
};
```

#### .env.mock.example
```bash
# Mock System Configuration
USE_MOCK_ANALYTICS=true
USE_MOCK_PAYMENT=true

# Mock API Settings
MOCK_API_ENDPOINT=http://localhost:3001/api/mock
MOCK_RESPONSE_DELAY=200
MOCK_ERROR_RATE=0.02

# Development Settings
REACT_APP_ENABLE_MOCK_SWITCHING=true
REACT_APP_SHOW_DATA_SOURCE_INDICATOR=true
```

## Backend System

### Adapter Pattern Implementation

#### 1. Payment System

##### Base Adapter Interface
```python
# apps/bot/services/adapters/base_adapter.py
from abc import ABC, abstractmethod

class PaymentGatewayAdapter(ABC):
    @abstractmethod
    def get_adapter_name(self) -> str:
        pass
    
    @abstractmethod
    async def create_customer(self, user_data: dict) -> dict:
        pass
    
    @abstractmethod
    async def create_payment_intent(self, amount, currency, customer_id, payment_method_id, metadata=None) -> dict:
        pass
```

##### Mock Implementation
```python
# apps/bot/services/adapters/mock_payment_adapter.py
class MockPaymentAdapter(PaymentGatewayAdapter):
    def get_adapter_name(self) -> str:
        return "mock_payment_gateway"
    
    async def create_customer(self, user_data: dict) -> dict:
        # Generate realistic mock customer data
        customer_id = f"cus_mock_{uuid.uuid4().hex[:12]}"
        return {"success": True, "customer_id": customer_id}
```

##### Real Implementation
```python
# apps/bot/services/adapters/stripe_payment_adapter.py
class StripePaymentAdapter(PaymentGatewayAdapter):
    def get_adapter_name(self) -> str:
        return "stripe"
    
    async def create_customer(self, user_data: dict) -> dict:
        # Real Stripe API integration
        customer = stripe.Customer.create(**user_data)
        return {"success": True, "customer_id": customer.id}
```

##### Factory Pattern
```python
# apps/bot/services/adapters/payment_adapter_factory.py
class PaymentAdapterFactory:
    @classmethod
    def get_current_adapter(cls) -> PaymentGatewayAdapter:
        use_mock = getattr(settings, 'USE_MOCK_PAYMENT', False)
        gateway = PaymentGateway.MOCK if use_mock else PaymentGateway.STRIPE
        return cls.create_adapter(gateway)
```

#### 2. Analytics System

##### Mock Analytics Adapter
```python
# apps/bot/services/adapters/mock_analytics_adapter.py
class MockAnalyticsAdapter(AnalyticsAdapter):
    async def get_channel_analytics(self, channel_id: str, start_date: datetime, end_date: datetime) -> dict:
        # Generate realistic mock analytics with trends
        days = (end_date - start_date).days + 1
        base_subscribers = 1000 + (hash(channel_id) % 10000)
        return {
            "channel_id": channel_id,
            "overview": {
                "total_subscribers": base_subscribers,
                "avg_engagement_rate": round(random.uniform(3.5, 8.5), 2)
            },
            "metadata": {"mock": True, "adapter": "mock_analytics"}
        }
```

##### Real Telegram Adapter
```python
# apps/bot/services/adapters/telegram_analytics_adapter.py
class TelegramAnalyticsAdapter(AnalyticsAdapter):
    def __init__(self, bot_token: str, rate_limit_config: RateLimitConfig):
        self.bot_token = bot_token
        self.rate_limiter = RateLimiter(rate_limit_config)
    
    async def get_channel_analytics(self, channel_id: str, start_date: datetime, end_date: datetime) -> dict:
        # Real Telegram Bot API integration with rate limiting
        channel_info = await self._get_channel_info(channel_id)
        member_count = await self._get_channel_member_count(channel_id)
        return {
            "channel_id": channel_id,
            "channel_info": channel_info,
            "overview": {"total_subscribers": member_count},
            "metadata": {"real_data": True, "adapter": "telegram_analytics"}
        }
```

## Configuration

### Environment Variables

#### Development (.env.development)
```bash
# Data Source Configuration
USE_MOCK_ANALYTICS=true
USE_MOCK_PAYMENT=true

# Mock Settings
MOCK_API_DELAY=200
MOCK_ERROR_RATE=0.02
MOCK_ENABLE_CACHING=true

# Development Features
ENABLE_DATA_SOURCE_SWITCHING=true
SHOW_MOCK_INDICATORS=true
LOG_LEVEL=debug
```

#### Production (.env.production)
```bash
# Data Source Configuration
USE_MOCK_ANALYTICS=false
USE_MOCK_PAYMENT=false

# Real API Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Performance Settings
CACHE_TTL=300
RATE_LIMIT_CALLS_PER_SECOND=1.0
RATE_LIMIT_CALLS_PER_HOUR=500
```

#### Testing (.env.test)
```bash
# Always use mock for tests
USE_MOCK_ANALYTICS=true
USE_MOCK_PAYMENT=true

# Test-specific settings
MOCK_CONSISTENT_DATA=true
MOCK_DISABLE_DELAYS=true
TEST_MODE=true
```

### Configuration Schema

```javascript
// Configuration validation schema
const configSchema = {
  dataSources: {
    analytics: {
      current: 'mock' | 'telegram',
      mock: {
        enabled: boolean,
        responseDelay: number,
        errorRate: number,
        caching: boolean
      },
      telegram: {
        botToken: string,
        rateLimiting: {
          callsPerSecond: number,
          callsPerMinute: number,
          callsPerHour: number
        }
      }
    },
    payment: {
      current: 'mock' | 'stripe',
      mock: { enabled: boolean },
      stripe: {
        secretKey: string,
        webhookSecret: string
      }
    }
  }
};
```

## Usage Examples

### 1. Frontend Component with Data Source Switching

```javascript
import React from 'react';
import { useDataSource, useAnalytics } from '../hooks/useDataSource';
import DataSourceSettings from '../components/DataSourceSettings';

function AnalyticsDashboard({ channelId }) {
  const { currentDataSource, isUsingMock, switchDataSource } = useDataSource();
  const { channelOverview, loading, error, refreshData } = useAnalytics(channelId, 30);

  const handleToggleDataSource = async () => {
    const newSource = isUsingMock ? 'real' : 'mock';
    await switchDataSource(newSource);
    await refreshData();
  };

  return (
    <div>
      <div className="data-source-controls">
        <span>Current: {currentDataSource}</span>
        <button onClick={handleToggleDataSource}>
          Switch to {isUsingMock ? 'Real' : 'Mock'} Data
        </button>
      </div>
      
      {loading && <div>Loading analytics...</div>}
      {error && <div>Error: {error.message}</div>}
      
      {channelOverview && (
        <div>
          <h2>Channel Analytics</h2>
          <p>Subscribers: {channelOverview.raw_analytics.overview.total_subscribers}</p>
          <p>Engagement: {channelOverview.raw_analytics.overview.avg_engagement_rate}%</p>
          <small>Source: {channelOverview.service_metadata.adapter}</small>
        </div>
      )}
    </div>
  );
}
```

### 2. Backend Service Integration

```python
# Using payment service with adapter switching
from apps.bot.services.payment_service import PaymentService
from apps.bot.services.adapters.payment_adapter_factory import PaymentGateway

# Create payment service (uses current configured adapter)
payment_service = PaymentService(payment_repository)

# Or explicitly set adapter
payment_service = PaymentService(payment_repository, gateway=PaymentGateway.MOCK)

# Switch adapter at runtime
payment_service.switch_payment_gateway(PaymentGateway.STRIPE)

# Process payment (adapter-agnostic)
result = await payment_service.process_payment(
    amount=Decimal('29.99'),
    currency='USD',
    customer_id='cus_123',
    payment_method_id='pm_456'
)
```

### 3. Testing with Different Data Sources

```python
# test_payment_service.py
import pytest
from apps.bot.services.adapters.payment_adapter_factory import PaymentGateway

class TestPaymentService:
    async def test_payment_with_mock_adapter(self):
        service = PaymentService(mock_repository, gateway=PaymentGateway.MOCK)
        result = await service.process_payment(...)
        assert result['success'] is True
        assert 'mock' in result['provider_payment_id']

    async def test_payment_with_stripe_adapter(self):
        service = PaymentService(mock_repository, gateway=PaymentGateway.STRIPE)
        # This test requires proper Stripe configuration
        result = await service.process_payment(...)
        assert result['success'] is True
```

## Best Practices

### 1. Development Workflow

```bash
# Start with mock data for rapid development
export USE_MOCK_ANALYTICS=true
export USE_MOCK_PAYMENT=true
npm run dev

# Test with real APIs before deployment
export USE_MOCK_ANALYTICS=false
export USE_MOCK_PAYMENT=false
# Ensure API keys are configured
npm run test

# Deploy with production configuration
npm run build
npm run deploy
```

### 2. Component Design

- Always use hooks for data fetching
- Handle loading and error states consistently
- Show data source indicators in development
- Implement graceful fallbacks for API failures

```javascript
// Good: Using hooks with proper error handling
function MyComponent({ channelId }) {
  const { channelOverview, loading, error } = useAnalytics(channelId);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!channelOverview) return <EmptyState />;
  
  return <AnalyticsDisplay data={channelOverview} />;
}

// Bad: Direct API calls without abstraction
function MyComponent({ channelId }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Direct API call - hard to switch between mock/real
    fetch(`/api/analytics/${channelId}`)
      .then(res => res.json())
      .then(setData);
  }, [channelId]);
  
  return <div>{data?.subscribers}</div>;
}
```

### 3. Backend Adapter Implementation

- Always implement the full interface
- Use consistent error handling patterns
- Add comprehensive logging
- Include health check methods

```python
# Good: Complete adapter implementation
class MyPaymentAdapter(PaymentGatewayAdapter):
    def __init__(self, config):
        self.config = config
        logger.info(f"Initialized {self.get_adapter_name()} adapter")
    
    def get_adapter_name(self) -> str:
        return "my_payment_provider"
    
    async def create_customer(self, user_data: dict) -> dict:
        try:
            # Implementation with proper error handling
            result = await self._make_api_call('customers', user_data)
            logger.info(f"Created customer: {result['id']}")
            return {"success": True, "customer_id": result['id']}
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> dict:
        try:
            await self._make_api_call('health')
            return {"status": "healthy", "adapter": self.get_adapter_name()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

### 4. Configuration Management

- Use environment-specific configuration files
- Validate configuration on startup
- Provide clear error messages for misconfiguration
- Document all configuration options

```python
# config/settings.py - Configuration validation
class Settings:
    def __init__(self):
        self.USE_MOCK_ANALYTICS = self._get_bool_env('USE_MOCK_ANALYTICS', default=False)
        self.USE_MOCK_PAYMENT = self._get_bool_env('USE_MOCK_PAYMENT', default=False)
        
        if not self.USE_MOCK_PAYMENT:
            self.STRIPE_SECRET_KEY = self._get_required_env('STRIPE_SECRET_KEY')
            
        if not self.USE_MOCK_ANALYTICS:
            self.TELEGRAM_BOT_TOKEN = self._get_required_env('TELEGRAM_BOT_TOKEN')
    
    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
```

## Troubleshooting

### Common Issues

#### 1. Data Source Not Switching

**Problem**: Changes to USE_MOCK_* variables don't take effect

**Solution**:
```bash
# Frontend: Restart development server
npm run dev

# Backend: Restart application
python manage.py runserver

# Clear adapter cache if using factory pattern
from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory
PaymentAdapterFactory.clear_cache()
```

#### 2. Mock Data Not Loading

**Problem**: Mock service returns empty or error responses

**Solution**:
```javascript
// Check mock configuration
import { mockConfig } from './config/mockConfig.js';
console.log('Mock config:', mockConfig);

// Verify mock service initialization
import { MockService } from './services/mockService.js';
const service = new MockService();
console.log('Mock service ready:', service.isReady());

// Check network requests in browser dev tools
// Mock API should show requests to mock endpoints
```

#### 3. Real API Rate Limiting

**Problem**: Too many requests to real APIs

**Solution**:
```python
# Adjust rate limiting configuration
rate_limit_config = RateLimitConfig(
    calls_per_second=0.5,  # Reduce from 1.0
    calls_per_minute=15,   # Reduce from 20
    calls_per_hour=300     # Reduce from 500
)

adapter = TelegramAnalyticsAdapter(bot_token, rate_limit_config)
```

#### 4. Configuration Errors

**Problem**: Missing or invalid configuration

**Solution**:
```bash
# Validate required environment variables
python -c "
from config.settings import settings
print('Analytics adapter:', settings.USE_MOCK_ANALYTICS)
print('Payment adapter:', settings.USE_MOCK_PAYMENT)
"

# Check environment file loading
export $(grep -v '^#' .env.development | xargs)
echo $USE_MOCK_ANALYTICS
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Frontend
export REACT_APP_DEBUG_MODE=true
export REACT_APP_LOG_LEVEL=debug

# Backend
export LOG_LEVEL=DEBUG
export DEBUG_ADAPTERS=true
```

### Health Checks

Verify system health:

```python
# Check all adapters
from apps.bot.services.adapters.payment_adapter_factory import PaymentAdapterFactory
from apps.bot.services.adapters.analytics_adapter_factory import AnalyticsAdapterFactory

payment_health = await PaymentAdapterFactory.health_check_all()
analytics_health = await AnalyticsAdapterFactory.health_check_all()

print("Payment adapters:", payment_health)
print("Analytics adapters:", analytics_health)
```

## Performance Considerations

### Mock System Optimization

- Use caching for frequently accessed mock data
- Implement realistic response delays in development
- Avoid generating expensive mock data on every request

### Real System Optimization  

- Implement proper rate limiting and retry logic
- Cache API responses where appropriate
- Use connection pooling for external APIs
- Monitor API quota usage

### Memory Management

- Clear adapter caches periodically
- Implement proper cleanup in adapter destructors
- Monitor memory usage with large datasets

This architecture provides a robust, scalable foundation for managing mock and real data sources across your entire application stack.