"""
AnalyticBot API - Main Entry Point
Unified FastAPI application
"""
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="AnalyticBot API", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}

# TODO: Add routers from legacy APIs as needed
# from apis.routers import analytics, security, performance
# app.include_router(analytics.router, prefix="/analytics")
# app.include_router(security.router, prefix="/security") 
# app.include_router(performance.router, prefix="/performance")
