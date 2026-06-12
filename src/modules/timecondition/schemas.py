from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    start_hour: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_hour: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    days: list[int]


class TimeConditionPayload(BaseModel):
    ranges: list[TimeRange]
    timezone: str


class TimeConditionResponse(BaseModel):
    status: str
    online: str
    msg: str


class ErrorResponse(BaseModel):
    error: bool = True
    detail: str
