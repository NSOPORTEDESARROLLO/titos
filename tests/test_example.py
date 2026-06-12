"""
Tests for the Example module endpoints.

Covers:
    - Authentication (missing/invalid token)
    - CRUD operations (create, read, update, delete)
    - Error cases (404 on non-existent item)
"""
from fastapi import status


class TestAuthentication:
    """Verify that all endpoints require a valid Bearer token."""

    def test_missing_token_returns_401(self, client):
        """GET /api/v1/example/items without token should return 401."""
        response = client.get("/api/v1/example/items")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_returns_401(self, client):
        """GET /api/v1/example/items with wrong token should return 401."""
        response = client.get(
            "/api/v1/example/items",
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_header_format_returns_401(self, client):
        """Authorization header without 'Bearer' prefix should return 401."""
        response = client.get(
            "/api/v1/example/items",
            headers={"Authorization": "Token test-token-123"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateItem:
    """Tests for POST /api/v1/example/items."""

    def test_create_item_success(self, client, auth_headers):
        """Creating a valid item should return 201 with the item data."""
        payload = {"name": "Test Item", "description": "A test", "value": 42.5}
        response = client.post("/api/v1/example/items", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["value"] == 42.5
        assert "id" in data
        assert "created_at" in data

    def test_create_item_missing_name_returns_422(self, client, auth_headers):
        """Payload without required 'name' field should return 422."""
        payload = {"value": 10}
        response = client.post("/api/v1/example/items", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_item_negative_value_returns_422(self, client, auth_headers):
        """Negative value should fail validation (ge=0)."""
        payload = {"name": "Bad", "value": -1}
        response = client.post("/api/v1/example/items", json=payload, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetItem:
    """Tests for GET /api/v1/example/items/{item_id}."""

    def test_get_existing_item(self, client, auth_headers):
        """Retrieving an existing item should return it."""
        create_resp = client.post(
            "/api/v1/example/items",
            json={"name": "Get Test", "value": 100},
            headers=auth_headers,
        )
        item_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/example/items/{item_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Get Test"

    def test_get_nonexistent_item_returns_404(self, client, auth_headers):
        """A random UUID that does not exist should return 404."""
        response = client.get(
            "/api/v1/example/items/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateItem:
    """Tests for PUT /api/v1/example/items/{item_id}."""

    def test_update_existing_item(self, client, auth_headers):
        """Updating an existing item should return the updated data."""
        create_resp = client.post(
            "/api/v1/example/items",
            json={"name": "Before", "value": 1},
            headers=auth_headers,
        )
        item_id = create_resp.json()["id"]

        response = client.put(
            f"/api/v1/example/items/{item_id}",
            json={"name": "After", "value": 999},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "After"
        assert response.json()["value"] == 999

    def test_update_nonexistent_item_returns_404(self, client, auth_headers):
        """Updating a non-existent item should return 404."""
        response = client.put(
            "/api/v1/example/items/00000000-0000-0000-0000-000000000000",
            json={"name": "Ghost", "value": 0},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteItem:
    """Tests for DELETE /api/v1/example/items/{item_id}."""

    def test_delete_existing_item(self, client, auth_headers):
        """Deleting an existing item should return 204."""
        create_resp = client.post(
            "/api/v1/example/items",
            json={"name": "Delete Me", "value": 0},
            headers=auth_headers,
        )
        item_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/example/items/{item_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify item is gone.
        get_resp = client.get(f"/api/v1/example/items/{item_id}", headers=auth_headers)
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_item_returns_404(self, client, auth_headers):
        """Deleting a non-existent item should return 404."""
        response = client.delete(
            "/api/v1/example/items/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListItems:
    """Tests for GET /api/v1/example/items."""

    def test_list_empty(self, client, auth_headers):
        """Initially the item list should be empty."""
        response = client.get("/api/v1/example/items", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_returns_all_items(self, client, auth_headers):
        """After creating two items, the list should contain both."""
        client.post("/api/v1/example/items", json={"name": "A", "value": 1}, headers=auth_headers)
        client.post("/api/v1/example/items", json={"name": "B", "value": 2}, headers=auth_headers)

        response = client.get("/api/v1/example/items", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
