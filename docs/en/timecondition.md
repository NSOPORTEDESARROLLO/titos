# Time Condition Module

Checks whether the current server time (in a given timezone) falls within configured time ranges.

## Endpoint

### `POST /api/v1/timecondition`

Requires `Authorization: Bearer <token>` header.

**Request body:**
```json
{
  "ranges": [
    {
      "start_hour": "08:00",
      "end_hour": "12:30",
      "days": [1, 2, 3]
    }
  ],
  "timezone": "America/Costa_Rica"
}
```

**Response `200`:**
```json
{
  "status": "on",
  "online": "true",
  "msg": "Time: 10:30 is in the ranges"
}
```

**Response `400`:** Invalid timezone or malformed range.

## Behavior

- Week starts on Monday (day 0).
- Ranges are checked with string comparison on `HH:MM` format.
- Multiple ranges are supported; if any matches, the result is `online: true`.
- If `WEBHOOK_TESTER` is configured, a copy of the response is POSTed there in the background.
