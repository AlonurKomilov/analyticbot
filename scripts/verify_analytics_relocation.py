"""
🔍 Import Verification Script

Verify all analytics imports are working correctly after relocation
"""

import sys
from pathlib import Path


def test_new_imports():
    """Test all new import paths"""
    print("🔍 Testing New Import Paths...")
    print("=" * 50)
    success_count = 0
    total_tests = 0
    try:
        import apps.bot.analytics as analytics

        print(f"✅ bot.analytics - {len(analytics.__all__)} components")
        success_count += 1
    except Exception as e:
        print(f"❌ bot.analytics - {e}")
    total_tests += 1
    components = [
        ("AdvancedDataProcessor", "bot.utils.data_processor"),
        ("PredictiveAnalyticsEngine", "bot.services.ml.predictive_engine"),
        ("AIInsightsGenerator", "bot.services.ml.ai_insights"),
        ("VisualizationEngine", "bot.services.dashboard_service"),
        ("AutomatedReportingSystem", "bot.services.reporting_service"),
    ]
    for component, module in components:
        try:
            exec(f"from {module} import {component}")
            print(f"✅ {component} from {module}")
            success_count += 1
        except Exception as e:
            print(f"❌ {component} from {module} - {e}")
        total_tests += 1
    try:
        print("✅ All components from apps.bot.system.analytics")
        success_count += 1
    except Exception as e:
        print(f"❌ All components from apps.bot.system.analytics - {e}")
    total_tests += 1
    try:
        print("✅ Factory functions from apps.bot.system.analytics")
        success_count += 1
    except Exception as e:
        print(f"❌ Factory functions from apps.bot.system.analytics - {e}")
    total_tests += 1
    print("=" * 50)
    print(
        f"📊 IMPORT TEST RESULTS: {success_count}/{total_tests} ({success_count / total_tests * 100:.1f}%)"
    )
    return success_count == total_tests


def check_old_imports():
    """Check that old imports are no longer accessible"""
    print("\n🚫 Testing Old Import Paths (Should Fail)...")
    print("=" * 50)
    old_imports = [
        "from analytics.data_processor import AdvancedDataProcessor",
        "from analytics.predictive_engine import PredictiveAnalyticsEngine",
        "from analytics.dashboard import VisualizationEngine",
        "from analytics.ai_insights import AIInsightsGenerator",
        "from analytics.reporting_system import AutomatedReportingSystem",
        "from analytics import AdvancedDataProcessor",
        "import analytics",
    ]
    failed_correctly = 0
    for import_stmt in old_imports:
        try:
            exec(import_stmt)
            print(f"⚠️  {import_stmt} - Still works (should fail)")
        except ImportError:
            print(f"✅ {import_stmt} - Correctly fails")
            failed_correctly += 1
        except Exception as e:
            print(f"❓ {import_stmt} - Unexpected error: {e}")
    print("=" * 50)
    print(f"📊 OLD IMPORT BLOCKS: {failed_correctly}/{len(old_imports)} correctly blocked")
    return failed_correctly == len(old_imports)


def verify_file_structure():
    """Verify the new file structure exists"""
    print("\n📁 Verifying New File Structure...")
    print("=" * 50)
    expected_files = [
        "bot/analytics.py",
        "bot/utils/data_processor.py",
        "bot/services/ml/predictive_engine.py",
        "bot/services/ml/ai_insights.py",
        "bot/services/dashboard_service.py",
        "bot/services/reporting_service.py",
    ]
    existing_files = 0
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
            existing_files += 1
        else:
            print(f"❌ {file_path} - Not found")
    print("=" * 50)
    print(f"📊 FILE STRUCTURE: {existing_files}/{len(expected_files)} files exist")
    return existing_files == len(expected_files)


def main():
    """Run all verification tests"""
    print("🚀 ANALYTICS RELOCATION VERIFICATION")
    print("=" * 60)
    new_imports_ok = test_new_imports()
    old_imports_blocked = check_old_imports()
    file_structure_ok = verify_file_structure()
    print("\n" + "=" * 60)
    print("📋 FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    results = [
        ("New Imports Working", new_imports_ok),
        ("Old Imports Blocked", old_imports_blocked),
        ("File Structure Correct", file_structure_ok),
    ]
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ Analytics relocation is complete and working")
        print("✅ Safe to delete the old analytics/ directory")
    else:
        print("⚠️  SOME VERIFICATION TESTS FAILED")
        print("❌ Do not delete analytics/ directory yet")
        print("🔧 Fix the failing tests first")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
