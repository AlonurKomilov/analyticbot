# Quick Migration Guide - Celery Architecture Fix

**For Developers & DevOps Teams**

---

## What Changed?

Celery application was moved from infrastructure layer to application layer to comply with Clean Architecture principles.

### Import Paths

| What | Old Path | New Path | Status |
|------|----------|----------|--------|
| Celery App | `infra.celery.celery_app` | `apps.celery.celery_app` | ✅ Updated |
| Monitoring | `apps.bot.utils.monitoring` | `apps.shared.monitoring` | ✅ Updated (backward compat) |
| Tasks | `apps.bot.tasks` | `apps.celery.tasks.bot_tasks` | ✅ Updated |

### Commands

| Task | Old Command | New Command |
|------|-------------|-------------|
| Worker | `celery -A infra.celery.celery_app worker` | `celery -A apps.celery.celery_app worker` |
| Beat | `celery -A infra.celery.celery_app beat` | `celery -A apps.celery.celery_app beat` |
| Flower | `celery -A infra.celery.celery_app flower` | `celery -A apps.celery.celery_app flower` |

---

## Developer Guide

### Importing Celery App

```python
# ❌ Old way (deprecated)
from infra.celery.celery_app import celery_app

# ✅ New way
from apps.celery.celery_app import celery_app
```

### Importing Monitoring Utilities

```python
# ⚠️ Old way (still works with deprecation warning)
from apps.bot.utils.monitoring import metrics, health_monitor

# ✅ New way
from apps.shared.monitoring import metrics, health_monitor
```

### Creating New Celery Tasks

Tasks should now be placed in `apps/celery/tasks/`:

```python
# apps/celery/tasks/my_tasks.py
from apps.celery.celery_app import celery_app

@celery_app.task(bind=True, name="apps.celery.tasks.my_tasks.my_new_task")
def my_new_task(self, arg1, arg2):
    """Your task implementation"""
    pass
```

Then update `apps/celery/celery_app.py`:
```python
celery_app = Celery(
    "analyticbot_tasks",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
    include=[
        "apps.celery.tasks.bot_tasks",
        "apps.celery.tasks.my_tasks",  # Add your module
    ],
)
```

---

## DevOps Guide

### Docker Compose

Already updated in `docker/docker-compose.yml`. No action needed.

```yaml
# Worker service
command: celery -A apps.celery.celery_app worker -l info

# Beat service
command: celery -A apps.celery.celery_app beat -l info
```

### Dockerfile

Already updated in `docker/Dockerfile`. No action needed.

```dockerfile
CMD ["/entrypoint.sh", "celery", "-A", "apps.celery.celery_app", "worker", ...]
```

### Kubernetes

Already updated in `infra/k8s/celery-deployment.yaml`. No action needed.

```yaml
command: ["celery", "-A", "apps.celery.celery_app", "worker", ...]
```

### Deployment Steps

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Rebuild Docker images:**
   ```bash
   docker-compose -f docker/docker-compose.yml build worker beat
   ```

3. **Rolling update (K8s):**
   ```bash
   kubectl apply -f infra/k8s/celery-deployment.yaml
   kubectl rollout status deployment/celery-worker -n analyticbot
   kubectl rollout status deployment/celery-beat -n analyticbot
   ```

4. **Verify health:**
   ```bash
   # Docker
   docker-compose -f docker/docker-compose.yml exec worker celery -A apps.celery.celery_app inspect ping

   # K8s
   kubectl exec -it deployment/celery-worker -n analyticbot -- celery -A apps.celery.celery_app inspect ping
   ```

---

## CI/CD Updates

### GitHub Actions / GitLab CI

Update any CI/CD pipelines that reference Celery:

```yaml
# ❌ Old
script:
  - celery -A infra.celery.celery_app worker --loglevel=info

# ✅ New
script:
  - celery -A apps.celery.celery_app worker --loglevel=info
```

### Testing

Update test commands:

```yaml
# ❌ Old
test:
  script:
    - pytest tests/ -k celery
    - celery -A infra.celery.celery_app inspect ping

# ✅ New
test:
  script:
    - pytest tests/ -k celery
    - celery -A apps.celery.celery_app inspect ping
```

---

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'infra.celery'

**Cause:** Using old import path
**Solution:** Update to `from apps.celery.celery_app import celery_app`

### Issue: Task not found

**Cause:** Task path changed
**Solution:** Use full task path: `apps.celery.tasks.bot_tasks.task_name`

### Issue: Monitoring import deprecation warning

**Cause:** Using old monitoring import
**Solution:** Update to `from apps.shared.monitoring import ...`

### Issue: Docker container fails to start

**Cause:** Using old Celery path in docker-compose.yml
**Solution:** Update command to use `apps.celery.celery_app`

### Issue: K8s pod CrashLoopBackOff

**Cause:** Using old Celery path in K8s manifest
**Solution:** Update deployment manifest and apply changes

---

## Rollback Plan

If issues occur, you can temporarily rollback:

1. **Revert code changes:**
   ```bash
   git revert <commit-hash>
   ```

2. **Rebuild images:**
   ```bash
   docker-compose build worker beat
   ```

3. **Redeploy:**
   ```bash
   kubectl rollout undo deployment/celery-worker -n analyticbot
   kubectl rollout undo deployment/celery-beat -n analyticbot
   ```

**Note:** Old files are still present as backup:
- `infra/celery/celery_app.py` (will be removed after validation)
- `apps/bot/tasks.py` (will be removed after validation)

---

## Validation Checklist

- [ ] Pull latest code
- [ ] Review changes in this guide
- [ ] Update local scripts/aliases
- [ ] Rebuild Docker images
- [ ] Test locally: `docker-compose up worker beat`
- [ ] Verify tasks execute: `celery -A apps.celery.celery_app inspect active`
- [ ] Check monitoring: `celery -A apps.celery.celery_app inspect ping`
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Monitor for errors (first 24h)
- [ ] Update team documentation

---

## Support

**Questions?** Contact the architecture team or check:
- 📄 `docs/audits/COMPLETE_ARCHITECTURE_FIX_SUMMARY.md`
- 📄 `docs/audits/CELERY_ARCHITECTURE_AUDIT.md`
- 📄 `docs/audits/PHASE_7_COMPLETION_REPORT.md`

**Found an issue?** Create a ticket with:
- Error message
- Steps to reproduce
- Environment (local/staging/prod)
- Docker/K8s logs
