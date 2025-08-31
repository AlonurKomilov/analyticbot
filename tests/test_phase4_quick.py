"""
🧪 Phase 4.0 Advanced Analytics - Quick Test Suite

Simplified test to verify core functionality of all 5 modules.
"""

import asyncio
import logging
import sys
from datetime import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspaces/analyticbot")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_simple_test_data():
    """Create simple test dataset"""
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=100, freq="D"),
            "sales": 1000 + np.cumsum(np.random.normal(10, 50, 100)),
            "customers": np.random.poisson(50, 100),
            "region": np.random.choice(["North", "South"], 100),
        }
    )
    df.loc[np.random.choice(df.index, 5), "sales"] = np.nan
    return df


async def test_data_processor():
    """Test basic data processing functionality"""
    try:
        print("🧪 Testing Data Processor...")
        from apps.bot.utils.data_processor import AdvancedDataProcessor

        processor = AdvancedDataProcessor()
        test_df = create_simple_test_data()
        quality_report = await processor.analyze_data_quality(test_df)
        print(f"   ✅ Data quality score: {quality_report['overall_score']:.1f}/100")
        cleaned_df = await processor.clean_data(test_df)
        print(f"   ✅ Cleaned data: {cleaned_df.shape[0]} rows")
        return True
    except Exception as e:
        print(f"   ❌ Data Processor test failed: {str(e)}")
        return False


async def test_predictive_engine():
    """Test basic predictive analytics"""
    try:
        print("🧪 Testing Predictive Engine...")
        from apps.bot.services.ml.predictive_engine import PredictiveAnalyticsEngine

        engine = PredictiveAnalyticsEngine()
        test_df = create_simple_test_data().dropna()
        results = await engine.auto_predict(
            test_df, "sales", task_type="regression", test_size=0.3, optimize=False
        )
        print(f"   ✅ Best model: {results['best_model']}")
        print(f"   ✅ Model score: {results['best_model_score']:.3f}")
        return True
    except Exception as e:
        print(f"   ❌ Predictive Engine test failed: {str(e)}")
        return False


async def test_visualization():
    """Test visualization capabilities"""
    try:
        print("🧪 Testing Visualization Engine...")
        from apps.bot.services.dashboard_service import VisualizationEngine

        viz_engine = VisualizationEngine()
        test_df = create_simple_test_data().dropna()
        viz_engine.create_line_chart(
            test_df.head(50), "timestamp", "sales", title="Test Sales Chart"
        )
        print("   ✅ Line chart created")
        bar_data = test_df.groupby("region")["sales"].sum().reset_index()
        viz_engine.create_bar_chart(
            bar_data, "region", "sales", title="Sales by Region"
        )
        print("   ✅ Bar chart created")
        return True
    except Exception as e:
        print(f"   ❌ Visualization test failed: {str(e)}")
        return False


async def test_ai_insights():
    """Test AI insights generation"""
    try:
        print("🧪 Testing AI Insights Generator...")
        from apps.bot.services.ml.ai_insights import AIInsightsGenerator

        insights_gen = AIInsightsGenerator()
        test_df = create_simple_test_data()
        insights = await insights_gen.generate_comprehensive_insights(
            test_df,
            target_column="sales",
            time_column="timestamp",
            insight_types=["statistical_summary", "correlation_insights"],
        )
        print(f"   ✅ Insights generated: {len(insights['insights'])} types")
        print(f"   ✅ Recommendations: {len(insights['recommendations'])}")
        return True
    except Exception as e:
        print(f"   ❌ AI Insights test failed: {str(e)}")
        return False


async def test_reporting():
    """Test reporting system"""
    try:
        print("🧪 Testing Reporting System...")
        from apps.bot.services.reporting_service import AutomatedReportingSystem

        reporting_system = AutomatedReportingSystem(output_directory="/tmp/quick_test_reports")
        test_df = create_simple_test_data()
        template = reporting_system.create_template(
            template_name="quick_test", sections=["executive_summary", "key_metrics"]
        )
        print(f"   ✅ Template created: {template.name}")
        output_files = await reporting_system.generate_comprehensive_report(
            data_source=test_df,
            template_name="quick_test",
            report_title="Quick Test Report",
            output_formats=["json"],
            include_insights=False,
            include_predictions=False,
        )
        print(f"   ✅ Report generated: {len(output_files)} formats")
        return True
    except Exception as e:
        print(f"   ❌ Reporting test failed: {str(e)}")
        return False


async def main():
    """Run quick test suite"""
    print("🚀 PHASE 4.0 ADVANCED ANALYTICS - QUICK TEST SUITE")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    test_results = []
    test_results.append(("Data Processor", await test_data_processor()))
    test_results.append(("Predictive Engine", await test_predictive_engine()))
    test_results.append(("Visualization", await test_visualization()))
    test_results.append(("AI Insights", await test_ai_insights()))
    test_results.append(("Reporting System", await test_reporting()))
    print("\n" + "=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    passed_tests = 0
    total_tests = len(test_results)
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed_tests += 1
    print("-" * 60)
    print(f"SUCCESS RATE: {passed_tests / total_tests * 100:.1f}% ({passed_tests}/{total_tests})")
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n📋 PHASE 4.0 MODULES VERIFIED:")
        print("✅ Module 4.1: Advanced Data Processing Engine")
        print("✅ Module 4.2: Predictive Analytics & Forecasting")
        print("✅ Module 4.3: Real-time Analytics Dashboard")
        print("✅ Module 4.4: AI-Powered Insights Generator")
        print("✅ Module 4.5: Automated Reporting System")
        print("\n🚀 ENTERPRISE DATA SCIENCE PLATFORM READY!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TEST(S) FAILED")
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
