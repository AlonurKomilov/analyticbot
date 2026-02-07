"""
AI System Example Usage
=======================

Demonstrates how to use both System AI and User AI
"""

import asyncio
import logging

from apps.ai.shared.models import DecisionType, WorkerType

# System AI imports
from apps.ai.system import SystemAIController, get_system_ai_config

# User AI imports
from apps.ai.user import UserAIAgent, UserAIConfig
from apps.ai.user.marketplace import MarketplaceServiceRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ====================
# SYSTEM AI EXAMPLES
# ====================


async def example_system_ai_basic():
    """Basic System AI usage example"""
    logger.info("=" * 60)
    logger.info("Example 1: System AI Controller - Basic Usage")
    logger.info("=" * 60)

    # Load config from environment
    config = get_system_ai_config()

    # Initialize controller with config
    controller = SystemAIController(config)

    # Start monitoring
    await controller.start()

    # Wait a bit for discovery
    await asyncio.sleep(2)

    # Check status
    status = await controller.get_status()
    logger.info("\n📊 System AI Status:")
    logger.info(f"   Running: {status['is_running']}")
    logger.info(f"   Mode: {status['approval_mode']}")
    logger.info(f"   Workers: {status['registry_stats']['total_workers']}")
    logger.info(f"   AI Manageable: {status['registry_stats']['ai_manageable_workers']}")

    # List discovered workers
    workers = await controller.registry.list_workers()
    logger.info("\n🔍 Discovered Workers:")
    for worker in workers:
        logger.info(f"   - {worker.name} ({worker.worker_type.value})")
        logger.info(f"     AI Manageable: {worker.ai_manageable}")

    # Stop controller
    await controller.stop()


async def example_system_ai_decision():
    """Example of System AI making a decision"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: System AI - Making Decisions")
    logger.info("=" * 60)

    config = get_system_ai_config()
    controller = SystemAIController(config)
    await controller.start()

    await asyncio.sleep(1)

    # Make a scale-up decision
    decision = await controller.make_decision(
        decision_type=DecisionType.SCALE,
        target_worker="mtproto_worker",
        action="scale_up",
        params={"instances": 2, "reason": "high_load"},
        reasoning="CPU usage exceeded 85% threshold for 10 minutes",
        risk_level="low",
        impact="Improved performance, slightly higher resource cost",
        confidence=0.9,
    )

    if decision:
        logger.info("\n✅ Decision Created:")
        logger.info(f"   ID: {decision.decision_id}")
        logger.info(f"   Type: {decision.decision_type.value}")
        logger.info(f"   Action: {decision.action}")
        logger.info(f"   Approval Level: {decision.approval_level.value}")
        logger.info(f"   Approved: {decision.approved}")

        # If auto-approved, execute it
        if decision.approved:
            logger.info("\n⚙️  Executing decision (dry run)...")
            result = await controller.execute_decision(decision)
            if result:
                logger.info(f"   Result: {result.message}")

    await controller.stop()


async def example_system_ai_workers():
    """Example of filtering workers"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: System AI - Worker Management")
    logger.info("=" * 60)

    controller = SystemAIController()
    await controller.start()

    await asyncio.sleep(1)

    registry = controller.registry

    # Get only MTProto workers
    mtproto_workers = await registry.list_workers(worker_type=WorkerType.MTPROTO)
    logger.info(f"\n📡 MTProto Workers: {len(mtproto_workers)}")
    for w in mtproto_workers:
        logger.info(f"   - {w.name}: {w.description}")

    # Get only API workers
    api_workers = await registry.list_workers(worker_type=WorkerType.API)
    logger.info(f"\n🌐 API Workers: {len(api_workers)}")
    for w in api_workers:
        logger.info(f"   - {w.name}: {w.description}")

    # Get AI-manageable workers only
    ai_manageable = await registry.list_workers(ai_manageable_only=True)
    logger.info(f"\n🤖 AI-Manageable Workers: {len(ai_manageable)}")
    for w in ai_manageable:
        logger.info(f"   - {w.name}")

    await controller.stop()


# ====================
# USER AI EXAMPLES
# ====================


