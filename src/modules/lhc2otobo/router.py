"""
REST API router for the lhc2otobo module.

Provides a single endpoint that receives webhook calls from
Live Helper Chat and forwards them to the Otobo ticket system.

All requests require authentication via Bearer token.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import verify_token
from src.modules.lhc2otobo.schemas import ErrorResponse, LhcWebhookPayload
from src.modules.lhc2otobo.service import Lhc2OtoboService

# Module-level service instance.
service = Lhc2OtoboService()

router = APIRouter(
    prefix="/api/v1/lhc2otobo",
    tags=["lhc2otobo"],
    dependencies=[Depends(verify_token)],
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid token"},
        500: {"model": ErrorResponse, "description": "Internal or upstream error"},
    },
)


@router.post(
    "/updatewithimage",
    summary="Forward LHC webhook to Otobo",
    description=(
        "Receives a ticket update payload from Live Helper Chat. "
        "If a File field with base64 image data is present, it is "
        "converted into an Otobo-compatible Attachment structure. "
        "Returns the Otobo API response verbatim."
    ),
)
async def update_with_image(payload: LhcWebhookPayload):
    """
    POST /api/v1/lhc2otobo/updatewithimage

    Processes a Live Helper Chat webhook and relays it to Otobo.
    """
    try:
        result = await service.process_webhook(payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error communicating with Otobo: {e}",
        )
