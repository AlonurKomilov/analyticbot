#!/bin/bash
# 🔧 Development Environment Setup Script
# Run this script to activate the Python virtual environment and set up development tools

echo "🐍 Activating Python Virtual Environment..."
source /home/alonur/analyticbot/venv/bin/activate

echo "✅ Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Virtual environment path: $(which python)"

echo "📦 Installed packages:"
echo "  - FastAPI: $(python -c 'import fastapi; print(fastapi.__version__)')"
echo "  - Pydantic: $(python -c 'import pydantic; print(pydantic.__version__)')"
echo "  - Pytest: $(python -c 'import pytest; print(pytest.__version__)')"

echo ""
echo "🚀 You can now run:"
echo "  - API server: uvicorn apps.api.main:app --reload"
echo "  - Tests: pytest"
echo "  - Bot: python -m apps.bot.main"

echo ""
echo "💡 Note: Make sure VS Code is using the virtual environment at:"
echo "   /home/alonur/analyticbot/venv/bin/python"
