#!/usr/bin/env python3
"""
Usage example for the new Celery master with send_message_task
Demonstrates how to use the critical message sending functionality
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_send_message_task():
    """
    Demonstrate the critical send_message_task usage with retry/backoff
    """
    try:
        from infra.celery.tasks import send_message_task
        
        logger.info("🚀 Demonstrating send_message_task usage")
        
        # Example 1: Basic message sending
        logger.info("📨 Example 1: Basic message to channel")
        result = send_message_task.delay(
            chat_id="-1001234567890",  # Example channel ID
            message="Hello from AnalyticBot! This is a test message."
        )
        logger.info(f"   Task queued with ID: {result.id}")
        
        # Example 2: Message with additional parameters
        logger.info("📨 Example 2: Message with parse mode")
        result = send_message_task.delay(
            chat_id="-1001234567890",
            message="*Bold text* and _italic text_",
            parse_mode="Markdown"
        )
        logger.info(f"   Task queued with ID: {result.id}")
        
        # Example 3: Scheduled message using apply_async
        logger.info("📨 Example 3: Delayed message (5 seconds)")
        result = send_message_task.apply_async(
            args=["-1001234567890", "This message is delayed by 5 seconds"],
            countdown=5  # Send in 5 seconds
        )
        logger.info(f"   Delayed task queued with ID: {result.id}")
        
        # Example 4: Retry configuration demonstration
        logger.info("🔄 Task retry configuration:")
        logger.info(f"   Max retries: {send_message_task.max_retries}")
        logger.info(f"   Retry backoff: {send_message_task.retry_backoff}")
        logger.info(f"   Retry jitter: {send_message_task.retry_jitter}")
        logger.info(f"   Autoretry for: {send_message_task.autoretry_for}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        return False


def demonstrate_analytics_task():
    """
    Demonstrate analytics processing task usage
    """
    try:
        from infra.celery.tasks import process_analytics
        
        logger.info("📊 Demonstrating analytics task usage")
        
        # Process analytics for a channel
        result = process_analytics.delay(
            channel_id="-1001234567890"
        )
        logger.info(f"   Analytics task queued with ID: {result.id}")
        
        # Process analytics for specific post
        result = process_analytics.delay(
            channel_id="-1001234567890",
            post_id="123"
        )
        logger.info(f"   Post analytics task queued with ID: {result.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Analytics demonstration failed: {e}")
        return False


def demonstrate_scheduled_broadcast():
    """
    Demonstrate scheduled broadcast functionality
    """
    try:
        from infra.celery.tasks import scheduled_broadcast
        
        logger.info("📢 Demonstrating scheduled broadcast")
        
        # Broadcast to multiple channels
        result = scheduled_broadcast.delay(
            message="📊 Weekly Analytics Report is ready!",
            target_channels=["-1001111111111", "-1002222222222", "-1003333333333"],
            schedule_time=datetime.utcnow().isoformat()
        )
        logger.info(f"   Broadcast task queued with ID: {result.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Broadcast demonstration failed: {e}")
        return False


def show_celery_beat_schedule():
    """
    Show the configured Celery Beat schedule
    """
    try:
        from infra.celery import celery_app
        
        logger.info("⏰ Celery Beat Schedule:")
        schedule = celery_app.conf.beat_schedule
        
        for task_name, config in schedule.items():
            logger.info(f"   {task_name}:")
            logger.info(f"     Task: {config['task']}")
            logger.info(f"     Interval: {config['schedule']} seconds")
            logger.info(f"     Queue: {config.get('options', {}).get('queue', 'default')}")
            
            # Convert seconds to human readable
            seconds = config['schedule']
            if seconds >= 3600:
                logger.info(f"     Human: Every {seconds/3600:.1f} hour(s)")
            elif seconds >= 60:
                logger.info(f"     Human: Every {seconds/60:.1f} minute(s)")
            else:
                logger.info(f"     Human: Every {seconds} second(s)")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Beat schedule demonstration failed: {e}")
        return False


def main():
    """
    Run all demonstrations
    """
    logger.info("🎯 AnalyticBot Celery Master - Usage Demonstration")
    logger.info("=" * 60)
    
    demonstrations = [
        ("Send Message Task", demonstrate_send_message_task),
        ("Analytics Task", demonstrate_analytics_task), 
        ("Scheduled Broadcast", demonstrate_scheduled_broadcast),
        ("Beat Schedule", show_celery_beat_schedule),
    ]
    
    for demo_name, demo_func in demonstrations:
        logger.info(f"\n🎬 {demo_name}")
        try:
            demo_func()
        except Exception as e:
            logger.error(f"❌ {demo_name} failed: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Demonstration completed!")
    logger.info("\n💡 To run with Redis and see actual task execution:")
    logger.info("   docker compose up -d redis")
    logger.info("   celery -A infra.celery.celery_app worker --loglevel=info")
    logger.info("   celery -A infra.celery.celery_app beat --loglevel=info")


if __name__ == "__main__":
    main()
