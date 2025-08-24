"""Payment routes for the bot API."""

from fastapi import APIRouter

payment_router = APIRouter(tags=["payments"])


@payment_router.get("/status")
async def payment_status():
    """Get payment system status."""
    return {"status": "ok", "message": "Payment system is operational"}


@payment_router.post("/webhook")
async def payment_webhook():
    """Payment webhook handler."""
    return {"status": "received"}
