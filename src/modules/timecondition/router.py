from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import verify_token
from src.modules.timecondition.schemas import (
    ErrorResponse,
    TimeConditionPayload,
    TimeConditionResponse,
)
from src.modules.timecondition.service import TimeConditionService

service = TimeConditionService()

router = APIRouter(
    prefix="/api/v1/timecondition",
    tags=["timecondition"],
    dependencies=[Depends(verify_token)],
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid token"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
    },
)


@router.post(
    "",
    response_model=TimeConditionResponse,
    summary="Check if current time falls within configured ranges",
    description=(
        "Given a list of time ranges, a timezone, and the current server time, "
        "returns whether the current time is within any of the specified ranges."
    ),
)
async def check_time(payload: TimeConditionPayload):
    try:
        return await service.check(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
