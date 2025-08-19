# AnalyticBot - Enhanced Telegram Channel Analytics Bot

A comprehensive Telegram bot for channel analytics, post scheduling, and performance monitoring with advanced error handling and monitoring capabilities.

## 🚀 Features

### Core Features
- **📊 Channel Analytics**: Track post views, engagement metrics, and channel performance
- **⏰ Post Scheduling**: Schedule messages with media, inline keyboards, and rich formatting
- **📈 Performance Monitoring**: Real-time monitoring with metrics collection
- **🔄 Background Tasks**: Automated view updates and post delivery via Celery
- **🌐 Web Interface**: React-based frontend for easy management
- **🗄️ Database Management**: PostgreSQL with Alembic migrations
- **🔒 Security**: JWT authentication, CORS protection, input validation

### Enhanced Features (New)
- **🛠️ Advanced Error Handling**: Centralized error management with context tracking
- **📊 Comprehensive Monitoring**: System health checks, performance metrics
- **⚡ Improved Performance**: Optimized database connections, rate limiting
- **🔄 Graceful Shutdown**: Proper resource cleanup and signal handling
- **📝 Enhanced Logging**: Structured logging with configurable formats
- **🧪 Integration Tests**: Comprehensive test coverage for all workflows

## 🏗️ Architecture

### Backend Components
```
bot/
├── handlers/           # Telegram message handlers
├── services/          # Business logic layer
├── database/          # Data access layer
│   ├── models.py     # SQLAlchemy models
│   └── repositories/ # Repository pattern implementation
├── middlewares/       # Request processing middleware
├── utils/            # Utilities and helpers
│   ├── error_handler.py    # Centralized error handling
│   ├── monitoring.py       # Metrics and health monitoring
│   └── safe_i18n_core.py  # Internationalization
└── tasks.py          # Celery background tasks
```

### Frontend Components
```
twa-frontend/
├── components/        # React components
├── store/            # State management
└── assets/           # Static assets
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (recommended)

### Environment Configuration

Create `.env` file with the following variables:

```env
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
STORAGE_CHANNEL_ID=your_storage_channel_id

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/analyticbot
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=analyticbot
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Web App
TWA_HOST_URL=https://your-domain.com

# Security
WEBAPP_AUTH_MAX_AGE=3600

# Monitoring & Performance
LOG_LEVEL=INFO
LOG_FORMAT=text
DEBUG_MODE=false
ENABLE_HEALTH_MONITORING=true
TELEGRAM_API_DELAY=0.5
ANALYTICS_UPDATE_INTERVAL=300

# Optional: Error Tracking
SENTRY_DSN=your_sentry_dsn_here
```

### Docker Setup (Recommended)

1. **Clone and setup**:
```bash
git clone https://github.com/AlonurKomilov/analyticbot.git
cd analyticbot
cp .env.example .env  # Edit with your values
```

2. **Start services**:
```bash
docker-compose up -d --build
```

3. **Run migrations**:
```bash
docker-compose exec api alembic upgrade head
```

### Manual Setup

1. **Backend setup**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start bot
python run_bot.py
```

2. **Frontend setup**:
```bash
cd twa-frontend
npm install
npm run build
npm start
```

3. **Start background workers**:
```bash
# Start Celery worker
celery -A bot.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A bot.celery_app beat --loglevel=info
```

## 📊 Monitoring & Health Checks

### Health Endpoints

The application provides comprehensive health monitoring:

- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed`

Example:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","timestamp":"2025-01-01T12:00:00","database":"healthy"}
```

### Metrics Collection

The system automatically collects metrics for:
- Request performance
- Error rates
- Database connections
- Celery task execution
- System resources (CPU, memory)

### Error Handling

Enhanced error handling with:
- Contextual error information
- Automatic error categorization
- Structured logging
- Telegram API specific error handling
- Database error recovery

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests  
pytest tests/integration/ -v

# Complete test suite
pytest tests/ -v --cov=bot
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Load and benchmark testing

## 🔧 Configuration

### Performance Tuning

Key configuration options for optimization:

```env
# Database
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
DB_POOL_TIMEOUT=30

# Telegram API
TELEGRAM_API_DELAY=0.5
TELEGRAM_BATCH_SIZE=50

# Analytics
ANALYTICS_UPDATE_INTERVAL=300
ANALYTICS_BATCH_SIZE=50

# Tasks
TASK_MAX_RETRIES=3
TASK_RETRY_DELAY=60
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check PostgreSQL service: `docker-compose logs postgres`
   - Verify DATABASE_URL configuration
   - Run migrations: `alembic upgrade head`

2. **Telegram API Errors**:
   - Verify BOT_TOKEN is correct and valid
   - Check bot permissions in target channels
   - Review rate limiting configuration

3. **Redis Connection Issues**:
   - Check Redis service: `docker-compose logs redis`
   - Verify REDIS_URL configuration
   - Test Redis connectivity: `redis-cli ping`

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_PROFILING=true
```

## 📈 Key Improvements Made

### 1. Enhanced Error Handling
- Centralized error management with contextual information
- Automatic error categorization (Telegram API, Database, etc.)
- Structured error logging with unique error IDs

### 2. Advanced Monitoring
- Real-time metrics collection for all operations
- System health monitoring with detailed endpoints
- Performance tracking and alerting capabilities

### 3. Database Optimizations
- Connection pooling with retry logic
- Health checks and automatic recovery
- Graceful error handling for database operations

### 4. Improved Performance
- Rate limiting for Telegram API calls
- Optimized batch processing for analytics updates
- Enhanced resource management and cleanup

### 5. Production Readiness
- Graceful shutdown handling
- Comprehensive logging configuration
- Security enhancements and validation
- Docker optimization and health checks

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

## 📝 Changelog

### Version 1.1.0 (Current Enhancement)
- ✅ Enhanced error handling with context tracking
- ✅ Comprehensive monitoring and metrics collection
- ✅ Improved database connection management
- ✅ Advanced logging and debugging capabilities
- ✅ Performance optimizations and rate limiting
- ✅ Graceful shutdown and resource cleanup
- ✅ Integration test coverage
- ✅ Health monitoring endpoints

### Version 1.0.0 (Original)
- ✅ Basic bot functionality with aiogram v3
- ✅ Channel analytics and post scheduling
- ✅ Celery background tasks
- ✅ Web interface integration
- ✅ Multi-language support (EN/UZ)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Telegram community**

```
