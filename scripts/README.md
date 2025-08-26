# 🛠️ Scripts Directory

This directory contains utility scripts, demos, and test runners for AnalyticBot.

## 📋 **Available Scripts**

### 🧪 **Test Runners**
- **`run_infrastructure_tests.py`** - Database performance and infrastructure tests
  ```bash
  python scripts/run_infrastructure_tests.py
  ```

- **`run_phase25_tests.py`** - Phase 2.5 AI/ML enhancement test suite
  ```bash
  python scripts/run_phase25_tests.py
  ```

### 🎯 **Demos & Examples**
- **`demo_celery_usage.py`** - Celery task execution examples
  ```bash
  python scripts/demo_celery_usage.py
  ```

## 🚀 **Usage**

Run scripts from the project root:
```bash
# Make sure dependencies are installed
pip install -r requirements.txt

# Run any script
python scripts/[script_name].py
```

## ⚙️ **Environment**

Scripts use the same environment configuration as the main application:
- Copy `.env.example` to `.env` and configure
- Ensure database and Redis are running if needed
