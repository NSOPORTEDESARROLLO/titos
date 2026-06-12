# Example Module

This module serves as a reference template for creating new modules in the Titos API.

## Endpoints

All endpoints are prefixed with `/api/v1/example` and require authentication via `Authorization: Bearer <token>` header.

### `GET /api/v1/example/items`

Returns a list of all items.

**Response `200`:** Array of `ItemResponse` objects.

### `POST /api/v1/example/items`

Creates a new item.

**Request body:**
```json
{
  "name": "Item name",
  "description": "Optional description",
  "value": 42.5
}
```

**Response `201`:** The created `ItemResponse` object.

### `GET /api/v1/example/items/{item_id}`

Retrieves a single item by its UUID.

**Response `200`:** `ItemResponse` object.
**Response `404`:** Item not found.

### `PUT /api/v1/example/items/{item_id}`

Updates an existing item. Same request body as POST.

**Response `200`:** Updated `ItemResponse` object.
**Response `404`:** Item not found.

### `DELETE /api/v1/example/items/{item_id}`

Deletes an item by its UUID.

**Response `204`:** No content (success).
**Response `404`:** Item not found.

## Running the server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
# or
python -m src.main
```

## Creating a new module

1. Copy the `src/modules/example/` folder to `src/modules/your_module/`.
2. Rename the classes and update the router prefix.
3. Replace the in-memory service logic with your external API calls using `HttpClient` from `src/shared/http_client.py`.
4. Register the router in `src/main.py`.
5. Add your tests in `tests/`.
6. Document your module in `docs/en/` and `docs/es/`.
