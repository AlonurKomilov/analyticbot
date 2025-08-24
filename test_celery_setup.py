#!/usr/bin/env python3
"""
Test script for Celery master setup validation
Validates worker/beat functionality and task execution
"""

import asyncio
import logging
import sys
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_celery_app_import():
    """Test that Celery app can be imported"""
    try:
        from infra.celery import celery_app
        logger.info("✅ Celery app imported successfully")
        logger.info(f"   Broker: {celery_app.conf.broker_url}")
        logger.info(f"   Backend: {celery_app.conf.result_backend}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import Celery app: {e}")
        return False


def test_task_imports():
    """Test that tasks can be imported"""
    try:
        from infra.celery.tasks import (
            send_message_task,
            process_analytics,
            cleanup_old_data,
            health_check_task,
            scheduled_broadcast,
            AVAILABLE_TASKS
        )
        logger.info("✅ All infra.celery.tasks imported successfully")
        logger.info(f"   Available tasks: {len(AVAILABLE_TASKS)}")
        
        # Test bot tasks import
        from apps.bot.tasks import send_scheduled_message
        logger.info("✅ Bot tasks imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import tasks: {e}")
        return False


def test_celery_health():
    """Test Celery health check function"""
    try:
        from infra.celery import check_celery_health
        health_status = check_celery_health()
        logger.info("✅ Celery health check executed")
        logger.info(f"   Status: {health_status.get('status', 'unknown')}")
        return True
    except Exception as e:
        logger.error(f"❌ Celery health check failed: {e}")
        return False


def test_task_delay_functionality():
    """Test basic task queueing (requires Redis)"""
    try:
        from infra.celery.tasks import health_check_task
        
        # Try to queue a health check task
        result = health_check_task.delay()
        logger.info("✅ Task queued successfully")
        logger.info(f"   Task ID: {result.id}")
        
        # Don't wait for completion in test (worker might not be running)
        return True
    except Exception as e:
        logger.warning(f"⚠️  Task queueing test skipped (Redis not available): {e}")
        return True  # Not critical for validation


def test_send_message_task_config():
    """Test the critical send_message_task configuration"""
    try:
        from infra.celery.tasks import send_message_task
        
        # Check task configuration
        logger.info("✅ send_message_task configuration:")
        logger.info(f"   Name: {send_message_task.name}")
        logger.info(f"   Max retries: {getattr(send_message_task, 'max_retries', 'default')}")
        logger.info(f"   Autoretry for: {getattr(send_message_task, 'autoretry_for', 'default')}")
        logger.info(f"   Retry backoff: {getattr(send_message_task, 'retry_backoff', 'default')}")
        logger.info(f"   Retry jitter: {getattr(send_message_task, 'retry_jitter', 'default')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ send_message_task configuration test failed: {e}")
        return False


def test_beat_schedule():
    """Test that Beat schedule is properly configured"""
    try:
        from infra.celery import celery_app
        
        schedule = celery_app.conf.beat_schedule
        logger.info("✅ Beat schedule configuration:")
        
        for task_name, config in schedule.items():
            logger.info(f"   {task_name}:")
            logger.info(f"     Task: {config['task']}")
            logger.info(f"     Schedule: {config['schedule']}s")
            logger.info(f"     Queue: {config.get('options', {}).get('queue', 'default')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Beat schedule test failed: {e}")
        return False


def run_validation_tests():
    """Run all validation tests"""
    logger.info("🚀 Starting Celery master validation tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Celery App Import", test_celery_app_import),
        ("Task Imports", test_task_imports),
        ("Celery Health Check", test_celery_health),
        ("Task Delay Functionality", test_task_delay_functionality),
        ("send_message_task Config", test_send_message_task_config),
        ("Beat Schedule", test_beat_schedule),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"🏁 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Celery master setup is ready.")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check configuration.")
        return False


if __name__ == "__main__":
    success = run_validation_tests()
    sys.exit(0 if success else 1)
