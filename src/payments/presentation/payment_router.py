"""
Payments Presentation Layer
==========================

FastAPI router for payments domain endpoints.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from src.payments.application.services.payment_service import PaymentService
from src.shared_kernel.presentation.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/health")
async def payments_health():
    """Health check for payments service"""
    return {"status": "healthy", "service": "payments"}


@router.post("/process")
async def process_payment(
    payment_data: dict,
    current_user=Depends(get_current_user),
    payment_service: PaymentService = Depends(),
):
    """Process a payment"""
    try:
        result = await payment_service.process_payment(payment_data, current_user.id)
        return {"success": True, "payment_id": result.payment_id}
    except Exception as e:
        logger.error(f"Payment processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
async def get_payment_history(
    current_user=Depends(get_current_user), payment_service: PaymentService = Depends()
):
    """Get payment history for user"""
    try:
        history = await payment_service.get_user_payment_history(current_user.id)
        return {"payments": history}
    except Exception as e:
        logger.error(f"Failed to get payment history: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve payment history")
