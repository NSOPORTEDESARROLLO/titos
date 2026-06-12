from typing import Optional

from pydantic import BaseModel, Field


class AdditionalDataItem(BaseModel):
    key: str
    identifier: str
    value: str


class LhcWebhookPayload(BaseModel):
    ticketnumber: str
    title: str
    queue: str
    subject: str
    additional_data: list[AdditionalDataItem]
    file: Optional[str] = None


class Attachment(BaseModel):
    ContentType: str
    Filename: str
    Content: str


class ErrorResponse(BaseModel):
    error: bool = True
    detail: str
