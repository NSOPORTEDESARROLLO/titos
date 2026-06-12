# Titos API — Agent guide

## Project overview

Modular FastAPI middleware that receives webhooks from Live Helper Chat and forwards them to the Otobo ticket system.

```
src/
├── core/          # config (pydantic-settings from .env), exceptions, security (Bearer token)
├── modules/       # feature modules — example, lhc2otobo, timecondition
├── shared/        # reusable HTTP client (httpx.AsyncClient wrapper with retries)
└── main.py        # FastAPI app entrypoint — registers routers
tests/
```

## Commands

```bash
# run dev server
uvicorn src.main:app --reload

# run all tests
pytest -v

# run single test file
pytest tests/test_lhc2otobo.py -v

# run single test class
pytest tests/test_lhc2otobo.py::TestWebhookWithFile -v
```

## Key facts

- **Auth**: All endpoints require `Authorization: Bearer <token>`. Token is `AUTH_TOKEN` env var (default from `.env` is `supersecretotoken123`).
- **Port**: 5001
- **Config**: `src/core/config.py` loads from `.env` via `pydantic-settings`. Test conftest overrides `AUTH_TOKEN` and `OTOBO_IP` before importing the app.
- **Adding a module**: Copy `src/modules/example/`, rename classes, update prefix, register router in `src/main.py:57`, add tests, add docs in `docs/en/` and `docs/es/`.
- **Tests**: `conftest.py` provides `client` (TestClient) and `auth_headers` fixtures. The example service resets between tests via `reset_example_service` autouse fixture.
- **lhc2otobo module**: `POST /api/v1/lhc2otobo/updatewithimage`. Input uses `ticketnumber`, `title`, `queue`, `subject`, `additional_data[]` (LHC format). Body is built from `additional_data` based on `menu_principal` (3 or 4). `UserLogin`/`Password` come from `OTOBO_USER`/`OTOBO_PWD` env vars. If `file` (base64) is present, filename is read from `averia_imagen_file` in `additional_data` and converted to an `Attachment` array. Requires `OTOBO_IP` env var.
- **timecondition module**: `POST /api/v1/timecondition`. Receives `ranges` (start_hour, end_hour, days) and `timezone`. Returns whether current time in that timezone falls within any range. Week starts on Monday (day 0). Python `zoneinfo` built-in, no extra deps.
- **WEBHOOK_TESTER**: If set to a valid URL, a copy of the outgoing JSON is POSTed fire-and-forget in the background.
- **Docker**: `python:3.13-slim` based, exposes port 8000, healthcheck on `/health`. Override `PORT` env var at runtime for a different port.
- **Specs**: `specs/proyect.md` and `specs/001-module-lhc2otobo.md` define project rules and the LHC→Otobo flow in Spanish.

## Conventions

- Routes in English, module folders under `src/modules/<name>/`.
- Each module has `router.py`, `schemas.py`, `service.py` (business logic). Optionally `utils.py`.
- Router is a scoped `APIRouter` with `prefix="/api/v1/<module>"` and `tags=[...]`.
- Pydantic models for request/response schemas. `ErrorResponse` model for error payloads.
- `AppException` for business-logic errors (custom status code). Global catch-all returns 500.
- Comments on every route, method, class, and public function (spec rule).