async def example_user_ai_basic():
    """Basic User AI usage example"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: User AI - Basic Usage")
    logger.info("=" * 60)

    # Load user config (from database in production)
    user_id = 12345
    config = await UserAIConfig.from_database(user_id)

    # Create user agent
    agent = UserAIAgent(config)

    # Get agent status
    status = await agent.get_status()
    logger.info("\n👤 User AI Status:")
    logger.info(f"   User ID: {status['user_id']}")
    logger.info(f"   Tier: {status['tier']}")
    logger.info(f"   Features: {status['enabled_features']}")
    logger.info(
        f"   Usage Today: {status['usage']['requests_today']}/{status['usage']['limits']['daily']}"
    )


async def example_user_ai_analytics():
    """User AI analytics example"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: User AI - Analytics Insights")
    logger.info("=" * 60)

    user_id = 12345
    config = await UserAIConfig.from_database(user_id)
    agent = UserAIAgent(config)

    # Analyze a channel
    channel_id = 67890
    result = await agent.analyze_channel(
        channel_id=channel_id,
        analysis_type="overview",
        period_days=30,
    )

    logger.info("\n📊 Analytics Result:")
    logger.info(f"   Success: {result['success']}")
    if result["success"]:
        logger.info(f"   Channel: {result['channel_id']}")
        logger.info(f"   Period: {result['period_days']} days")
        logger.info(f"   Generated: {result['generated_at']}")


async def example_user_ai_content():
    """User AI content generation example"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 6: User AI - Content Suggestions")
    logger.info("=" * 60)

    user_id = 12345
    config = await UserAIConfig.from_database(user_id)
    agent = UserAIAgent(config)

    # Get content suggestions
    result = await agent.suggest_content(
        channel_id=67890,
        topic="cryptocurrency",
        content_type="post",
        count=3,
    )

    logger.info("\n💡 Content Suggestions:")
    logger.info(f"   Success: {result['success']}")
    if result["success"]:
        for suggestion in result["suggestions"]:
            logger.info(f"   - {suggestion['title']}")


async def example_marketplace_services():
    """Marketplace services example"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 7: Marketplace Service Integration")
    logger.info("=" * 60)

    # Get registry
    registry = MarketplaceServiceRegistry()

    # List available services
    stats = registry.get_stats()
    logger.info("\n🏪 Marketplace Stats:")
    logger.info(f"   Total Services: {stats['total_services']}")
    logger.info(f"   Free Services: {stats['free_services']}")
    logger.info(f"   Capabilities: {stats['capabilities_available']}")

    # List all services
    services = registry.list_all()
    logger.info("\n📦 Available Services:")
    for service in services:
        logger.info(f"   - {service.name} (v{service.version})")
        logger.info(f"     {service.description}")
        logger.info(f"     Tier: {service.required_tier}")


async def example_registry_stats():
    """Example of getting registry statistics"""
    logger.info("\n" + "=" * 60)
    logger.info("Example 8: System AI - Registry Statistics")
    logger.info("=" * 60)

    controller = SystemAIController()
    await controller.start()

    await asyncio.sleep(1)

    stats = await controller.registry.get_registry_stats()

    logger.info("\n📊 Registry Statistics:")
    logger.info(f"   Total Workers: {stats['total_workers']}")
    logger.info(f"   AI Manageable: {stats['ai_manageable_workers']}")
    logger.info(f"   Auto-scaling Enabled: {stats['auto_scaling_enabled']}")

    logger.info("\n   Worker Types:")
    for worker_type, count in stats["type_counts"].items():
        logger.info(f"     {worker_type}: {count}")

    await controller.stop()


async def main():
    """Run all examples"""
    try:
        # System AI examples
        await example_system_ai_basic()
        await asyncio.sleep(1)

        await example_system_ai_decision()
        await asyncio.sleep(1)

        await example_system_ai_workers()
        await asyncio.sleep(1)

        # User AI examples
        await example_user_ai_basic()
        await asyncio.sleep(1)

        await example_user_ai_analytics()
        await asyncio.sleep(1)

        await example_user_ai_content()
        await asyncio.sleep(1)

        # Marketplace examples
        await example_marketplace_services()
        await asyncio.sleep(1)

        # Stats
        await example_registry_stats()

        logger.info("\n" + "=" * 60)
        logger.info("✅ All examples completed successfully!")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
