# Titos API

Modular middleware API for integrating external systems. Receives webhooks from [Live Helper Chat](https://livehelperchat.com/) and forwards them to the [Otobo](https://otobo.io/) ticket system, among other utilities.

## Modules

| Module | Endpoint | Description |
|---|---|---|
| lhc2otobo | `POST /api/v1/lhc2otobo/updatewithimage` | Forwards LHC ticket updates to Otobo with optional image attachment |
| timecondition | `POST /api/v1/timecondition` | Checks if current time falls within configured ranges for a given timezone |
| example | `CRUD /api/v1/example/items` | Reference template for creating new modules |

## Quick start

```bash
cp .env.example .env
# edit .env with your settings
uvicorn src.main:app --reload
```

## Docker

```bash
docker build -t titos-api .
docker run -p 5001:8000 --env-file .env titos-api
```

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `AUTH_TOKEN` | Yes | — | Bearer token for API authentication |
| `OTOBO_IP` | For lhc2otobo | — | Otobo server hostname/IP |
| `OTOBO_USER` | For lhc2otobo | — | Otobo login |
| `OTOBO_PWD` | For lhc2otobo | — | Otobo password |
| `OTOBO_TIMEOUT` | No | `30` | HTTP timeout in seconds for Otobo requests |
| `OTOBO_VERIFY_SSL` | No | `true` | Set to `false` to skip SSL verification (self-signed certs) |
| `WEBHOOK_TESTER` | No | — | URL for fire-and-forget copy of outgoing payloads |
| `HOST` | No | `0.0.0.0` | Bind address |
| `PORT` | No | `5001` | Listen port |

## Architecture

```
src/
├── core/       # Config, auth, exception handlers
├── modules/    # Feature modules
├── shared/     # Reusable HTTP client
└── main.py     # App entrypoint
tests/
docs/
```

Every module follows the same pattern: `router.py` → `schemas.py` → `service.py`.

## Authentication

All endpoints require `Authorization: Bearer <token>`. Use the value of `AUTH_TOKEN` from your `.env` file.

## Tests

```bash
pytest -v
```

## Docs

Extended documentation in English and Spanish under `docs/en/` and `docs/es/`.
