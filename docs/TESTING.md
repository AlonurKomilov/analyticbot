# 🧪 Testing Infrastructure Documentation

This document provides comprehensive guidance on the testing infrastructure, automated workflows, and quality assurance processes for AnalyticBot.

## 📋 Table of Contents

- [Testing Overview](#testing-overview)
- [Test Types and Coverage](#test-types-and-coverage)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Local Development Testing](#local-development-testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Quality Gates](#quality-gates)
- [Troubleshooting](#troubleshooting)

## 🎯 Testing Overview

Our testing infrastructure provides comprehensive coverage across multiple dimensions:

### Test Pyramid
```
        🔺 E2E Tests (Integration)
       🔺🔺 API Tests (Integration)
      🔺🔺🔺 Service Tests (Unit)
     🔺🔺🔺🔺 Repository Tests (Unit)
```

### Quality Assurance Layers
- **Unit Tests**: Individual function/method validation
- **Integration Tests**: Service interaction verification
- **Performance Tests**: Load, memory, and benchmark testing
- **Security Tests**: Vulnerability and dependency scanning
- **Frontend Tests**: Component and user interaction testing

## 🔬 Test Types and Coverage

### Backend Testing (`tests/`)

#### Unit Tests
```bash
# Service layer tests
tests/test_analytics_service.py     # Analytics service functionality
tests/test_guard_service.py         # Security and rate limiting
tests/test_subscription_service.py  # Subscription management

# Repository layer tests
tests/unit/test_repositories.py     # Database operations
tests/unit/test_db_retry.py          # Database resilience
```

#### Integration Tests
```bash
# Full system integration
tests/test_integration_complete.py  # End-to-end workflows
tests/integration/test_migrations.py # Database migration testing

# Health and monitoring
tests/unit/test_health_endpoint.py   # Health check endpoints
```

#### Performance Tests
```bash
# Performance benchmarking
tests/test_performance.py           # Comprehensive performance suite
```

### Frontend Testing (`twa-frontend/src/`)

#### Component Tests
```bash
# Unit tests for React components
src/**/*.test.jsx                   # Component functionality
src/**/*.test.js                    # Utility functions
```

#### Integration Tests
```bash
# API integration tests
src/services/*.test.js              # Service layer testing
```

### Configuration Testing
```bash
tests/unit/test_settings_env.py     # Environment configuration
```

## 🚀 GitHub Actions Workflows

### 1. Enhanced CI Pipeline (`.github/workflows/ci-enhanced.yml`)

**Triggers:**
- Push to main/develop branches
- Pull requests
- Scheduled daily runs

**Stages:**
1. **Preflight Checks**
   - Code formatting (ruff)
   - Type checking (mypy)
   - Security linting (bandit)

2. **Quality Gates**
   - Coverage threshold enforcement
   - Performance benchmarks
   - Security scan results

3. **Database Tests**
   - Migration testing
   - Repository layer validation
   - Connection resilience

4. **Application Tests**
   - Service layer testing
   - API endpoint validation
   - Business logic verification

5. **Frontend Tests**
   - Component testing
   - Build verification
   - Linting and formatting

6. **Compose Tests**
   - Full stack integration
   - Service connectivity
   - Health checks

**Matrix Testing:**
- Python 3.11 & 3.12
- Multiple database configurations
- Different Redis configurations

### 2. Security Enhanced Pipeline (`.github/workflows/security-enhanced.yml`)

**Security Scanning Tools:**
- **Gitleaks**: Secret detection
- **Trivy**: Vulnerability scanning
- **CodeQL**: Static analysis
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability checking
- **Semgrep**: Pattern-based security analysis

**Reports Generated:**
- SARIF uploads to GitHub Security tab
- Vulnerability summaries
- Dependency audit reports
- Security recommendation comments on PRs

### 3. Performance Testing Pipeline (`.github/workflows/performance-testing.yml`)

**Performance Metrics:**
- Response time benchmarks
- Memory usage profiling
- Load testing with Locust
- Database query performance
- Concurrent operation handling

**Baseline Comparison:**
- Historical performance tracking
- Regression detection
- Performance gates enforcement

### 4. Release Automation (`.github/workflows/release.yml`)

**Release Process:**
1. Version validation
2. Comprehensive test execution
3. Docker image building
4. Security scanning of artifacts
5. GitHub release creation
6. Stakeholder notification
7. Deployment issue creation

## ⚡ Performance Testing

### Performance Test Suite (`tests/test_performance.py`)

#### Benchmark Categories
1. **Service Performance**
   - Analytics service response times
   - Guard service rate limiting
   - Subscription service operations

2. **Memory Management**
   - Memory leak detection
   - Resource cleanup verification
   - Long-running operation monitoring

3. **Concurrent Operations**
   - Multi-user simulation
   - Database connection pooling
   - Cache performance under load

4. **Error Handling Performance**
   - Exception handling overhead
   - Recovery time measurement
   - Circuit breaker performance

#### Running Performance Tests

```bash
# Local performance testing
pytest tests/test_performance.py -v

# With memory profiling
pytest tests/test_performance.py --profile-mem

# Benchmark comparison
pytest tests/test_performance.py --benchmark-compare

# CI performance testing
make test-performance
```

### Load Testing with Locust

The performance pipeline includes Locust-based load testing:

```python
# Example load test scenario
class UserBehavior(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # User authentication
        pass
    
    @task(3)
    def analytics_query(self):
        # Simulate analytics requests
        pass
    
    @task(1)  
    def subscription_check(self):
        # Simulate subscription verification
        pass
```

## 🔒 Security Testing

### Automated Security Scans

#### 1. Secrets Detection (Gitleaks)
```yaml
# .gitleaks.toml configuration
[rules]
  description = "Generic API Key"
  regex = '''[a-zA-Z0-9_-]*[A-Z][a-zA-Z0-9_-]*'''
  tags = ["key", "API", "generic"]
```

#### 2. Dependency Vulnerability Scanning
- **Safety**: Python package vulnerabilities
- **Trivy**: Container and dependency scanning
- **Snyk**: Advanced vulnerability detection

#### 3. Static Application Security Testing (SAST)
- **CodeQL**: GitHub's semantic analysis
- **Bandit**: Python-specific security linting
- **Semgrep**: Custom security rule enforcement

### Security Testing Checklist
- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection in frontend
- [ ] Authentication/authorization checks
- [ ] Secure headers configuration
- [ ] HTTPS enforcement
- [ ] Rate limiting configured

## 🛠️ Local Development Testing

### Quick Test Commands

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_analytics_service.py -v

# Run tests with database
make test-db

# Frontend tests
cd twa-frontend && npm test

# Performance benchmarks
make test-performance

# Security scans
make security-scan
```

### Development Workflow

1. **Pre-commit Testing**
   ```bash
   # Run before committing
   make pre-commit
   ```

2. **Branch Testing**
   ```bash
   # Test your feature branch
   make test-branch
   ```

3. **Integration Testing**
   ```bash
   # Full integration test
   docker-compose -f docker-compose.test.yml up --abort-on-container-exit
   ```

## 🔄 CI/CD Pipeline

### Quality Gates

#### 1. Code Quality Gates
- **Minimum Coverage**: 80% (configurable via labels)
- **Type Coverage**: 95% mypy success rate
- **Security Score**: No high/critical vulnerabilities
- **Performance Threshold**: <500ms p95 response time

#### 2. Test Gates
- All unit tests must pass
- Integration tests must pass
- Performance benchmarks within threshold
- Security scans show no critical issues

#### 3. Deployment Gates
- All quality gates passed
- Code review approved
- Security review completed (for sensitive changes)
- Performance impact assessed

### Pipeline Optimization

#### Parallel Execution
```yaml
# Jobs run in parallel where possible
jobs:
  test-backend:     # ~5 minutes
  test-frontend:    # ~3 minutes  
  security-scan:    # ~4 minutes
  performance-test: # ~8 minutes
# Total pipeline time: ~8 minutes (vs ~20 sequential)
```

#### Caching Strategy
- **Docker Layer Caching**: Build time reduction
- **Dependency Caching**: pip/npm cache
- **Test Result Caching**: Skip unchanged tests

## 🎛️ Quality Gates

### Configurable Thresholds

#### Coverage Labels
- `cov:27` - Minimum 27% coverage
- `cov:50` - Minimum 50% coverage  
- `cov:80` - Minimum 80% coverage

#### Performance Labels
- `performance` - Run full performance suite
- `performance:skip` - Skip performance tests

#### Security Labels
- `security-scan` - Full security scan
- `security:low` - Basic security checks only

### Gate Configuration

```yaml
# Example gate configuration in workflow
- name: Check Coverage Gate
  run: |
    COVERAGE_THRESHOLD=80
    if [[ "${{ contains(github.event.pull_request.labels.*.name, 'cov:50') }}" == "true" ]]; then
      COVERAGE_THRESHOLD=50
    elif [[ "${{ contains(github.event.pull_request.labels.*.name, 'cov:27') }}" == "true" ]]; then
      COVERAGE_THRESHOLD=27
    fi
    
    python -c "
    import xml.etree.ElementTree as ET
    tree = ET.parse('coverage.xml')
    coverage = float(tree.getroot().attrib['line-rate']) * 100
    if coverage < ${COVERAGE_THRESHOLD}:
        print(f'❌ Coverage {coverage:.1f}% below threshold {COVERAGE_THRESHOLD}%')
        exit(1)
    print(f'✅ Coverage {coverage:.1f}% meets threshold {COVERAGE_THRESHOLD}%')
    "
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. Test Failures

**Database Connection Issues**
```bash
# Check database service health
docker-compose ps
docker-compose logs postgres

# Reset test database
docker-compose down -v
docker-compose up -d postgres
```

**Import Errors**
```bash
# Ensure Python path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

#### 2. Performance Test Issues

**Baseline Missing**
```bash
# Generate new baseline
pytest tests/test_performance.py --benchmark-save=baseline
```

**Memory Profiling Errors**
```bash
# Install memory profiler
pip install memory-profiler psutil

# Run with memory profiling
pytest tests/test_performance.py --profile-mem
```

#### 3. Security Scan Issues

**False Positives**
```bash
# Update security scan configuration
# Edit .github/workflows/security-enhanced.yml
# Add exceptions to scanning tools
```

**Dependency Vulnerabilities**
```bash
# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Check for security updates
safety check
```

#### 4. Frontend Test Issues

**Node Version Conflicts**
```bash
# Use correct Node version
nvm use 18
cd twa-frontend
npm install
npm test
```

**Build Failures**
```bash
# Clear cache and rebuild
cd twa-frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Getting Help

1. **Check Workflow Logs**: Review failed job details in GitHub Actions
2. **Local Reproduction**: Run the same commands locally
3. **Environment Verification**: Ensure all dependencies are installed
4. **Configuration Review**: Verify environment variables and settings

### Performance Debugging

```bash
# Profile specific functions
python -m cProfile -s cumtime bot/services/analytics_service.py

# Memory usage monitoring
python -m memory_profiler bot/services/guard_service.py

# Database query analysis
export LOG_LEVEL=DEBUG
pytest tests/test_repositories.py -v -s
```

---

## 📊 Testing Metrics

### Current Coverage
- **Backend Coverage**: ~85%
- **Frontend Coverage**: ~75%
- **Integration Coverage**: ~90%
- **Security Coverage**: 100% (all files scanned)

### Performance Baselines
- **API Response Time**: <200ms p95
- **Database Queries**: <50ms average
- **Memory Usage**: <512MB under normal load
- **Concurrent Users**: 1000+ supported

### Security Metrics
- **Dependencies Scanned**: 100%
- **SAST Coverage**: 100%
- **Secret Detection**: Active
- **Vulnerability Patches**: <24h SLA

---

This testing infrastructure ensures high-quality, secure, and performant code through comprehensive automated testing and quality assurance processes.
