import asyncio
import logging
from typing import Optional

import httpx

from src.core.config import settings
from src.modules.lhc2otobo.schemas import LhcWebhookPayload
from src.modules.lhc2otobo.utils import build_body, detect_image_info, extract_filename
from src.shared.http_client import HttpClient

logger = logging.getLogger(__name__)

OTOBO_PATH = (
    "/otobo/nph-genericinterface.pl/Webservice/Ticket/TicketUpdate/TicketID"
)


class Lhc2OtoboService:

    def __init__(self, http_client: Optional[HttpClient] = None):
        self._client = http_client or HttpClient(
            timeout=settings.otobo_timeout,
            verify=settings.otobo_verify_ssl,
        )

    def _build_otobo_url(self) -> str:
        ip = settings.otobo_ip
        if not ip:
            raise ValueError("OTOBO_IP environment variable is not set")
        return f"https://{ip}{OTOBO_PATH}"

    async def process_webhook(self, payload: LhcWebhookPayload) -> dict:
        url = self._build_otobo_url()

        body = build_body(payload.additional_data)

        otobo_data = {
            "UserLogin": settings.otobo_user,
            "Password": settings.otobo_pwd,
            "TicketNumber": payload.ticketnumber,
            "Ticket": {
                "Title": payload.title,
                "Queue": payload.queue,
            },
            "Article": {
                "Subject": payload.subject,
                "Body": body,
                "ContentType": "text/plain; charset=utf8",
            },
        }

        if payload.file:
            content_type, clean_base64, ext = detect_image_info(payload.file)
            filename = extract_filename(payload.additional_data, ext)
            otobo_data["Attachment"] = [
                {
                    "ContentType": content_type,
                    "Filename": filename,
                    "Content": clean_base64,
                }
            ]

        if settings.webhook_tester:
            asyncio.create_task(self._send_to_webhook_tester(otobo_data))

        response = await self._client.post(url, json=otobo_data)
        return response.json()

    async def _send_to_webhook_tester(self, data: dict) -> None:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(settings.webhook_tester, json=data)
        except Exception:
            logger.warning("Failed to send data to WEBHOOK_TESTER")
