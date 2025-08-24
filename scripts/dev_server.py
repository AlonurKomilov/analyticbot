#!/usr/bin/env python3
"""
Development server for AnalyticBot API
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
