import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from src.core.config import settings
from src.modules.timecondition.schemas import (
    TimeConditionPayload,
    TimeConditionResponse,
)

logger = logging.getLogger(__name__)


class TimeConditionService:

    async def check(self, payload: TimeConditionPayload) -> TimeConditionResponse:
        try:
            tz = ZoneInfo(payload.timezone)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(f"Invalid timezone: {payload.timezone}")

        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday()

        online = False
        for rng in payload.ranges:
            if current_weekday not in rng.days:
                continue
            if rng.start_hour <= current_time <= rng.end_hour:
                online = True
                break

        status = "on" if online else "off"
        online_str = "true" if online else "false"

        if online:
            msg = f"Time: {current_time} is in the ranges"
        else:
            msg = f"Time: {current_time} is out of the ranges"

        result = TimeConditionResponse(status=status, online=online_str, msg=msg)

        if settings.webhook_tester:
            asyncio.create_task(self._send_to_webhook_tester(result.model_dump()))

        return result

    async def _send_to_webhook_tester(self, data: dict) -> None:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(settings.webhook_tester, json=data)
        except Exception:
            logger.warning("Failed to send data to WEBHOOK_TESTER")
