"""
Payment Analytics Microservice
==============================

Focused microservice for payment analytics, statistics, and business intelligence.
Handles payment metrics, subscription analytics, and reporting.

Single Responsibility: Payment analytics and reporting only.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from ..protocols.payment_protocols import (
    PaymentAnalyticsProtocol,
    PaymentStats,
    SubscriptionStats,
)

logger = logging.getLogger(__name__)


class PaymentAnalyticsService(PaymentAnalyticsProtocol):
    """
    Payment analytics microservice.

    Responsibilities:
    - Calculate payment statistics and metrics
    - Generate subscription analytics and KPIs
    - Provide revenue analytics and forecasting
    - Analyze payment failures and churn
    - Generate business intelligence reports
    """

    def __init__(self, payment_repository):
        self.repository = payment_repository
        logger.info("📊 PaymentAnalyticsService initialized")

    async def get_payment_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> PaymentStats:
        """
        Get comprehensive payment statistics.

        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            PaymentStats with comprehensive metrics
        """
        try:
            logger.info("📊 Generating payment statistics")

            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)  # Last 30 days

            # Get raw payment statistics
            raw_stats = await self.repository.get_payment_statistics(start_date, end_date)

            # Calculate derived metrics
            total_payments = raw_stats.get("total_payments", 0)
            successful_payments = raw_stats.get("successful_payments", 0)
            failed_payments = raw_stats.get("failed_payments", 0)
            total_revenue = Decimal(str(raw_stats.get("total_revenue", 0)))
            failed_amount = Decimal(str(raw_stats.get("failed_amount", 0)))

            # Calculate average payment amount
            average_payment_amount = (
                total_revenue / successful_payments if successful_payments > 0 else Decimal("0")
            )

            # Get provider-specific stats
            provider_stats = await self._get_provider_statistics(start_date, end_date)

            # Get daily breakdown
            daily_stats = await self._get_daily_payment_stats(start_date, end_date)

            return PaymentStats(
                total_payments=total_payments,
                successful_payments=successful_payments,
                failed_payments=failed_payments,
                total_revenue=total_revenue,
                failed_amount=failed_amount,
                average_payment_amount=average_payment_amount,
                payment_count_by_provider=provider_stats["count_by_provider"],
                revenue_by_provider=provider_stats["revenue_by_provider"],
                daily_stats=daily_stats,
            )

        except Exception as e:
            logger.error(f"❌ Failed to get payment statistics: {e}")
            # Return empty stats on error
            return PaymentStats(
                total_payments=0,
                successful_payments=0,
                failed_payments=0,
                total_revenue=Decimal("0"),
                failed_amount=Decimal("0"),
                average_payment_amount=Decimal("0"),
                payment_count_by_provider={},
                revenue_by_provider={},
                daily_stats=[],
            )

    async def get_subscription_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> SubscriptionStats:
        """
        Get comprehensive subscription statistics.

        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            SubscriptionStats with comprehensive metrics
        """
        try:
            logger.info("📊 Generating subscription statistics")

            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)  # Last 30 days

            # Get raw subscription statistics
            raw_stats = await self.repository.get_subscription_statistics(start_date, end_date)

            # Extract basic metrics
            total_subscriptions = raw_stats.get("total_subscriptions", 0)
            active_subscriptions = raw_stats.get("active_subscriptions", 0)
            canceled_subscriptions = raw_stats.get("canceled_subscriptions", 0)
            past_due_subscriptions = raw_stats.get("past_due_subscriptions", 0)
            trial_subscriptions = raw_stats.get("trial_subscriptions", 0)

            # Calculate derived metrics
            average_subscription_amount = Decimal(str(raw_stats.get("avg_subscription_amount", 0)))

            # Calculate churn rate
            churn_rate = self._calculate_churn_rate(active_subscriptions, canceled_subscriptions)

            # Calculate recurring revenue
            mrr, arr = await self._calculate_recurring_revenue()

            return SubscriptionStats(
                total_subscriptions=total_subscriptions,
                active_subscriptions=active_subscriptions,
                canceled_subscriptions=canceled_subscriptions,
                past_due_subscriptions=past_due_subscriptions,
                trial_subscriptions=trial_subscriptions,
                average_subscription_amount=average_subscription_amount,
                churn_rate=churn_rate,
                monthly_recurring_revenue=mrr,
                yearly_recurring_revenue=arr,
            )

        except Exception as e:
            logger.error(f"❌ Failed to get subscription statistics: {e}")
            # Return empty stats on error
            return SubscriptionStats(
                total_subscriptions=0,
                active_subscriptions=0,
                canceled_subscriptions=0,
                past_due_subscriptions=0,
                trial_subscriptions=0,
                average_subscription_amount=Decimal("0"),
                churn_rate=0.0,
                monthly_recurring_revenue=Decimal("0"),
                yearly_recurring_revenue=Decimal("0"),
            )

    async def get_revenue_analytics(
        self,
        period: str = "monthly",  # "daily", "weekly", "monthly", "yearly"
    ) -> dict[str, Any]:
        """
        Get revenue analytics for a specific period.

        Args:
            period: Time period for analytics

        Returns:
            Revenue analytics data
        """
        try:
            logger.info(f"📊 Generating revenue analytics for period: {period}")

            # Calculate date range based on period
            end_date = datetime.utcnow()
            if period == "daily":
                start_date = end_date - timedelta(days=30)
                group_by = "day"
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=12)
                group_by = "week"
            elif period == "monthly":
                start_date = end_date - timedelta(days=365)
                group_by = "month"
            elif period == "yearly":
                start_date = end_date - timedelta(days=365 * 3)
                group_by = "year"
            else:
                raise ValueError(f"Unsupported period: {period}")

            # Get revenue data
            revenue_data = await self._get_revenue_by_period(start_date, end_date, group_by)

            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(revenue_data)

            # Get top revenue sources
            top_plans = await self._get_top_revenue_plans(start_date, end_date)

            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_revenue": sum(item["revenue"] for item in revenue_data),
                "revenue_data": revenue_data,
                "growth_metrics": growth_metrics,
                "top_plans": top_plans,
                "currency": "USD",  # Default currency
            }

        except Exception as e:
            logger.error(f"❌ Failed to get revenue analytics: {e}")
            return {
                "period": period,
                "error": str(e),
                "total_revenue": 0,
                "revenue_data": [],
                "growth_metrics": {},
                "top_plans": [],
            }

    async def get_churn_analysis(self) -> dict[str, Any]:
        """
        Get subscription churn analysis.

        Returns:
            Churn analysis data
        """
        try:
            logger.info("📊 Generating churn analysis")

            # Get churn data for last 12 months
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)

            # Calculate monthly churn rates
            monthly_churn = await self._get_monthly_churn_rates(start_date, end_date)

            # Analyze churn reasons
            churn_reasons = await self._analyze_churn_reasons(start_date, end_date)

            # Calculate cohort retention
            cohort_analysis = await self._calculate_cohort_retention()

            # Get at-risk customers
            at_risk_customers = await self._identify_at_risk_customers()

            return {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "overall_churn_rate": self._calculate_average_churn_rate(monthly_churn),
                "monthly_churn_rates": monthly_churn,
                "churn_reasons": churn_reasons,
                "cohort_analysis": cohort_analysis,
                "at_risk_customers": len(at_risk_customers),
                "recommendations": self._generate_churn_recommendations(
                    monthly_churn, churn_reasons
                ),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get churn analysis: {e}")
            return {
                "error": str(e),
                "overall_churn_rate": 0.0,
                "monthly_churn_rates": [],
                "churn_reasons": {},
                "recommendations": [],
            }

    async def get_payment_failure_analysis(self) -> dict[str, Any]:
        """
        Analyze payment failures and reasons.

        Returns:
            Payment failure analysis
        """
        try:
            logger.info("📊 Analyzing payment failures")

            # Get failure data for last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            # Get failure statistics
            failure_stats = await self._get_payment_failure_stats(start_date, end_date)

            # Analyze failure reasons
            failure_reasons = await self._analyze_failure_reasons(start_date, end_date)

            # Get failure trends
            failure_trends = await self._get_failure_trends(start_date, end_date)

            # Calculate failure rate by provider
            provider_failure_rates = await self._calculate_provider_failure_rates(
                start_date, end_date
            )

            return {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "total_failures": failure_stats["total_failures"],
                "failure_rate": failure_stats["failure_rate"],
                "failed_amount": failure_stats["failed_amount"],
                "failure_reasons": failure_reasons,
                "failure_trends": failure_trends,
                "provider_failure_rates": provider_failure_rates,
                "recommendations": self._generate_failure_recommendations(
                    failure_reasons, provider_failure_rates
                ),
            }

        except Exception as e:
            logger.error(f"❌ Failed to analyze payment failures: {e}")
            return {
                "error": str(e),
                "total_failures": 0,
                "failure_rate": 0.0,
                "recommendations": [],
            }

    async def get_provider_performance(self) -> dict[str, Any]:
        """
        Compare performance across payment providers.

        Returns:
            Provider performance comparison
        """
        try:
            logger.info("📊 Analyzing provider performance")

            # Get performance data for last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)

            # Get provider statistics
            provider_stats = await self._get_detailed_provider_stats(start_date, end_date)

            # Calculate performance metrics for each provider
            provider_performance = {}
            for provider, stats in provider_stats.items():
                provider_performance[provider] = {
                    "total_transactions": stats["total_transactions"],
                    "successful_transactions": stats["successful_transactions"],
                    "failed_transactions": stats["failed_transactions"],
                    "success_rate": (
                        stats["successful_transactions"] / stats["total_transactions"] * 100
                        if stats["total_transactions"] > 0
                        else 0
                    ),
                    "total_revenue": stats["total_revenue"],
                    "average_transaction_amount": (
                        stats["total_revenue"] / stats["successful_transactions"]
                        if stats["successful_transactions"] > 0
                        else Decimal("0")
                    ),
                    "average_processing_time": stats.get("average_processing_time", 0),
                }

            # Determine best performing provider
            best_provider = max(
                provider_performance.items(),
                key=lambda x: x[1]["success_rate"],
                default=(None, {}),
            )[0]

            return {
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "provider_performance": provider_performance,
                "best_performing_provider": best_provider,
                "recommendations": self._generate_provider_recommendations(provider_performance),
            }

        except Exception as e:
            logger.error(f"❌ Failed to analyze provider performance: {e}")
            return {"error": str(e), "provider_performance": {}, "recommendations": []}

    # Helper methods for calculations and data processing

    async def _get_provider_statistics(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get provider-specific statistics."""
        # Simplified implementation - in real scenario, this would query the database
        return {
            "count_by_provider": {"stripe": 100, "payme": 50, "click": 25},
            "revenue_by_provider": {
                "stripe": Decimal("5000.00"),
                "payme": Decimal("2500.00"),
                "click": Decimal("1000.00"),
            },
        }

    async def _get_daily_payment_stats(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get daily payment statistics."""
        # Simplified implementation
        stats = []
        current_date = start_date
        while current_date <= end_date:
            stats.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "total_payments": 10,
                    "successful_payments": 9,
                    "failed_payments": 1,
                    "revenue": Decimal("500.00"),
                }
            )
            current_date += timedelta(days=1)
        return stats

    def _calculate_churn_rate(
        self, active_subscriptions: int, canceled_subscriptions: int
    ) -> float:
        """Calculate subscription churn rate."""
        total = active_subscriptions + canceled_subscriptions
        return (canceled_subscriptions / total * 100) if total > 0 else 0.0

    async def _calculate_recurring_revenue(self) -> tuple[Decimal, Decimal]:
        """Calculate Monthly and Annual Recurring Revenue."""
        # Simplified calculation
        mrr = Decimal("10000.00")  # $10k MRR
        arr = mrr * 12  # $120k ARR
        return mrr, arr

    async def _get_revenue_by_period(
        self, start_date: datetime, end_date: datetime, group_by: str
    ) -> list[dict[str, Any]]:
        """Get revenue data grouped by time period."""
        # Simplified implementation
        return [
            {"period": "2024-01", "revenue": Decimal("5000.00"), "transactions": 100},
            {"period": "2024-02", "revenue": Decimal("5500.00"), "transactions": 110},
            {"period": "2024-03", "revenue": Decimal("6000.00"), "transactions": 120},
        ]

    def _calculate_growth_metrics(self, revenue_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate revenue growth metrics."""
        if len(revenue_data) < 2:
            return {"growth_rate": 0.0, "trend": "insufficient_data"}

        latest = revenue_data[-1]["revenue"]
        previous = revenue_data[-2]["revenue"]

        growth_rate = ((latest - previous) / previous * 100) if previous > 0 else 0

        return {
            "growth_rate": float(growth_rate),
            "trend": (
                "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            ),
        }

    async def _get_top_revenue_plans(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get top revenue generating plans."""
        # Simplified implementation
        return [
            {"plan_name": "Premium", "revenue": Decimal("8000.00"), "subscribers": 80},
            {"plan_name": "Basic", "revenue": Decimal("3000.00"), "subscribers": 150},
            {
                "plan_name": "Enterprise",
                "revenue": Decimal("5000.00"),
                "subscribers": 10,
            },
        ]

    async def _get_monthly_churn_rates(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get monthly churn rates."""
        # Simplified implementation
        return [
            {
                "month": "2024-01",
                "churn_rate": 5.2,
                "churned_customers": 26,
                "total_customers": 500,
            },
            {
                "month": "2024-02",
                "churn_rate": 4.8,
                "churned_customers": 24,
                "total_customers": 500,
            },
            {
                "month": "2024-03",
                "churn_rate": 6.1,
                "churned_customers": 30,
                "total_customers": 490,
            },
        ]

    async def _analyze_churn_reasons(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, int]:
        """Analyze reasons for subscription cancellations."""
        # Simplified implementation
        return {
            "price_too_high": 15,
            "no_longer_needed": 10,
            "switching_to_competitor": 8,
            "technical_issues": 5,
            "other": 12,
        }

    async def _calculate_cohort_retention(self) -> dict[str, Any]:
        """Calculate cohort retention analysis."""
        # Simplified implementation
        return {
            "month_0": 100,
            "month_1": 85,
            "month_3": 75,
            "month_6": 65,
            "month_12": 55,
        }

    async def _identify_at_risk_customers(self) -> list[str]:
        """Identify customers at risk of churning."""
        # Simplified implementation
        return ["customer_1", "customer_2", "customer_3"]

    def _calculate_average_churn_rate(self, monthly_churn: list[dict[str, Any]]) -> float:
        """Calculate average churn rate from monthly data."""
        if not monthly_churn:
            return 0.0
        return sum(item["churn_rate"] for item in monthly_churn) / len(monthly_churn)

    def _generate_churn_recommendations(
        self, monthly_churn: list[dict[str, Any]], churn_reasons: dict[str, int]
    ) -> list[str]:
        """Generate recommendations to reduce churn."""
        recommendations = []

        avg_churn = self._calculate_average_churn_rate(monthly_churn)
        if avg_churn > 5.0:
            recommendations.append("Churn rate is above 5% - implement retention campaigns")

        if churn_reasons.get("price_too_high", 0) > 10:
            recommendations.append("Consider offering discounts or lower-tier plans")

        if churn_reasons.get("technical_issues", 0) > 5:
            recommendations.append("Improve technical support and product stability")

        return recommendations

    async def _get_payment_failure_stats(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get payment failure statistics."""
        # Simplified implementation
        return {
            "total_failures": 45,
            "total_attempts": 500,
            "failure_rate": 9.0,
            "failed_amount": Decimal("2250.00"),
        }

    async def _analyze_failure_reasons(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, int]:
        """Analyze payment failure reasons."""
        # Simplified implementation
        return {
            "insufficient_funds": 20,
            "card_declined": 15,
            "expired_card": 5,
            "network_error": 3,
            "other": 2,
        }

    async def _get_failure_trends(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict[str, Any]]:
        """Get failure trend data."""
        # Simplified implementation
        return [
            {"date": "2024-03-01", "failures": 3, "total": 35},
            {"date": "2024-03-02", "failures": 2, "total": 32},
            {"date": "2024-03-03", "failures": 4, "total": 38},
        ]

    async def _calculate_provider_failure_rates(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, float]:
        """Calculate failure rates by provider."""
        # Simplified implementation
        return {"stripe": 7.5, "payme": 12.0, "click": 15.5}

    def _generate_failure_recommendations(
        self, failure_reasons: dict[str, int], provider_rates: dict[str, float]
    ) -> list[str]:
        """Generate recommendations to reduce payment failures."""
        recommendations = []

        if failure_reasons.get("insufficient_funds", 0) > 15:
            recommendations.append("Implement smart retry logic for insufficient funds")

        if failure_reasons.get("expired_card", 0) > 3:
            recommendations.append("Send proactive card expiration notifications")

        worst_provider = max(provider_rates.items(), key=lambda x: x[1], default=(None, 0))
        if worst_provider[1] > 10:
            recommendations.append(
                f"Review {worst_provider[0]} provider configuration - high failure rate"
            )

        return recommendations

    async def _get_detailed_provider_stats(
        self, start_date: datetime, end_date: datetime
    ) -> dict[str, dict[str, Any]]:
        """Get detailed statistics for each provider."""
        # Simplified implementation
        return {
            "stripe": {
                "total_transactions": 300,
                "successful_transactions": 285,
                "failed_transactions": 15,
                "total_revenue": Decimal("15000.00"),
                "average_processing_time": 2.1,
            },
            "payme": {
                "total_transactions": 150,
                "successful_transactions": 135,
                "failed_transactions": 15,
                "total_revenue": Decimal("6750.00"),
                "average_processing_time": 3.2,
            },
            "click": {
                "total_transactions": 100,
                "successful_transactions": 85,
                "failed_transactions": 15,
                "total_revenue": Decimal("4250.00"),
                "average_processing_time": 4.1,
            },
        }

    def _generate_provider_recommendations(
        self, provider_performance: dict[str, dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations for provider optimization."""
        recommendations = []

        # Find providers with low success rates
        for provider, stats in provider_performance.items():
            if stats["success_rate"] < 90:
                recommendations.append(f"Review {provider} configuration - success rate below 90%")

        # Find slowest provider
        slowest_provider = max(
            provider_performance.items(),
            key=lambda x: x[1].get("average_processing_time", 0),
            default=(None, {}),
        )[0]

        if slowest_provider:
            recommendations.append(f"Optimize {slowest_provider} integration for faster processing")

        return recommendations

    async def health_check(self) -> dict[str, Any]:
        """Health check for payment analytics service."""
        try:
            # Test repository connection by getting basic stats
            test_stats = await self.repository.get_payment_statistics()

            return {
                "service": "PaymentAnalyticsService",
                "status": "healthy",
                "repository_connected": True,
                "data_available": len(test_stats) > 0,
            }
        except Exception as e:
            return {
                "service": "PaymentAnalyticsService",
                "status": "unhealthy",
                "error": str(e),
            }
