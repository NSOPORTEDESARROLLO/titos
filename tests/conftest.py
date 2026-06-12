"""
Pytest configuration and shared fixtures for the test suite.
"""
import os

import pytest
from fastapi.testclient import TestClient

# Ensure we use test settings before importing the app.
os.environ["AUTH_TOKEN"] = "test-token-123"
os.environ["OTOBO_IP"] = "otobo-test.example.com"
os.environ["OTOBO_USER"] = "test-otobo-user"
os.environ["OTOBO_PWD"] = "test-otobo-pass"

from src.main import app  # noqa: E402
from src.modules.example.router import service as example_service  # noqa: E402


@pytest.fixture(autouse=True)
def reset_example_service():
    """
    Resets the in-memory service state before every test
    to prevent test interdependence.
    """
    example_service.reset()


@pytest.fixture
def client():
    """
    Provides a TestClient instance pointed at the main FastAPI app.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    """
    Returns valid Authorization headers for test requests.
    """
    return {"Authorization": "Bearer test-token-123"}
