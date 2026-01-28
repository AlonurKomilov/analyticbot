"""
User AI Agent
=============

Per-user AI agent for analytics, content, and service integration.
Unlike System AI (infrastructure), User AI handles:
- Analytics insights and recommendations
- Content suggestions
- Audience analysis
- Marketplace service integration

Multi-Provider Support:
- Uses user's configured AI provider (OpenAI, Claude, Gemini, etc.)
- Falls back to system provider if user hasn't configured one
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from apps.ai.shared.models import Action, ActionType
from apps.ai.user.config import AIFeature, UserAIConfig
from core.repositories.user_ai_providers_repository import UserAIProvidersRepository
from core.repositories.user_ai_usage_repository import UserAIUsageRepository
from core.services.ai.base_provider import BaseAIProvider
from core.services.ai.models import AIMessage, AIProviderConfig
from core.services.ai.provider_registry import AIProviderRegistry

logger = logging.getLogger(__name__)


class UserAIAgent:
    """
    Per-user AI agent for analytics and service integration.

    Features:
    - Channel analytics insights
    - Content recommendations
    - Audience analysis
    - Competitor tracking
    - Marketplace service integration

    Usage:
        config = await UserAIConfig.from_database(user_id)
        agent = UserAIAgent(config)

        # Get analytics insights
        insights = await agent.analyze_channel(channel_id)

        # Get content suggestions
        suggestions = await agent.suggest_content(channel_id, topic="crypto")
    """

    def __init__(
        self,
        config: UserAIConfig,
        providers_repo: UserAIProvidersRepository | None = None,
        usage_repo: UserAIUsageRepository | None = None,
    ):
        self.config = config
        self.user_id = config.user_id
        self.providers_repo = providers_repo
        self.usage_repo = usage_repo

        # Action history for this session
        self.actions: list[Action] = []

        logger.info(
            f"🤖 User AI Agent initialized for user {self.user_id} (tier: {config.tier.value})"
        )

    async def _get_ai_provider(self) -> BaseAIProvider:
        """
        Get user's configured AI provider or fallback to system provider.

        Returns:
            Configured AI provider instance
        """
        # Try to get user's configured provider
        if self.providers_repo:
            try:
                user_provider = await self.providers_repo.get_default_provider(
                    user_id=self.user_id,
                    decrypt_key=True,
                )

                if user_provider:
                    # User has their own API key
                    provider_name = user_provider["provider_name"]
                    api_key = user_provider["api_key"]
                    model = user_provider["model_preference"]

                    logger.info(f"Using user's {provider_name} provider with model {model}")

                    # Get provider class and create instance
                    provider_class = AIProviderRegistry.get_provider_class(provider_name)
                    config = AIProviderConfig(
                        api_key=api_key,
                        model=model,
                        temperature=self.config.settings.temperature,
                        max_tokens=self.config.limits.max_tokens_per_request,
                    )

                    return provider_class(config)
            except Exception as e:
                logger.warning(
                    f"Failed to load user provider for user {self.user_id}: {e}. "
                    f"Falling back to system provider"
                )

        # Fallback to system provider (platform-provided API key)
        # TODO: Load from system config
        # For now, raise error - system provider not configured yet
        raise ValueError(
            "No AI provider configured. Please add your API key in settings or contact support."
        )

    async def _track_ai_usage(
        self,
        provider_name: str,
        tokens_used: int,
        cost_usd: float,
    ) -> None:
        """Track AI usage and update spending."""
        if self.usage_repo:
            try:
                # Track in usage repository
                await self.usage_repo.increment_usage(
                    user_id=self.user_id,
                    tokens=tokens_used,
                    cost=cost_usd,
                )

                # Update provider spending
                if self.providers_repo:
                    await self.providers_repo.update_spending(
                        user_id=self.user_id,
                        provider_name=provider_name,
                        cost_usd=Decimal(str(cost_usd)),
                        tokens_used=tokens_used,
                    )

                logger.info(
                    f"Tracked usage: {tokens_used} tokens, ${cost_usd:.4f} for user {self.user_id}"
                )
            except Exception as e:
                logger.error(f"Failed to track AI usage: {e}")

    async def analyze_channel(
        self,
        channel_id: int,
        analysis_type: str = "overview",
        period_days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze a Telegram channel and provide AI insights.

        Args:
            channel_id: The channel to analyze
            analysis_type: Type of analysis (overview, engagement, growth, content)
            period_days: Number of days to analyze

        Returns:
            Dictionary with analysis results and AI insights
        """
        # Check permissions
        if not self.config.can_use_feature(AIFeature.ANALYTICS_INSIGHTS):
            return {
                "success": False,
                "error": "Analytics insights not enabled for your account",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            # Track usage
            self.config.increment_usage()

            # Create action for tracking
            action = Action(
                action_id=f"user_ai_{datetime.utcnow().timestamp()}",
                action_type=ActionType.ANALYZE,
                target_worker="user_analytics",
                parameters={
                    "channel_id": channel_id,
                    "analysis_type": analysis_type,
                    "period_days": period_days,
                },
                triggered_by=f"user_{self.user_id}",
            )
            self.actions.append(action)

            # Get AI provider
            provider = await self._get_ai_provider()

            # TODO: Fetch real channel data from database
            # For now, use mock data
            channel_data = {
                "channel_id": channel_id,
                "name": f"Channel {channel_id}",
                "subscriber_count": 10000,
                "avg_views": 500,
                "engagement_rate": 5.0,
            }

            # Create AI prompt
            messages = [
                AIMessage(
                    role="system",
                    content=(
                        "You are an expert Telegram channel analyst. "
                        "Analyze the provided channel metrics and provide actionable insights. "
                        "Focus on growth opportunities, engagement patterns, and content recommendations."
                    ),
                ),
                AIMessage(
                    role="user",
                    content=(
                        f"Analyze this Telegram channel:\n"
                        f"Channel: {channel_data['name']}\n"
                        f"Subscribers: {channel_data['subscriber_count']}\n"
                        f"Avg Views: {channel_data['avg_views']}\n"
                        f"Engagement: {channel_data['engagement_rate']}%\n"
                        f"Period: Last {period_days} days\n"
                        f"Analysis Type: {analysis_type}\n\n"
                        f"Provide:\n"
                        f"1. Key insights (3-5 points)\n"
                        f"2. Growth opportunities\n"
                        f"3. Content recommendations\n"
                        f"4. Action items"
                    ),
                ),
            ]

            logger.info(
                f"📊 Analyzing channel {channel_id} with AI provider {provider.provider_info.name}"
            )

            # Get AI response
            response = await provider.complete(messages, max_tokens=1000)

            # Track usage
            await self._track_ai_usage(
                provider_name=response.provider,
                tokens_used=response.tokens_used,
                cost_usd=response.cost_usd,
            )

            logger.info(
                f"✅ Channel analysis complete: {response.tokens_used} tokens, "
                f"${response.cost_usd:.4f} cost"
            )

            # Parse insights from AI response
            insights = self._parse_insights(response.content)

            return {
                "success": True,
                "channel_id": channel_id,
                "analysis_type": analysis_type,
                "period_days": period_days,
                "insights": insights,
                "ai_provider": response.provider,
                "ai_model": response.model,
                "tokens_used": response.tokens_used,
                "cost_usd": response.cost_usd,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Channel analysis failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _parse_insights(self, ai_response: str) -> dict[str, Any]:
        """Parse AI response into structured insights."""
        # Simple parsing for now - can be improved with structured output
        lines = ai_response.strip().split("\n")

        insights = {
            "summary": (ai_response[:200] + "..." if len(ai_response) > 200 else ai_response),
            "full_analysis": ai_response,
            "key_points": [],
            "recommendations": [],
        }

        # Extract bullet points as key insights
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                point = line.lstrip("-•* ").strip()
                if point:
                    insights["key_points"].append(point)

        return insights

    async def suggest_content(
        self,
        channel_id: int,
        topic: str | None = None,
        content_type: str = "post",
        count: int = 3,
    ) -> dict[str, Any]:
        """
        Generate content suggestions for a channel.

        Args:
            channel_id: Target channel
            topic: Optional topic focus
            content_type: Type of content (post, poll, quiz)
            count: Number of suggestions

        Returns:
            Dictionary with content suggestions
        """
        if not self.config.can_use_feature(AIFeature.CONTENT_SUGGESTIONS):
            return {
                "success": False,
                "error": "Content suggestions not enabled for your account",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            self.config.increment_usage()

            logger.info(f"💡 Generating content suggestions for channel {channel_id}")

            # TODO: Implement with LLM
            return {
                "success": True,
                "channel_id": channel_id,
                "topic": topic,
                "content_type": content_type,
                "suggestions": [
                    {
                        "id": i + 1,
                        "title": f"Content suggestion {i + 1}",
                        "preview": "Content preview will be generated by LLM",
                        "reasoning": "Based on channel analysis",
                    }
                    for i in range(count)
                ],
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Content suggestion failed: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_audience(
        self,
        channel_id: int,
    ) -> dict[str, Any]:
        """
        Analyze channel audience demographics and behavior.
        """
        if not self.config.can_use_feature(AIFeature.AUDIENCE_ANALYSIS):
            return {
                "success": False,
                "error": "Audience analysis not enabled for your account",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            self.config.increment_usage()

            logger.info(f"👥 Analyzing audience for channel {channel_id}")

            # TODO: Implement audience analysis
            return {
                "success": True,
                "channel_id": channel_id,
                "audience": {
                    "estimated_size": 0,
                    "engagement_rate": 0.0,
                    "peak_activity_hours": [],
                    "demographics": {},
                },
                "insights": [],
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Audience analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_posting_recommendations(
        self,
        channel_id: int,
    ) -> dict[str, Any]:
        """
        Get AI recommendations for optimal posting times and frequency.
        """
        if not self.config.can_use_feature(AIFeature.POSTING_OPTIMIZATION):
            return {
                "success": False,
                "error": "Posting optimization not enabled for your account",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            self.config.increment_usage()

            logger.info(f"⏰ Getting posting recommendations for channel {channel_id}")

            # TODO: Implement posting optimization
            return {
                "success": True,
                "channel_id": channel_id,
                "recommendations": {
                    "optimal_times": [],
                    "frequency": "2-3 posts per day",
                    "content_mix": {},
                },
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Posting recommendations failed: {e}")
            return {"success": False, "error": str(e)}

    async def custom_query(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a custom AI query (Pro/Enterprise only).

        Args:
            query: Natural language query
            context: Optional context data (channel_id, etc.)

        Returns:
            AI response to the query
        """
        if not self.config.limits.custom_queries_enabled:
            return {
                "success": False,
                "error": "Custom queries require Pro or Enterprise tier",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            self.config.increment_usage()

            logger.info(f"🔍 Processing custom query for user {self.user_id}")

            # TODO: Implement with LLM
            return {
                "success": True,
                "query": query,
                "response": "Custom query processing will be implemented in Phase 2",
                "context_used": context or {},
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Custom query failed: {e}")
            return {"success": False, "error": str(e)}

    async def execute_marketplace_service(
        self,
        service_id: str,
        parameters: dict[str, Any],
        channel_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute a marketplace service through AI.

        Marketplace services can be:
        - Auto-posting to Telegram
        - Content scheduling
        - Cross-platform analytics
        - Custom integrations

        Args:
            service_id: The marketplace service identifier
            parameters: Service-specific parameters
            channel_id: Target channel (optional)

        Returns:
            Service execution result
        """
        if not self.config.can_use_marketplace_service(service_id):
            return {
                "success": False,
                "error": f"Service {service_id} not enabled or not available for your tier",
            }

        can_request, message = self.config.can_make_request()
        if not can_request:
            return {"success": False, "error": message}

        try:
            self.config.increment_usage()

            logger.info(f"🔧 Executing marketplace service {service_id} for user {self.user_id}")

            # Load service from marketplace registry
            from apps.ai.user.marketplace import (
                ServiceExecutionContext,
                get_marketplace_registry,
            )

            registry = get_marketplace_registry()
            adapter = registry.get(service_id)

            if not adapter:
                return {
                    "success": False,
                    "error": f"Service {service_id} not found in registry",
                }

            # Check tier requirements
            if not adapter.check_tier(self.config.tier.value):
                return {
                    "success": False,
                    "error": f"Service {service_id} requires {adapter.definition.required_tier} tier or higher",
                }

            # Create execution context
            context = ServiceExecutionContext(
                user_id=self.user_id,
                channel_id=channel_id,
                parameters=parameters,
                ai_enhancement=True,
                dry_run=False,
            )

            # Validate parameters
            is_valid, validation_error = await adapter.validate_parameters(parameters)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Invalid parameters: {validation_error}",
                }

            # Execute service
            result = await adapter.execute(context)

            # Record action
            action = Action(
                action_id=f"mp_{service_id}_{datetime.utcnow().timestamp()}",
                action_type=ActionType.EXECUTE_SERVICE,
                target_worker=f"marketplace_{service_id}",
                parameters=parameters,
            )
            self.actions.append(action)

            return {
                "success": result.success,
                "service_id": service_id,
                "service_name": adapter.definition.name,
                "result": result.result_data,
                "ai_insights": result.ai_insights,
                "execution_time_ms": result.execution_time_ms,
                "error": result.error_message,
                "executed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Marketplace service execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def list_available_services(self) -> dict[str, Any]:
        """
        List marketplace services available to this user.

        Returns:
            Dictionary with available services and their details
        """
        try:
            from apps.ai.user.marketplace import get_marketplace_registry

            registry = get_marketplace_registry()

            # Get services available for user's tier
            available = registry.find_by_tier(self.config.tier.value)

            services = []
            for adapter in available:
                defn = adapter.definition
                services.append(
                    {
                        "service_id": defn.service_id,
                        "name": defn.name,
                        "description": defn.description,
                        "capabilities": [c.value for c in defn.capabilities],
                        "required_tier": defn.required_tier,
                        "is_free": defn.is_free,
                        "monthly_price": defn.monthly_price,
                        "enabled": defn.service_id in self.config.enabled_services,
                    }
                )

            return {
                "success": True,
                "user_tier": self.config.tier.value,
                "services": services,
                "total_available": len(services),
            }

        except Exception as e:
            logger.error(f"❌ Failed to list services: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> dict[str, Any]:
        """Get agent status and usage statistics"""
        return {
            "user_id": self.user_id,
            "tier": self.config.tier.value,
            "usage": {
                "requests_today": self.config.requests_today,
                "requests_this_hour": self.config.requests_this_hour,
                "limits": {
                    "daily": self.config.limits.requests_per_day,
                    "hourly": self.config.limits.requests_per_hour,
                },
            },
            "enabled_features": [f.value for f in self.config.settings.enabled_features],
            "enabled_services": self.config.enabled_services,
            "session_actions": len(self.actions),
        }
