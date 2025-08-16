# health_app.py
from typing import Dict

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
