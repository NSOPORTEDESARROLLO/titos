from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import status

from src.modules.lhc2otobo.router import service
from src.modules.lhc2otobo.schemas import AdditionalDataItem, LhcWebhookPayload
from src.modules.lhc2otobo.utils import (
    build_body,
    detect_image_info,
    extract_filename,
    get_additional_value,
)

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

ADDITIONAL_DATA_3 = [
    AdditionalDataItem(key="menu_principal", identifier="menu_principal", value="3"),
    AdditionalDataItem(key="numero_medidor", identifier="numero_medidor", value="12345"),
    AdditionalDataItem(key="numero_telefono", identifier="numero_telefono", value="555-1234"),
    AdditionalDataItem(key="nombre_usuario", identifier="nombre_usuario", value="Juan Perez"),
    AdditionalDataItem(key="descripcion_averia", identifier="descripcion_averia", value="Cable caido"),
    AdditionalDataItem(key="averia_imagen_file", identifier="averia_imagen_file", value="[file=1071_89d1d83fea0945cb3cc27c72849531b4]"),
]

ADDITIONAL_DATA_4 = [
    AdditionalDataItem(key="menu_principal", identifier="menu_principal", value="4"),
    AdditionalDataItem(key="numero_suscriptor", identifier="numero_suscriptor", value="98765"),
    AdditionalDataItem(key="numero_telefono", identifier="numero_telefono", value="555-5678"),
    AdditionalDataItem(key="nombre_usuario", identifier="nombre_usuario", value="Maria Lopez"),
    AdditionalDataItem(key="descripcion_averia", identifier="descripcion_averia", value="Transformador danado"),
    AdditionalDataItem(key="averia_imagen_file", identifier="averia_imagen_file", value="[file=abcd1234]"),
]

ADDITIONAL_DATA_NO_FILE = [
    AdditionalDataItem(key="menu_principal", identifier="menu_principal", value="3"),
    AdditionalDataItem(key="numero_medidor", identifier="numero_medidor", value="99999"),
    AdditionalDataItem(key="numero_telefono", identifier="numero_telefono", value="555-0000"),
    AdditionalDataItem(key="nombre_usuario", identifier="nombre_usuario", value="Test User"),
    AdditionalDataItem(key="descripcion_averia", identifier="descripcion_averia", value="No image"),
]

VALID_PAYLOAD_NO_FILE = {
    "ticketnumber": "2025010112345678",
    "title": "Test ticket",
    "queue": "Support",
    "subject": "Re: Help needed",
    "additional_data": [item.model_dump() for item in ADDITIONAL_DATA_NO_FILE],
}

VALID_PAYLOAD_WITH_FILE = {
    "ticketnumber": "2025010112345678",
    "title": "Test ticket",
    "queue": "Support",
    "subject": "Re: Help needed",
    "additional_data": [item.model_dump() for item in ADDITIONAL_DATA_3],
    "file": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk",
}

PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
JPEG_BASE64 = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U"
GIF_BASE64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
WEBP_BASE64 = "UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAQBtLaAAn"
UNKNOWN_BASE64 = "AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQ"


