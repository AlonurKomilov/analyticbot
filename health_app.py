# health_app.py
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
