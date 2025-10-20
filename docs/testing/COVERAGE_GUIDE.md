# Test Coverage Guide

**Created:** October 20, 2025  
**Status:** Active  
**Current Coverage:** 17%  
**Goal:** 25%+ by end of Week 1

---

## 📊 Overview

Test coverage tracking is now fully configured for the AnalyticBot project. Coverage is measured across three main layers:

- **apps/** - Application layer (APIs, bots, jobs)
- **core/** - Core domain logic and services
- **infra/** - Infrastructure (database, cache, external services)

---

## 🚀 Quick Start

### Run Tests with Coverage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests with coverage
PYTHONPATH=. pytest

# Run specific test file with coverage
PYTHONPATH=. pytest apps/tests/test_api/test_main.py

# Run tests without coverage (faster)
PYTHONPATH=. pytest --no-cov
```

### View Coverage Reports

```bash
# Generate comprehensive coverage report
./scripts/coverage_report.sh

# Open HTML report in browser
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS

# Check coverage thresholds
./scripts/check_coverage.py
```

---

## 📈 Current Coverage (Baseline)

**Overall:** 17% (13,636 statements, 10,890 missing)

### By Layer

| Layer | Coverage | Priority |
|-------|----------|----------|
| **apps/** | ~17% | HIGH - Focus area |
| **core/** | ~15% | MEDIUM |
| **infra/** | ~20% | LOW |

### Critical Files Status

| File | Coverage | Target | Priority |
|------|----------|--------|----------|
| `apps/api/middleware/auth.py` | 25% | 60%+ | 🔴 **Very High** |
| `apps/api/auth_utils.py` | 41% | 70%+ | 🔴 **High** |
| `apps/api/di_analytics.py` | 13% | 40%+ | 🔴 **High** |
| `apps/api/main.py` | 65% | 80%+ | 🟡 **Medium** |

---

## 🎯 Coverage Goals

### Week 1 (Days 2-7)

- **Day 2:** Configure coverage tracking ✅
- **Days 3-4:** Payment system tests (→70% payment coverage)
- **Days 5-7:** Integration tests
- **End of Week 1:** **17% → 25%+ overall**

### Week 2-3

- Authentication & Security: 25% → 60%+
- Payment Flows: Current → 70%+
- API Endpoints: 30% → 60%+
- **End of Week 3:** **25% → 40%+**

---

## 📋 Configuration Files

### pytest.ini

Main pytest configuration with coverage enabled:

```ini
[pytest]
addopts =
    --cov=apps
    --cov=core
    --cov=infra
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=json:coverage.json
    --cov-fail-under=15
    --cov-branch
```

### .coveragerc

Detailed coverage.py configuration:

- **Source:** apps, core, infra
- **Omit:** Tests, migrations, archives, frontend
- **Branch coverage:** Enabled
- **Reports:** HTML, JSON, Terminal

---

## 🛠️ Tools & Scripts

### scripts/coverage_report.sh

Comprehensive coverage report generator with:
- Color-coded terminal output
- HTML report generation
- JSON export for CI/CD
- Top 5 best/worst covered files
- Coverage highlights and trends

### scripts/check_coverage.py

Quick coverage threshold checker:
- Overall coverage validation (≥15%)
- Critical file checks
- Exit codes for CI/CD pipelines
- Detailed failure messages

---

## 📊 Report Types

### 1. Terminal Report

```bash
PYTHONPATH=. pytest --cov-report=term-missing
```

- Quick overview during development
- Shows missing line numbers
- Skips fully covered files

### 2. HTML Report

```bash
xdg-open htmlcov/index.html
```

- Interactive browsing
- Line-by-line coverage visualization
- File tree navigation
- Coverage trends

### 3. JSON Report

```bash
cat coverage.json | jq '.totals'
```

- Machine-readable format
- CI/CD integration
- Trend analysis
- Automated reporting

---

## 🎨 Best Practices

### Writing Testable Code

```python
# ✅ Good: Dependency injection, easy to mock
def process_payment(payment_service: PaymentService, amount: float):
    return payment_service.charge(amount)

# ❌ Bad: Hard-coded dependencies
def process_payment(amount: float):
    service = StripePaymentService()  # Hard to test
    return service.charge(amount)
```

### Test Organization

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Service integration tests
├── e2e/            # End-to-end critical paths
└── fixtures/       # Shared test fixtures
```

### Coverage Markers

```python
# Skip coverage for specific lines
def debug_only_function():  # pragma: no cover
    print("Debug info")

# Skip abstract methods
@abstractmethod
def interface_method(self):
    raise NotImplementedError  # Excluded by default
```

---

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run tests with coverage
  run: |
    source .venv/bin/activate
    PYTHONPATH=. pytest
    
- name: Check coverage thresholds
  run: |
    python scripts/check_coverage.py
    
- name: Upload coverage report
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.json
```

---

## 📝 Coverage Thresholds

### Current (Oct 20, 2025)

- **Overall:** ≥15% (baseline established)
- **Critical auth files:** ≥30%
- **New code:** ≥60% (aspirational)

### Progressive Targets

| Week | Overall | Auth/Security | Payment | API |
|------|---------|---------------|---------|-----|
| 1    | 17%→25% | 25%→40%      | 30%→70% | 30%→45% |
| 2    | 25%→32% | 40%→55%      | 70%→75% | 45%→60% |
| 3    | 32%→40% | 55%→70%      | 75%→80% | 60%→70% |

---

## 🔍 Finding Gaps

### Identify Untested Code

```bash
# Find files with <20% coverage
python << 'EOF'
import json
with open("coverage.json") as f:
    data = json.load(f)
for file, stats in data["files"].items():
    cov = stats["summary"]["percent_covered"]
    if cov < 20 and "test" not in file:
        print(f"{cov:5.1f}% - {file}")
EOF
```

### Branch Coverage Gaps

```bash
# Find untested branches
PYTHONPATH=. pytest --cov-report=term-missing | grep "branch"
```

---

## 📚 Resources

### Internal Docs

- [Test Infrastructure](./TEST_INFRASTRUCTURE.md)
- [Fixture Guide](./FIXTURES_GUIDE.md)
- [Pylance Errors Analysis](./PYLANCE_ERRORS_ANALYSIS.md)

### External Resources

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py guide](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## 🎯 Next Steps

1. ✅ **Coverage tracking configured** (Oct 20, 2025)
2. **Payment system tests** (Days 3-4) - Target: 70% payment coverage
3. **Integration tests** (Days 5-7) - Target: 25%+ overall
4. **Continuous improvement** (Week 2+) - Target: 40%+ overall

---

**Last Updated:** October 20, 2025  
**Maintainer:** Development Team  
**Questions?** See [Testing FAQ](./TESTING_FAQ.md)
