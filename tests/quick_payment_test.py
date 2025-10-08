"""
Quick validation test for Week 15-16 Payment System Implementation
"""

import json
import os
import sys


def test_file_exists(file_path, description):
    """Test if a file exists"""
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {'EXISTS' if exists else 'MISSING'}")
    return exists


def test_import_module(module_path, description):
    """Test if a module can be imported"""
    try:
        sys.path.insert(0, "/home/alonur/analyticbot")
        __import__(module_path)
        print(f"✅ {description}: IMPORT SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {description}: IMPORT FAILED - {str(e)}")
        return False


def test_package_dependencies():
    """Test frontend package dependencies"""
    package_json_path = "/home/alonur/analyticbot/apps/frontend/package.json"
    if not os.path.exists(package_json_path):
        print("❌ Frontend package.json: MISSING")
        return False

    with open(package_json_path) as f:
        package_data = json.load(f)

    deps = package_data.get("dependencies", {})
    required_deps = ["@stripe/react-stripe-js", "@stripe/stripe-js", "axios"]

    all_deps_present = True
    for dep in required_deps:
        if dep in deps:
            print(f"✅ Frontend dependency {dep}: CONFIGURED")
        else:
            print(f"❌ Frontend dependency {dep}: MISSING")
            all_deps_present = False

    return all_deps_present


def main():
    """Run quick validation tests"""
    print("🚀 Week 15-16 Payment System - Quick Validation")
    print("=" * 55)

    # Backend Infrastructure Tests
    print("\n📝 BACKEND INFRASTRUCTURE:")
    backend_files = [
        ("/home/alonur/analyticbot/apps/bot/services/stripe_adapter.py", "Stripe Adapter"),
        ("/home/alonur/analyticbot/apps/bot/api/payment_router.py", "Payment API Routes"),
        ("/home/alonur/analyticbot/config/settings.py", "Settings Configuration"),
        ("/home/alonur/analyticbot/apps/bot/services/payment_service.py", "Payment Service"),
    ]

    backend_results = []
    for file_path, description in backend_files:
        result = test_file_exists(file_path, description)
        backend_results.append(result)

    # Frontend Components Tests
    print("\n🌐 FRONTEND COMPONENTS:")
    frontend_files = [
        (
            "/home/alonur/analyticbot/apps/frontend/src/components/payment/PaymentForm.jsx",
            "Payment Form Component",
        ),
        (
            "/home/alonur/analyticbot/apps/frontend/src/components/payment/SubscriptionDashboard.jsx",
            "Subscription Dashboard",
        ),
        (
            "/home/alonur/analyticbot/apps/frontend/src/components/payment/PlanSelector.jsx",
            "Plan Selector Component",
        ),
        (
            "/home/alonur/analyticbot/apps/frontend/src/services/paymentAPI.js",
            "Payment API Service",
        ),
        ("/home/alonur/analyticbot/apps/frontend/src/services/apiClient.js", "API Client"),
    ]

    frontend_results = []
    for file_path, description in frontend_files:
        result = test_file_exists(file_path, description)
        frontend_results.append(result)

    # Configuration Tests
    print("\n⚙️ CONFIGURATION:")
    config_files = [
        ("/home/alonur/analyticbot/apps/frontend/.env.example", "Frontend Environment Example"),
        ("/home/alonur/analyticbot/WEEK_15_16_PAYMENT_SYSTEM_PLAN.md", "Implementation Plan"),
    ]

    config_results = []
    for file_path, description in config_files:
        result = test_file_exists(file_path, description)
        config_results.append(result)

    # Dependencies Test
    print("\n📦 DEPENDENCIES:")
    deps_result = test_package_dependencies()

    # Import Tests
    print("\n🔧 MODULE IMPORTS:")
    import_tests = [
        ("apps.bot.services.stripe_adapter", "Stripe Adapter Import"),
        ("apps.bot.models.payment", "Payment Models Import"),
    ]

    import_results = []
    for module_path, description in import_tests:
        result = test_import_module(module_path, description)
        import_results.append(result)

    # Summary
    print("\n" + "=" * 55)
    print("📊 IMPLEMENTATION SUMMARY")
    print("=" * 55)

    backend_completion = (sum(backend_results) / len(backend_results)) * 100
    frontend_completion = (sum(frontend_results) / len(frontend_results)) * 100
    config_completion = (sum(config_results) / len(config_results)) * 100
    import_completion = (sum(import_results) / len(import_results)) * 100

    print(
        f"Backend Infrastructure: {backend_completion:.1f}% complete ({sum(backend_results)}/{len(backend_results)})"
    )
    print(
        f"Frontend Components: {frontend_completion:.1f}% complete ({sum(frontend_results)}/{len(frontend_results)})"
    )
    print(
        f"Configuration: {config_completion:.1f}% complete ({sum(config_results)}/{len(config_results)})"
    )
    print(
        f"Module Imports: {import_completion:.1f}% complete ({sum(import_results)}/{len(import_results)})"
    )
    print(f"Dependencies: {'✅ Configured' if deps_result else '❌ Missing'}")

    overall_completion = (
        (sum(backend_results) + sum(frontend_results) + sum(config_results) + sum(import_results))
        / (len(backend_results) + len(frontend_results) + len(config_results) + len(import_results))
        * 100
    )

    print(f"\n🎯 OVERALL COMPLETION: {overall_completion:.1f}%")

    if overall_completion >= 90:
        print("🚀 PAYMENT SYSTEM READY FOR DEPLOYMENT!")
        print("📝 Next Steps:")
        print("   1. Configure production Stripe keys")
        print("   2. Set up webhook endpoints")
        print("   3. Test payment flows")
        print("   4. Deploy to production")
    elif overall_completion >= 75:
        print("⚡ PAYMENT SYSTEM MOSTLY COMPLETE!")
        print("📝 Next Steps:")
        print("   1. Complete missing components")
        print("   2. Install frontend dependencies")
        print("   3. Configure environment variables")
        print("   4. Test integration")
    else:
        print("🔧 PAYMENT SYSTEM NEEDS MORE WORK")
        print("📝 Next Steps:")
        print("   1. Address missing files")
        print("   2. Fix import errors")
        print("   3. Complete implementation")


if __name__ == "__main__":
    main()
