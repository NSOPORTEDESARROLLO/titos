from unittest.mock import MagicMock, patch
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest
from fastapi import status

from src.modules.timecondition.router import service
from src.modules.timecondition.schemas import TimeConditionPayload

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_IN_RANGE_PAYLOAD = {
    "ranges": [
        {"start_hour": "08:00", "end_hour": "12:00", "days": [1, 2, 3]},
    ],
    "timezone": "America/Costa_Rica",
}

_OUT_OF_RANGE_DAY_PAYLOAD = {
    "ranges": [
        {"start_hour": "08:00", "end_hour": "12:00", "days": [1, 2, 3]},
    ],
    "timezone": "America/Costa_Rica",
}

_OUT_OF_RANGE_HOUR_PAYLOAD = {
    "ranges": [
        {"start_hour": "08:00", "end_hour": "12:00", "days": [1, 2, 3]},
    ],
    "timezone": "America/Costa_Rica",
}

_MULTI_RANGE_PAYLOAD = {
    "ranges": [
        {"start_hour": "08:00", "end_hour": "12:00", "days": [1, 2, 3]},
        {"start_hour": "14:00", "end_hour": "18:00", "days": [1, 2, 3]},
    ],
    "timezone": "America/Costa_Rica",
}

# Tuesday 2024-01-02 10:30
TUE_1030 = datetime(2024, 1, 2, 10, 30, tzinfo=ZoneInfo("America/Costa_Rica"))
# Tuesday 2024-01-02 14:30
TUE_1430 = datetime(2024, 1, 2, 14, 30, tzinfo=ZoneInfo("America/Costa_Rica"))
# Tuesday 2024-01-02 17:30
TUE_1730 = datetime(2024, 1, 2, 17, 30, tzinfo=ZoneInfo("America/Costa_Rica"))
# Friday 2024-01-05 10:30 (weekday=4, not in [1,2,3])
FRI_1030 = datetime(2024, 1, 5, 10, 30, tzinfo=ZoneInfo("America/Costa_Rica"))


def _assert_on_response(data: dict):
    assert data["status"] == "on"
    assert data["online"] == "true"
    assert "is in the ranges" in data["msg"]


def _assert_off_response(data: dict):
    assert data["status"] == "off"
    assert data["online"] == "false"
    assert "is out of the ranges" in data["msg"]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_missing_token_returns_401(self, client):
        response = client.post(
            "/api/v1/timecondition", json=_IN_RANGE_PAYLOAD
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_returns_401(self, client):
        response = client.post(
            "/api/v1/timecondition",
            json=_IN_RANGE_PAYLOAD,
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Time range checks
# ---------------------------------------------------------------------------

class TestWithinRange:

    def test_time_within_range(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = TUE_1030
            response = client.post(
                "/api/v1/timecondition",
                json=_IN_RANGE_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_on_response(response.json())

    def test_exact_start_boundary(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(
                2024, 1, 2, 8, 0, tzinfo=ZoneInfo("America/Costa_Rica")
            )
            response = client.post(
                "/api/v1/timecondition",
                json=_IN_RANGE_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_on_response(response.json())

    def test_exact_end_boundary(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(
                2024, 1, 2, 12, 0, tzinfo=ZoneInfo("America/Costa_Rica")
            )
            response = client.post(
                "/api/v1/timecondition",
                json=_IN_RANGE_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_on_response(response.json())


class TestOutOfRange:

    def test_wrong_day(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = FRI_1030
            response = client.post(
                "/api/v1/timecondition",
                json=_OUT_OF_RANGE_DAY_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_off_response(response.json())

    def test_wrong_hour(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = TUE_1430
            response = client.post(
                "/api/v1/timecondition",
                json=_OUT_OF_RANGE_HOUR_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_off_response(response.json())


class TestMultipleRanges:

    def test_matches_second_range(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = TUE_1730
            response = client.post(
                "/api/v1/timecondition",
                json=_MULTI_RANGE_PAYLOAD,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_on_response(response.json())

    def test_no_match_in_any_range(self, client, auth_headers):
        payload = {
            "ranges": [
                {"start_hour": "08:00", "end_hour": "09:00", "days": [1]},
                {"start_hour": "18:00", "end_hour": "20:00", "days": [2]},
            ],
            "timezone": "America/Costa_Rica",
        }
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = TUE_1730
            response = client.post(
                "/api/v1/timecondition",
                json=payload,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_200_OK
        _assert_off_response(response.json())


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

class TestInvalidTimezone:

    def test_invalid_timezone_returns_400(self, client, auth_headers):
        payload = {
            "ranges": [{"start_hour": "08:00", "end_hour": "12:00", "days": [1]}],
            "timezone": "Invalid/Timezone",
        }
        response = client.post(
            "/api/v1/timecondition",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# WEBHOOK_TESTER
# ---------------------------------------------------------------------------

class TestWebhookTester:

    def test_sends_copy_when_tester_url_is_set(self, client, auth_headers):
        with patch.object(service, "_send_to_webhook_tester") as mock_tester:
            with patch("src.modules.timecondition.service.settings.webhook_tester", "https://tester.example.com/hook"):
                with patch("src.modules.timecondition.service.datetime") as mock_dt:
                    mock_dt.now.return_value = TUE_1030
                    client.post(
                        "/api/v1/timecondition",
                        json=_IN_RANGE_PAYLOAD,
                        headers=auth_headers,
                    )

            mock_tester.assert_called_once()
            sent = mock_tester.call_args[0][0]
            assert sent["status"] == "on"
            assert sent["online"] == "true"

    def test_skips_when_tester_url_is_empty(self, client, auth_headers):
        with patch.object(service, "_send_to_webhook_tester") as mock_tester:
            with patch("src.modules.timecondition.service.settings.webhook_tester", ""):
                with patch("src.modules.timecondition.service.datetime") as mock_dt:
                    mock_dt.now.return_value = TUE_1030
                    client.post(
                        "/api/v1/timecondition",
                        json=_IN_RANGE_PAYLOAD,
                        headers=auth_headers,
                    )

            mock_tester.assert_not_called()

    def test_send_to_webhook_tester_makes_post_request(self):
        import asyncio
        from src.modules.timecondition.service import TimeConditionService
        svc = TimeConditionService()
        test_data = {"status": "on", "online": "true", "msg": "test"}
        with patch("src.modules.timecondition.service.settings.webhook_tester", "https://tester.example.com"):
            with patch("httpx.AsyncClient.post") as mock_httpx_post:
                asyncio.run(svc._send_to_webhook_tester(test_data))
                mock_httpx_post.assert_called_once_with(
                    "https://tester.example.com", json=test_data
                )


# ---------------------------------------------------------------------------
# Response format
# ---------------------------------------------------------------------------

class TestResponseFormat:

    def test_response_has_expected_fields(self, client, auth_headers):
        with patch("src.modules.timecondition.service.datetime") as mock_dt:
            mock_dt.now.return_value = TUE_1030
            response = client.post(
                "/api/v1/timecondition",
                json=_IN_RANGE_PAYLOAD,
                headers=auth_headers,
            )
        data = response.json()
        assert "status" in data and isinstance(data["status"], str)
        assert "online" in data and isinstance(data["online"], str)
        assert "msg" in data and isinstance(data["msg"], str)
