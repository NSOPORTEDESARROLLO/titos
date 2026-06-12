"""
Pydantic models for request validation and response serialization
in the Example module.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemPayload(BaseModel):
    """
    Schema for creating or updating an item.

    Attributes:
        name: Human-readable item name.
        description: Optional detailed description of the item.
        value: Numeric value associated with the item.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    value: float = Field(..., ge=0, description="Numeric value of the item")


class ItemResponse(BaseModel):
    """
    Schema returned after item operations.

    Attributes:
        id: Unique identifier for the item.
        name: Item name.
        description: Item description.
        value: Item value.
        created_at: ISO timestamp of creation.
    """
    id: str
    name: str
    description: Optional[str] = None
    value: float
    created_at: datetime


class ErrorResponse(BaseModel):
    """
    Standard error payload returned on failures.
    """
    error: bool = True
    detail: str
