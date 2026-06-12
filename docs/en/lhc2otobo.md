# lhc2otobo Module

Receives webhook payloads from Live Helper Chat, transforms them into the Otobo ticket update format, and forwards them. Supports optional image attachment.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OTOBO_IP` | Hostname or IP of the Otobo server | Yes |
| `OTOBO_USER` | Otobo user login | Yes |
| `OTOBO_PWD` | Otobo user password | Yes |
| `WEBHOOK_TESTER` | URL for fire-and-forget copy of outgoing payload (optional) | No |

The Otobo URL is built automatically as:
```
https://{OTOBO_IP}/otobo/nph-genericinterface.pl/Webservice/Ticket/TicketUpdate/TicketID
```

## Endpoint

### `POST /api/v1/lhc2otobo/updatewithimage`

Requires `Authorization: Bearer <token>` header.

**Request body (Live Helper Chat webhook):**
```json
{
  "ticketnumber": "2025010112345678",
  "title": "Test ticket",
  "queue": "Support",
  "subject": "Re: Help needed",
  "additional_data": [
    { "key": "menu_principal", "identifier": "menu_principal", "value": "3" },
    { "key": "numero_medidor", "identifier": "numero_medidor", "value": "12345" },
    { "key": "numero_telefono", "identifier": "numero_telefono", "value": "555-1234" },
    { "key": "nombre_usuario", "identifier": "nombre_usuario", "value": "Juan Perez" },
    { "key": "descripcion_averia", "identifier": "descripcion_averia", "value": "Cable caido" },
    { "key": "averia_imagen_file", "identifier": "averia_imagen_file", "value": "1071_89d1d83fea0945cb3cc27c72849531b4" }
  ],
  "file": "iVBOR... (base64 raw — optional)"
}
```

**Behavior:**

1. The `Article.Body` is built from `additional_data` based on `menu_principal`:
   - If `menu_principal` = `3`: body contains Medidor, Telefono, Nombre, Descripcion
   - If `menu_principal` = `4`: body contains Suscriptor, Telefono, Nombre, Descripcion
2. `UserLogin` and `Password` are taken from `OTOBO_USER` / `OTOBO_PWD` env vars.
3. If `file` is present:
   - Detects image format from base64 magic bytes (PNG/JPEG/GIF/WEBP).
   - Reads filename from `averia_imagen_file` in `additional_data` and appends the extension.
   - Replaces `file` with an `Attachment` array in the payload sent to Otobo.
4. If `WEBHOOK_TESTER` is configured, a copy of the outgoing JSON is POSTed there in the background (fire-and-forget, does not affect the response).

**Response:** The Otobo API response is returned verbatim.

## Flow Diagram

```
LHC  ──POST──>  /api/v1/lhc2otobo/updatewithimage
                   │
                   ├── Build Article.Body from additional_data
                   │         (menu_principal = 3 or 4)
                   │
                   ├── Inject UserLogin/Password from env vars
                   │
                   ├── file present? ──Yes──>  Detect format
                   │                              │
                   │                         Read filename from
                   │                         averia_imagen_file
                   │                              │
                   │                         Build Attachment
                   │                              │
                   └──── No ──────────────────────┘
                                                    │
                                    ┌───────────────┘
                                    ▼
                         POST to Otobo API
                                    │
                         <── Otobo response ──┘
                                    │
                         WEBHOOK_TESTER? ──Yes──>  POST copy (fire-and-forget)
