"""
AnalyticBot API - Main Entry Point
Unified FastAPI application with secure configuration
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import settings

app = FastAPI(
    title="AnalyticBot API", 
    version="v1",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }

# TODO: Add routers from legacy APIs as needed
# from apis.routers import analytics, security, performance
# app.include_router(analytics.router, prefix="/analytics")
# app.include_router(security.router, prefix="/security") 
# app.include_router(performance.router, prefix="/performance")
