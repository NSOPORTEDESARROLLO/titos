"""
REST API router for the Example module.

All endpoints are prefixed with /api/v1/example and require
authentication via Bearer token in the Authorization header.

This router serves as a reference template for creating
new modules. Copy this folder, rename it, and replace
the in-memory service with real external API calls.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import verify_token
from src.modules.example.schemas import ErrorResponse, ItemPayload, ItemResponse
from src.modules.example.service import ExampleService

# Module-level service instance (one per module).
# In a larger deployment, consider dependency injection.
service = ExampleService()

# Router with module-scoped prefix and tags for OpenAPI docs.
router = APIRouter(
    prefix="/api/v1/example",
    tags=["example"],
    dependencies=[Depends(verify_token)],
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid token"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
    },
)


@router.get(
    "/items",
    response_model=list[ItemResponse],
    summary="List all items",
    description="Returns every item currently stored in the example module.",
)
async def list_items():
    """GET /api/v1/example/items — Retrieves all items."""
    return await service.list_items()


@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Creates an item with the provided name, description, and value.",
)
async def create_item(payload: ItemPayload):
    """POST /api/v1/example/items — Creates a new item."""
    return await service.create_item(payload)


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Get an item by ID",
    description="Retrieves a single item using its UUID.",
)
async def get_item(item_id: str):
    """GET /api/v1/example/items/{item_id} — Fetches an item by ID."""
    item = await service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Update an item",
    description="Replaces the data of an existing item identified by its UUID.",
)
async def update_item(item_id: str, payload: ItemPayload):
    """PUT /api/v1/example/items/{item_id} — Updates an existing item."""
    updated = await service.update_item(item_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Removes an item from the store by its UUID.",
)
async def delete_item(item_id: str):
    """DELETE /api/v1/example/items/{item_id} — Deletes an item."""
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
