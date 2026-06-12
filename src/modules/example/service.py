"""
Business logic for the Example module.
Contains in-memory storage operations as a reference pattern.
When connecting to real external systems, replace the internal dict
with calls to HttpClient methods (see shared/http_client.py).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from src.modules.example.schemas import ItemPayload, ItemResponse


class ExampleService:
    """
    Service class that encapsulates all business rules for the Example module.

    This implementation uses an in-memory dictionary as a simple store.
    To integrate with an external API, replace method bodies with
    HttpClient calls (e.g., self._client.post("/items", json=...)).
    """

    def __init__(self):
        # In-memory store: mapping of item_id -> ItemResponse
        self._store: dict[str, ItemResponse] = {}

    async def create_item(self, payload: ItemPayload) -> ItemResponse:
        """
        Creates a new item with a generated UUID and current timestamp.

        Args:
            payload: validated item data from the request body.

        Returns:
            ItemResponse with the generated id and creation timestamp.
        """
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        item = ItemResponse(
            id=item_id,
            name=payload.name,
            description=payload.description,
            value=payload.value,
            created_at=now,
        )
        self._store[item_id] = item
        return item

    async def get_item(self, item_id: str) -> Optional[ItemResponse]:
        """
        Retrieves an item by its unique identifier.

        Args:
            item_id: UUID string of the item.

        Returns:
            ItemResponse if found, or None if the item does not exist.
        """
        return self._store.get(item_id)

    async def list_items(self) -> list[ItemResponse]:
        """
        Returns all stored items.

        Returns:
            A list (possibly empty) of all ItemResponse objects.
        """
        return list(self._store.values())

    async def update_item(
        self, item_id: str, payload: ItemPayload
    ) -> Optional[ItemResponse]:
        """
        Updates an existing item with new data.

        Args:
            item_id: UUID string of the item to update.
            payload: new item data.

        Returns:
            Updated ItemResponse if the item exists, or None otherwise.
        """
        existing = self._store.get(item_id)
        if existing is None:
            return None
        updated = ItemResponse(
            id=item_id,
            name=payload.name,
            description=payload.description,
            value=payload.value,
            created_at=existing.created_at,
        )
        self._store[item_id] = updated
        return updated

    async def delete_item(self, item_id: str) -> bool:
        """
        Deletes an item by its unique identifier.

        Args:
            item_id: UUID string of the item to delete.

        Returns:
            True if the item was removed, False if it did not exist.
        """
        if item_id in self._store:
            del self._store[item_id]
            return True
        return False

    def reset(self):
        """
        Clears all stored items. Useful for testing isolation.
        """
        self._store.clear()
