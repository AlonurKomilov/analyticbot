#!/usr/bin/env python3
"""
MTProto Configuration Checker - Phase 2 Implementation

Simple verification tool that checks configuration without trying to load invalid settings.
"""

import asyncio
import os
import sys
from pathlib import Path


def check_env_file():
    """Check .env file configuration."""
    print("🔍 Checking .env Configuration...")
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
        
    # Read .env file
    with open(env_path) as f:
        env_content = f.read()
        
    # Check for placeholder values
    issues = []
    
    if "YOUR_API_ID_HERE" in env_content:
        issues.append("Replace YOUR_API_ID_HERE with your actual Telegram API ID")
        
    if "YOUR_API_HASH_HERE" in env_content:
        issues.append("Replace YOUR_API_HASH_HERE with your actual Telegram API Hash")
        
    # Check required settings
    required_settings = {
        "MTPROTO_ENABLED": "true",
        "MTPROTO_HISTORY_ENABLED": "true", 
        "MTPROTO_UPDATES_ENABLED": "true",
        "MTPROTO_STATS_ENABLED": "true"
    }
    
    for setting, expected in required_settings.items():
        if f"{setting}={expected}" not in env_content:
            issues.append(f"Set {setting}={expected}")
            
    # Check if credentials are configured
    has_api_id = "TELEGRAM_API_ID=" in env_content and "YOUR_API_ID_HERE" not in env_content
    has_api_hash = "TELEGRAM_API_HASH=" in env_content and "YOUR_API_HASH_HERE" not in env_content
    
    if not has_api_id:
        issues.append("Add real TELEGRAM_API_ID value")
        
    if not has_api_hash:
        issues.append("Add real TELEGRAM_API_HASH value")
        
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
        
    print("✅ .env configuration looks good!")
    return True


def check_project_structure():
    """Check that all required files exist."""
    print("\n📁 Checking Project Structure...")
    
    base_path = Path(__file__).parent.parent
    
    required_files = [
        "apps/mtproto/config.py",
        "apps/mtproto/di.py", 
        "apps/mtproto/collectors/history.py",
        "apps/mtproto/collectors/updates.py",
        "apps/mtproto/tasks/sync_history.py",
        "scripts/mtproto_service.py",
        "docker-compose.yml"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not (base_path / file_path).exists():
            missing_files.append(file_path)
            
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
        
    print("✅ All required files present!")
    return True


def show_setup_instructions():
    """Show step-by-step setup instructions."""
    print("\n🚀 MTProto Real Data Integration Setup Instructions")
    print("=" * 60)
    
    print("\n1. 📋 Get Telegram API Credentials:")
    print("   • Go to https://my.telegram.org/apps")
    print("   • Login with your Telegram account")
    print("   • Create new application or use existing")
    print("   • Copy API ID and API Hash")
    
    print("\n2. 📝 Update .env File:")
    print("   Replace these lines in .env:")
    print("   TELEGRAM_API_ID=YOUR_ACTUAL_API_ID")
    print("   TELEGRAM_API_HASH=YOUR_ACTUAL_API_HASH")
    
    print("\n3. 📺 Add Channels to Monitor:")
    print('   MTPROTO_PEERS=["@channel1","@channel2","-1001234567890"]')
    
    print("\n4. 🧪 Test Configuration:")
    print("   python scripts/check_mtproto_config.py")
    
    print("\n5. 🔐 First-Time Authentication:")
    print("   python scripts/mtproto_service.py test")
    
    print("\n6. 📊 Start Data Collection:")
    print("   python scripts/mtproto_service.py history")
    print("   python scripts/mtproto_service.py updates")
    
    print("\n7. 🐳 Production Deployment:")
    print("   docker-compose --profile mtproto up -d")
    
    print("\n" + "=" * 60)


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        ("telethon", "telethon"),
        ("asyncpg", "asyncpg"), 
        ("pydantic", "pydantic"),
        ("dependency-injector", "dependency_injector")
    ]
    
    missing_packages = []
    
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(display_name)
            
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n   Install with: pip install -r requirements.txt")
        return False
        
    print("✅ All required packages installed!")
    return True


def show_status_summary(config_ok, structure_ok, deps_ok):
    """Show final status summary."""
    print("\n📊 Setup Status Summary")
    print("=" * 30)
    
    status_items = [
        ("Project Structure", structure_ok),
        ("Dependencies", deps_ok), 
        ("Configuration", config_ok)
    ]
    
    all_ok = all(status for _, status in status_items)
    
    for item, status in status_items:
        icon = "✅" if status else "❌"
        print(f"{icon} {item}")
        
    print("=" * 30)
    
    if all_ok:
        print("🎉 Ready for MTProto data collection!")
        print("\nNext step: Run authentication")
        print("python scripts/mtproto_service.py test")
    else:
        print("⚠️  Please fix the issues above before proceeding")
        
    return all_ok


def main():
    """Main configuration checker."""
    print("🎯 MTProto Configuration Checker")
    print("Verifying setup for real Telegram data collection...")
    
    # Check all components
    structure_ok = check_project_structure()
    deps_ok = check_dependencies() 
    config_ok = check_env_file()
    
    # Show status summary
    ready = show_status_summary(config_ok, structure_ok, deps_ok)
    
    if not ready:
        show_setup_instructions()
        sys.exit(1)
    else:
        print("\n🚀 System is ready for real data collection!")
        print("\nRun this to test authentication:")
        print("python scripts/mtproto_service.py test")
        sys.exit(0)


if __name__ == "__main__":
    main()