def _mock_otobo_response(return_data: dict | None = None, status_code: int = 200):
    mock_http_response = MagicMock(spec=httpx.Response)
    mock_http_response.json.return_value = return_data or {
        "TicketID": 123,
        "Status": "successful",
    }
    mock_http_response.status_code = status_code
    mock_http_response.raise_for_status.return_value = None

    mock_post = AsyncMock(return_value=mock_http_response)
    return mock_post


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_missing_token_returns_401(self, client):
        response = client.post(
            "/api/v1/lhc2otobo/updatewithimage", json=VALID_PAYLOAD_NO_FILE
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_returns_401(self, client):
        response = client.post(
            "/api/v1/lhc2otobo/updatewithimage",
            json=VALID_PAYLOAD_NO_FILE,
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Utils: get_additional_value
# ---------------------------------------------------------------------------

class TestGetAdditionalValue:

    def test_finds_existing_key(self):
        result = get_additional_value(ADDITIONAL_DATA_3, "numero_medidor")
        assert result == "12345"

    def test_returns_none_for_missing_key(self):
        result = get_additional_value(ADDITIONAL_DATA_3, "nonexistent")
        assert result is None


# ---------------------------------------------------------------------------
# Utils: build_body
# ---------------------------------------------------------------------------

BODY_3 = (
    "Medidor : 12345\n"
    "Telefono : 555-1234\n"
    "Nombre: Juan Perez\n"
    "Descripcion: Cable caido"
)

BODY_4 = (
    "Suscriptor : 98765\n"
    "Telefono : 555-5678\n"
    "Nombre: Maria Lopez\n"
    "Descripcion: Transformador danado"
)


class TestBuildBody:

    def test_menu_3_format(self):
        assert build_body(ADDITIONAL_DATA_3) == BODY_3

    def test_menu_4_format(self):
        assert build_body(ADDITIONAL_DATA_4) == BODY_4

    def test_empty_body_for_unknown_menu(self):
        data = [AdditionalDataItem(key="menu_principal", identifier="menu_principal", value="99")]
        assert build_body(data) == ""


# ---------------------------------------------------------------------------
# Utils: extract_filename
# ---------------------------------------------------------------------------

class TestExtractFilename:

    def test_uses_averia_imagen_file_strips_prefix(self):
        name = extract_filename(ADDITIONAL_DATA_3, "png")
        assert name == "1071_89d1d83fea0945cb3cc27c72849531b4.png"

    def test_handles_value_without_prefix(self):
        data = [AdditionalDataItem(key="averia_imagen_file", identifier="averia_imagen_file", value="plainname")]
        name = extract_filename(data, "jpg")
        assert name == "plainname.jpg"

    def test_fallback_when_key_missing(self):
        name = extract_filename([], "jpg")
        assert name.endswith(".jpg")
        assert len(name) == 12 + 4

    def test_uses_correct_extension(self):
        name = extract_filename(ADDITIONAL_DATA_3, "jpeg")
        assert name.endswith(".jpeg")


# ---------------------------------------------------------------------------
# Utils: detect_image_info
# ---------------------------------------------------------------------------

class TestDetectImageInfo:

    def test_png_magic_bytes(self):
        ct, data, ext = detect_image_info(PNG_BASE64)
        assert ct == "image/png"
        assert ext == "png"
        assert data == PNG_BASE64

    def test_jpeg_magic_bytes(self):
        ct, data, ext = detect_image_info(JPEG_BASE64)
        assert ct == "image/jpeg"
        assert ext == "jpg"
        assert data == JPEG_BASE64

    def test_gif_magic_bytes(self):
        ct, data, ext = detect_image_info(GIF_BASE64)
        assert ct == "image/gif"
        assert ext == "gif"

    def test_webp_magic_bytes(self):
        ct, data, ext = detect_image_info(WEBP_BASE64)
        assert ct == "image/webp"
        assert ext == "webp"

    def test_unknown_format_falls_back_to_png(self):
        ct, data, ext = detect_image_info(UNKNOWN_BASE64)
        assert ct == "image/png"
        assert ext == "png"


# ---------------------------------------------------------------------------
# Webhook processing: without file
# ---------------------------------------------------------------------------

class TestWebhookWithoutFile:

    def test_forwards_payload_with_env_credentials(self, client, auth_headers):
        mock_post = _mock_otobo_response()
        with patch.object(service._client, "post", mock_post):
            response = client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=VALID_PAYLOAD_NO_FILE,
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        mock_post.assert_called_once()
        _url, kwargs = mock_post.call_args
        sent = kwargs["json"]

        assert sent["UserLogin"] == "test-otobo-user"
        assert sent["Password"] == "test-otobo-pass"
        assert sent["TicketNumber"] == "2025010112345678"
        assert sent["Ticket"]["Title"] == "Test ticket"
        assert sent["Ticket"]["Queue"] == "Support"
        assert sent["Article"]["Subject"] == "Re: Help needed"
        assert "No image" in sent["Article"]["Body"]
        assert sent["Article"]["ContentType"] == "text/plain; charset=utf8"
        assert "Attachment" not in sent

    def test_returns_otobo_response_verbatim(self, client, auth_headers):
        otobo_response = {"TicketID": 999, "Status": "created"}
        mock_post = _mock_otobo_response(otobo_response)
        with patch.object(service._client, "post", mock_post):
            response = client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=VALID_PAYLOAD_NO_FILE,
                headers=auth_headers,
            )
        assert response.json() == otobo_response


# ---------------------------------------------------------------------------
# Webhook processing: with file
# ---------------------------------------------------------------------------

class TestWebhookWithFile:

    def test_adds_attachment_with_correct_filename(self, client, auth_headers):
        mock_post = _mock_otobo_response()
        with patch.object(service._client, "post", mock_post) as mock:
            response = client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=VALID_PAYLOAD_WITH_FILE,
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        mock.assert_called_once()
        _url, kwargs = mock.call_args
        sent = kwargs["json"]

        assert "Attachment" in sent
        assert len(sent["Attachment"]) == 1
        att = sent["Attachment"][0]
        assert att["ContentType"] == "image/png"
        assert att["Content"] == PNG_BASE64
        assert att["Filename"] == "1071_89d1d83fea0945cb3cc27c72849531b4.png"
        assert "file=" not in att["Filename"]
        assert "[" not in att["Filename"]
        assert "]" not in att["Filename"]

    def test_detects_format_from_magic_bytes(self, client, auth_headers):
        payload = {**VALID_PAYLOAD_WITH_FILE, "file": JPEG_BASE64}
        mock_post = _mock_otobo_response()
        with patch.object(service._client, "post", mock_post) as mock:
            client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=payload,
                headers=auth_headers,
            )
        _url, kwargs = mock.call_args
        att = kwargs["json"]["Attachment"][0]
        assert att["ContentType"] == "image/jpeg"
        assert att["Filename"].endswith(".jpg")

    def test_body_is_built_from_additional_data(self, client, auth_headers):
        payload = {**VALID_PAYLOAD_WITH_FILE}
        mock_post = _mock_otobo_response()
        with patch.object(service._client, "post", mock_post) as mock:
            client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=payload,
                headers=auth_headers,
            )
        _url, kwargs = mock.call_args
        assert kwargs["json"]["Article"]["Body"] == (
            "Medidor : 12345\n"
            "Telefono : 555-1234\n"
            "Nombre: Juan Perez\n"
            "Descripcion: Cable caido"
        )


