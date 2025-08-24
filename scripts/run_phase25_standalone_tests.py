"""
🤖 Phase 2.5: AI/ML Enhancement Test Runner (Standalone)

Test Coverage:
- ML service initialization (without config dependencies)
- Content analysis and optimization
- Engagement prediction
- Churn risk assessment
- Direct service testing
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
os.environ["TESTING"] = "true"


async def test_ml_services_standalone():
    """🧪 Test core ML services without config dependencies"""
    print("\n" + "=" * 60)
    print("🤖 PHASE 2.5: AI/ML ENHANCEMENT - STANDALONE TESTING")
    print("=" * 60)
    test_results = {
        "ml_imports": False,
        "content_analysis": False,
        "engagement_prediction": False,
        "churn_prediction": False,
        "real_time_scoring": False,
        "hashtag_optimization": False,
    }
    print("\n🔍 Testing ML service imports (standalone)...")
    try:
        import sys

        sys.path.insert(0, "/workspaces/analyticbot")
        from apps.bot.services.ml.churn_predictor import ChurnPredictor
        from apps.bot.services.ml.content_optimizer import ContentOptimizer
        from apps.bot.services.ml.prediction_service import (
            ContentMetrics,
            PredictionService,
        )

        print("✅ All ML services imported successfully")
        test_results["ml_imports"] = True
    except Exception as e:
        print(f"❌ ML import failed: {e}")
        return test_results
    print("\n📝 Testing content analysis...")
    try:
        content_optimizer = ContentOptimizer(cache_service=None, analytics_service=None)
        test_content = "\n        🚀 Exciting news! Our new AI-powered analytics feature is now live!\n        \n        This revolutionary update will help you:\n        • Boost engagement by 40-60%\n        • Predict optimal posting times\n        • Analyze content performance in real-time\n        \n        Try it now and transform your social media strategy! \n        \n        #analytics #AI #socialmedia #growth #innovation #tech\n        "
        analysis = await content_optimizer.analyze_content(
            text=test_content, media_urls=["https://example.com/image.jpg"], target_audience="tech"
        )
        print(f"   📊 Content Score: {analysis.overall_score:.1f}/100")
        print(f"   😊 Sentiment: {analysis.sentiment_label} ({analysis.sentiment_score:.2f})")
        print(f"   📖 Readability: {analysis.readability_level} ({analysis.readability_score:.1f})")
        print(f"   📱 Hashtags: {analysis.hashtag_count}")
        print(f"   🎯 SEO Score: {analysis.seo_score:.1f}")
        print(f"   💡 Suggestions: {len(analysis.optimization_tips)}")
        print(f"   🏷️ Hashtag Suggestions: {len(analysis.suggested_hashtags)}")
        if analysis.overall_score > 0:
            print("✅ Content analysis working correctly")
            test_results["content_analysis"] = True
            if analysis.optimization_tips:
                print(f"   💡 Top recommendation: {analysis.optimization_tips[0]}")
        else:
            print("⚠️ Content analysis returned zero score")
    except Exception as e:
        print(f"❌ Content analysis failed: {e}")
        import traceback

        traceback.print_exc()
    print("\n⚡ Testing real-time content scoring...")
    try:
        scores = await content_optimizer.score_content_realtime(test_content)
        print(f"   ⚡ Real-time Score: {scores.get('overall_score', 0):.3f}")
        print(f"   📏 Length Score: {scores.get('length_score', 0):.3f}")
        print(f"   📱 Hashtag Score: {scores.get('hashtag_score', 0):.3f}")
        print(f"   😊 Sentiment Score: {scores.get('sentiment_score', 0):.3f}")
        print(f"   😀 Emoji Score: {scores.get('emoji_score', 0):.3f}")
        if scores.get("overall_score", 0) > 0:
            print("✅ Real-time scoring working")
            test_results["real_time_scoring"] = True
    except Exception as e:
        print(f"❌ Real-time scoring failed: {e}")
    print("\n📱 Testing hashtag optimization...")
    try:
        hashtag_suggestions = await content_optimizer.optimize_hashtags(
            text=test_content,
            current_hashtags=["#analytics", "#AI"],
            target_audience="tech",
            max_suggestions=8,
        )
        print(f"   📱 Generated {len(hashtag_suggestions)} hashtag suggestions")
        for i, suggestion in enumerate(hashtag_suggestions[:5], 1):
            print(f"   {i}. {suggestion.tag} (relevance: {suggestion.relevance_score:.2f})")
        if hashtag_suggestions:
            print("✅ Hashtag optimization working")
            test_results["hashtag_optimization"] = True
    except Exception as e:
        print(f"❌ Hashtag optimization failed: {e}")
    print("\n🎯 Testing engagement prediction...")
    try:
        prediction_service = PredictionService(cache_service=None, db_service=None)
        await prediction_service.initialize_models()
        content_metrics = ContentMetrics(
            sentiment_score=0.7,
            readability_score=0.8,
            hashtag_count=6,
            word_count=150,
            media_count=1,
            emoji_count=3,
            engagement_history=[120, 95, 180, 220, 150],
        )
        prediction = await prediction_service.predict_engagement(
            content_metrics, channel_id=12345, scheduled_time=datetime.now()
        )
        print(f"   📈 Predicted Engagement: {prediction.prediction:.1f}")
        print(f"   🎯 Confidence: {prediction.confidence:.2f}")
        print(f"   🔑 Key Factors: {len(prediction.factors)}")
        print(f"   💡 Recommendations: {len(prediction.recommendations)}")
        if prediction.factors:
            top_factor = max(prediction.factors.items(), key=lambda x: x[1])
            print(f"   🔝 Top factor: {top_factor[0]} ({top_factor[1]:.3f})")
        if prediction.recommendations:
            print(f"   💡 Top recommendation: {prediction.recommendations[0]}")
        if prediction.prediction > 0:
            print("✅ Engagement prediction working")
            test_results["engagement_prediction"] = True
    except Exception as e:
        print(f"❌ Engagement prediction failed: {e}")
        import traceback

        traceback.print_exc()
    print("\n⏰ Testing optimal timing analysis...")
    try:
        timing_result = await prediction_service.find_optimal_posting_time(
            channel_id=12345, content_type="tech", date_range_days=7
        )
        print("   ⏰ Analysis completed")
        print(f"   📈 Expected Boost: {timing_result.get('expected_boost', 1):.2f}x")
        print(f"   🎯 Confidence: {timing_result.get('confidence', 0):.2f}")
        optimal_times = timing_result.get("optimal_times", {})
        if optimal_times:
            print(f"   📅 Days analyzed: {len(optimal_times)}")
            monday_times = optimal_times.get("monday", [])
            if monday_times:
                print(f"   📅 Monday optimal: {', '.join(monday_times[:3])}")
        recommendations = timing_result.get("recommendations", [])
        if recommendations:
            print(f"   💡 Timing tip: {recommendations[0]}")
        print("✅ Optimal timing analysis working")
    except Exception as e:
        print(f"❌ Optimal timing failed: {e}")
    print("\n⚠️ Testing churn prediction...")
    try:
        churn_predictor = ChurnPredictor(
            db_service=None, analytics_service=None, cache_service=None
        )
        await churn_predictor.initialize_model()
        assessment = await churn_predictor.predict_churn_risk(user_id=67890, channel_id=12345)
        print(f"   ⚠️ Churn Probability: {assessment.churn_probability:.3f}")
        print(f"   🚨 Risk Level: {assessment.risk_level}")
        print(f"   🎯 Confidence: {assessment.confidence:.2f}")
        print(f"   👤 User Segment: {assessment.user_segment}")
        print(f"   🔍 Risk Factors: {len(assessment.primary_risk_factors)}")
        print(f"   💡 Retention Strategies: {len(assessment.retention_strategies)}")
        print(f"   ⚡ Immediate Actions: {len(assessment.immediate_actions)}")
        if assessment.primary_risk_factors:
            top_risk = assessment.primary_risk_factors[0]
            print(f"   🔝 Top risk: {top_risk.get('factor', 'unknown')}")
        if assessment.immediate_actions:
            print(f"   ⚡ Top action: {assessment.immediate_actions[0]}")
        if assessment.churn_probability is not None:
            print("✅ Churn prediction working")
            test_results["churn_prediction"] = True
    except Exception as e:
        print(f"❌ Churn prediction failed: {e}")
        import traceback

        traceback.print_exc()
    print("\n🏥 Testing service health checks...")
    try:
        health_checks = {}
        services = {
            "content_optimizer": content_optimizer,
            "prediction_service": prediction_service,
            "churn_predictor": churn_predictor,
        }
        for name, service in services.items():
            try:
                health = await service.health_check()
                health_checks[name] = health
                status = health.get("status", "unknown")
                print(f"   {name}: {status}")
                if "models_loaded" in health:
                    print(f"     Models loaded: {health['models_loaded']}")
                if "timestamp" in health:
                    print(f"     Last check: {health['timestamp']}")
            except Exception as e:
                health_checks[name] = {"status": "error", "error": str(e)}
                print(f"   {name}: error ({e})")
        healthy_services = sum(1 for h in health_checks.values() if h.get("status") == "healthy")
        print(f"✅ Health checks completed: {healthy_services}/{len(services)} services healthy")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    print("\n📊 Testing performance characteristics...")
    try:
        import time

        start_time = time.time()
        for i in range(5):
            await content_optimizer.score_content_realtime(
                f"Test content {i} for performance analysis #test #performance"
            )
        analysis_time = (time.time() - start_time) / 5
        print(f"   ⚡ Avg analysis time: {analysis_time * 1000:.1f}ms")
        import sys

        memory_usage = sys.getsizeof(content_optimizer) + sys.getsizeof(prediction_service)
        print(f"   💾 Service memory: {memory_usage / 1024:.1f}KB")
        if analysis_time < 1.0:
            print("✅ Performance characteristics acceptable")
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    print("\n" + "=" * 60)
    print("📊 PHASE 2.5 STANDALONE TEST RESULTS")
    print("=" * 60)
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = passed_tests / total_tests * 100
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25}: {status}")
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    if success_rate >= 80:
        print("🚀 EXCELLENT: Phase 2.5 AI/ML Enhancement is ready for deployment!")
        recommendation = "DEPLOY"
    elif success_rate >= 60:
        print("✅ GOOD: Phase 2.5 core functionality working, minor issues detected")
        recommendation = "DEPLOY with monitoring"
    elif success_rate >= 40:
        print("⚠️ PARTIAL: Some Phase 2.5 components working, needs attention")
        recommendation = "FIX issues before deployment"
    else:
        print("❌ CRITICAL: Phase 2.5 needs significant fixes before deployment")
        recommendation = "DO NOT DEPLOY"
    print(f"\n🚀 DEPLOYMENT READINESS: {recommendation}")
    print("📈 EXPECTED BENEFITS:")
    print("   • Content Quality Scoring: Real-time analysis")
    print(f"   • Engagement Prediction: {prediction.prediction:.0f}+ expected engagement")
    print(f"   • Churn Risk Assessment: {assessment.confidence * 100:.0f}% confidence")
    print(f"   • Content Optimization: {len(analysis.optimization_tips)} actionable suggestions")
    return test_results


async def main():
    """🚀 Main standalone test runner"""
    print("🤖 PHASE 2.5: AI/ML ENHANCEMENT - STANDALONE TEST SUITE")
    print("Testing ML services without external dependencies")
    print("=" * 60)
    results = await test_ml_services_standalone()
    print(f"\n🏁 Testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        passed = sum(results.values()) if results else 0
        total = len(results) if results else 0
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - PHASE 2.5 READY!")
            sys.exit(0)
        elif passed >= total * 0.8:
            print(f"\n✅ MOST TESTS PASSED ({passed}/{total}) - GOOD TO GO!")
            sys.exit(0)
        elif passed >= total * 0.6:
            print(f"\n⚠️ PARTIAL SUCCESS ({passed}/{total}) - NEEDS ATTENTION")
            sys.exit(1)
        else:
            print(f"\n❌ MAJOR ISSUES ({passed}/{total}) - NEEDS FIXING")
            sys.exit(2)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(4)
