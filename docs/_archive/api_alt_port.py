"""
🤖 Pure AI/ML API - Alternative Port (8004)

Running the same API on port 8004 for better browser compatibility
"""

import sys

sys.path.insert(0, "/workspaces/analyticbot")
from apps.api.pure_ai_api import app

if __name__ == "__main__":
    import uvicorn

    print("🤖 Starting Pure AI/ML API on Alternative Port 8004...")
    print("📖 Documentation: http://localhost:8004/docs")
    print("🎬 Demo analysis: http://localhost:8004/demo/analyze")
    print("🏥 Health check: http://localhost:8004/health")
    uvicorn.run(app, host="127.0.0.1", port=8004, reload=False, log_level="info")