# ---------------------------------------------------------------------------
# Webhook processing: WEBHOOK_TESTER
# ---------------------------------------------------------------------------

class TestWebhookTester:

    def test_sends_copy_when_tester_url_is_set(self, client, auth_headers):
        with patch.object(service, "_send_to_webhook_tester") as mock_tester:
            mock_post = _mock_otobo_response()
            with patch.object(service._client, "post", mock_post):
                with patch("src.modules.lhc2otobo.service.settings.webhook_tester", "https://tester.example.com/hook"):
                    client.post(
                        "/api/v1/lhc2otobo/updatewithimage",
                        json=VALID_PAYLOAD_WITH_FILE,
                        headers=auth_headers,
                    )

            mock_tester.assert_called_once()
            sent = mock_tester.call_args[0][0]
            assert sent["TicketNumber"] == "2025010112345678"
            assert "Attachment" in sent

    def test_skips_when_tester_url_is_empty(self, client, auth_headers):
        with patch.object(service, "_send_to_webhook_tester") as mock_tester:
            mock_post = _mock_otobo_response()
            with patch.object(service._client, "post", mock_post):
                with patch("src.modules.lhc2otobo.service.settings.webhook_tester", ""):
                    client.post(
                        "/api/v1/lhc2otobo/updatewithimage",
                        json=VALID_PAYLOAD_NO_FILE,
                        headers=auth_headers,
                    )

            mock_tester.assert_not_called()

    def test_send_to_webhook_tester_makes_post_request(self):
        import asyncio
        from src.modules.lhc2otobo.service import Lhc2OtoboService
        svc = Lhc2OtoboService()
        test_data = {"test": "data"}
        with patch("src.modules.lhc2otobo.service.settings.webhook_tester", "https://tester.example.com"):
            with patch("httpx.AsyncClient.post") as mock_httpx_post:
                asyncio.run(svc._send_to_webhook_tester(test_data))
                mock_httpx_post.assert_called_once_with(
                    "https://tester.example.com", json=test_data
                )


# ---------------------------------------------------------------------------
# Error scenarios
# ---------------------------------------------------------------------------

class TestWebhookErrors:

    def test_missing_otobo_ip_returns_500(self, client, auth_headers):
        with patch("src.modules.lhc2otobo.service.settings.otobo_ip", ""):
            response = client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=VALID_PAYLOAD_NO_FILE,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "OTOBO_IP" in response.json()["detail"]

    def test_upstream_failure_returns_500(self, client, auth_headers):
        mock_exception = httpx.HTTPStatusError(
            "502 Bad Gateway",
            request=MagicMock(),
            response=MagicMock(status_code=502),
        )
        mock_post = AsyncMock(side_effect=mock_exception)
        with patch.object(service._client, "post", mock_post):
            response = client.post(
                "/api/v1/lhc2otobo/updatewithimage",
                json=VALID_PAYLOAD_NO_FILE,
                headers=auth_headers,
            )
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
