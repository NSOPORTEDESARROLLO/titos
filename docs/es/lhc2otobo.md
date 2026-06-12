# Módulo lhc2otobo

Recibe webhooks de Live Helper Chat, los transforma al formato de actualización de tickets de Otobo y los reenvía. Soporta adjuntos de imagen opcionales.

## Variables de Entorno

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `OTOBO_IP` | Hostname o IP del servidor Otobo | Sí |
| `OTOBO_USER` | Usuario de Otobo | Sí |
| `OTOBO_PWD` | Contraseña de Otobo | Sí |
| `WEBHOOK_TESTER` | URL para copia fire-and-forget del payload saliente (opcional) | No |

La URL de Otobo se construye automáticamente como:
```
https://{OTOBO_IP}/otobo/nph-genericinterface.pl/Webservice/Ticket/TicketUpdate/TicketID
```

## Endpoint

### `POST /api/v1/lhc2otobo/updatewithimage`

Requiere header `Authorization: Bearer <token>`.

**Cuerpo de la solicitud (webhook de Live Helper Chat):**
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
  "file": "iVBOR... (base64 raw — opcional)"
}
```

**Comportamiento:**

1. El `Article.Body` se construye desde `additional_data` según `menu_principal`:
   - Si `menu_principal` = `3`: el body contiene Medidor, Telefono, Nombre, Descripcion
   - Si `menu_principal` = `4`: el body contiene Suscriptor, Telefono, Nombre, Descripcion
2. `UserLogin` y `Password` se toman de las variables de entorno `OTOBO_USER` / `OTOBO_PWD`.
3. Si `file` está presente:
   - Detecta el formato de imagen desde los magic bytes del base64 (PNG/JPEG/GIF/WEBP).
   - Obtiene el nombre de archivo del campo `averia_imagen_file` en `additional_data` y le agrega la extensión.
   - Reemplaza `file` con un arreglo `Attachment` en el payload enviado a Otobo.
4. Si `WEBHOOK_TESTER` está configurado, se envía una copia del JSON saliente a esa URL en segundo plano (fire-and-forget, sin afectar la respuesta).

**Respuesta:** La respuesta de la API de Otobo se devuelve sin modificar.

## Diagrama de Flujo

```
LHC  ──POST──>  /api/v1/lhc2otobo/updatewithimage
                   │
                   ├── Construir Article.Body desde additional_data
                   │         (menu_principal = 3 o 4)
                   │
                   ├── Inyectar UserLogin/Password desde env vars
                   │
                   ├── ¿file presente? ──Sí──>  Detectar formato
                   │                              │
                   │                         Leer nombre archivo
                   │                         desde averia_imagen_file
                   │                              │
                   │                         Construir Attachment
                   │                              │
                   └──── No ──────────────────────┘
                                                    │
                                    ┌───────────────┘
                                    ▼
                         POST a API Otobo
                                    │
                         <── Respuesta Otobo ──┘
                                    │
                         ¿WEBHOOK_TESTER? ──Sí──>  POST copia (fire-and-forget)
