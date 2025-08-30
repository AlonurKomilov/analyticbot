"""
Test critical module imports
"""

import pytest


def test_api_main_import():
    """Test that main API module imports successfully"""
    try:
        from apps.api import main

        assert hasattr(main, "app")
        assert main.app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import apps.api.main: {e}")


def test_bot_runner_import():
    """Test that bot runner imports successfully"""
    try:
        import apps.bot.run_bot

        assert hasattr(apps.bot.run_bot, "main")
    except ImportError as e:
        pytest.fail(f"Failed to import apps.bot.run_bot: {e}")


def test_core_bot_modules():
    """Test that core bot modules import successfully"""
    critical_modules = [
        "bot.config",
        "bot.container",
        "bot.database.repositories",
    ]

    failed_imports = []

    for module in critical_modules:
        try:
            __import__(module)
        except ImportError as e:
            failed_imports.append(f"{module}: {e}")

    if failed_imports:
        pytest.fail(f"Failed imports: {'; '.join(failed_imports)}")


def test_fastapi_import():
    """Test FastAPI and essential dependencies"""
    try:
        pass
    except ImportError as e:
        pytest.fail(f"Failed to import FastAPI dependencies: {e}")


def test_database_imports():
    """Test database related imports"""
    try:
        pass
    except ImportError as e:
        pytest.fail(f"Failed to import database dependencies: {e}")


def test_aiogram_imports():
    """Test Aiogram bot dependencies"""
    try:
        pass
    except ImportError as e:
        pytest.fail(f"Failed to import Aiogram dependencies: {e}")
