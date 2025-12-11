#!/usr/bin/env python3
"""
Credit System Setup Verification Script
========================================

This script verifies that the credit system is properly set up:
1. Checks if migrations have been applied
2. Verifies seeded data exists
3. Tests basic credit operations
4. Reports any issues

Usage:
    python scripts/verify_credit_system.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal


async def main():
    print("=" * 60)
    print("🔍 Credit System Verification")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Connect to database
    try:
        import asyncpg
        from config.settings import settings
        
        # Convert async URL to sync URL if needed
        db_url = settings.DATABASE_URL
        if '+asyncpg' in db_url:
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        pool = await asyncpg.create_pool(db_url)
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1
    
    try:
        # ============================================
        # Check Tables Exist
        # ============================================
        print("\n📋 Checking tables...")
        
        required_tables = [
            "user_credits",
            "credit_transactions",
            "credit_packages",
            "credit_services",
            "achievements",
            "user_achievements",
            "user_referrals",
            "marketplace_items",
            "user_purchases",
            "marketplace_bundles",
            "bundle_items",
            "item_reviews",
        ]
        
        for table in required_tables:
            exists = await pool.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = $1
                )
            """, table)
            
            if exists:
                print(f"  ✅ {table}")
            else:
                errors.append(f"Table '{table}' does not exist")
                print(f"  ❌ {table} - MISSING")
        
        # ============================================
        # Check User Columns
        # ============================================
        print("\n📋 Checking users table columns...")
        
        required_columns = ["credit_balance", "referral_code", "referred_by_user_id"]
        
        for column in required_columns:
            exists = await pool.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = $1
                )
            """, column)
            
            if exists:
                print(f"  ✅ users.{column}")
            else:
                errors.append(f"Column 'users.{column}' does not exist")
                print(f"  ❌ users.{column} - MISSING")
        
        # ============================================
        # Check Seeded Data
        # ============================================
        print("\n📋 Checking seeded data...")
        
        # Credit Packages
        package_count = await pool.fetchval("SELECT COUNT(*) FROM credit_packages")
        if package_count >= 4:
            print(f"  ✅ Credit packages: {package_count}")
        else:
            warnings.append(f"Only {package_count} credit packages found (expected 4+)")
            print(f"  ⚠️ Credit packages: {package_count} (expected 4+)")
        
        # Credit Services
        service_count = await pool.fetchval("SELECT COUNT(*) FROM credit_services")
        if service_count >= 10:
            print(f"  ✅ Credit services: {service_count}")
        else:
            warnings.append(f"Only {service_count} credit services found (expected 10+)")
            print(f"  ⚠️ Credit services: {service_count} (expected 10+)")
        
        # Achievements
        achievement_count = await pool.fetchval("SELECT COUNT(*) FROM achievements")
        if achievement_count >= 15:
            print(f"  ✅ Achievements: {achievement_count}")
        else:
            warnings.append(f"Only {achievement_count} achievements found (expected 15+)")
            print(f"  ⚠️ Achievements: {achievement_count} (expected 15+)")
        
        # Marketplace Items
        item_count = await pool.fetchval("SELECT COUNT(*) FROM marketplace_items")
        if item_count >= 15:
            print(f"  ✅ Marketplace items: {item_count}")
        else:
            warnings.append(f"Only {item_count} marketplace items found (expected 15+)")
            print(f"  ⚠️ Marketplace items: {item_count} (expected 15+)")
        
        # Marketplace Bundles
        bundle_count = await pool.fetchval("SELECT COUNT(*) FROM marketplace_bundles")
        if bundle_count >= 5:
            print(f"  ✅ Marketplace bundles: {bundle_count}")
        else:
            warnings.append(f"Only {bundle_count} bundles found (expected 5+)")
            print(f"  ⚠️ Marketplace bundles: {bundle_count} (expected 5+)")
        
        # Bundle Items (links bundles to credit services)
        bundle_item_count = await pool.fetchval("SELECT COUNT(*) FROM bundle_items")
        print(f"  ℹ️ Bundle items linked: {bundle_item_count} (optional)")
        
        # ============================================
        # Test Basic Operations
        # ============================================
        print("\n📋 Testing basic operations...")
        
        # Test credit repository
        try:
            from infra.db.repositories.credit_repository import CreditRepository
            credit_repo = CreditRepository(pool)
            
            # Test get_packages
            packages = await credit_repo.get_packages()
            if len(packages) > 0:
                print(f"  ✅ get_packages() works - {len(packages)} packages")
            else:
                warnings.append("get_packages() returned empty list")
                print("  ⚠️ get_packages() returned empty list")
            
            # Test get_services
            services = await credit_repo.get_services()
            if len(services) > 0:
                print(f"  ✅ get_services() works - {len(services)} services")
            else:
                warnings.append("get_services() returned empty list")
                print("  ⚠️ get_services() returned empty list")
            
            # Test get_all_achievements
            achievements = await credit_repo.get_all_achievements()
            if len(achievements) > 0:
                print(f"  ✅ get_all_achievements() works - {len(achievements)} achievements")
            else:
                warnings.append("get_all_achievements() returned empty list")
                print("  ⚠️ get_all_achievements() returned empty list")
            
        except Exception as e:
            errors.append(f"Credit repository test failed: {e}")
            print(f"  ❌ Credit repository test failed: {e}")
        
        # Test marketplace repository
        try:
            from infra.db.repositories.marketplace_repository import MarketplaceRepository
            marketplace_repo = MarketplaceRepository(pool)
            
            # Test get_items
            items = await marketplace_repo.get_items()
            if len(items) > 0:
                print(f"  ✅ get_items() works - {len(items)} items")
            else:
                warnings.append("get_items() returned empty list")
                print("  ⚠️ get_items() returned empty list")
            
            # Test get_categories
            categories = await marketplace_repo.get_categories()
            if len(categories) > 0:
                print(f"  ✅ get_categories() works - {len(categories)} categories")
            else:
                warnings.append("get_categories() returned empty list")
                print("  ⚠️ get_categories() returned empty list")
            
            # Test get_bundles
            bundles = await marketplace_repo.get_bundles()
            if len(bundles) > 0:
                print(f"  ✅ get_bundles() works - {len(bundles)} bundles")
            else:
                warnings.append("get_bundles() returned empty list")
                print("  ⚠️ get_bundles() returned empty list")
            
        except Exception as e:
            errors.append(f"Marketplace repository test failed: {e}")
            print(f"  ❌ Marketplace repository test failed: {e}")
        
        # ============================================
        # Summary
        # ============================================
        print("\n" + "=" * 60)
        print("📊 Summary")
        print("=" * 60)
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not errors and not warnings:
            print("\n✅ Credit system is fully set up and working!")
            print("\n📝 Next steps:")
            print("   1. Start your API server")
            print("   2. Visit /credits to see the credits page")
            print("   3. Visit /rewards for achievements and referrals")
            print("   4. Visit /marketplace to browse items")
        elif not errors:
            print("\n✅ Credit system is set up but has some minor issues.")
            print("   Consider running the seed migration to add missing data.")
        else:
            print("\n❌ Credit system has critical issues that need to be fixed.")
            print("\n📝 To fix, run:")
            print("   alembic upgrade head")
        
        return 1 if errors else 0
        
    finally:
        await pool.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
