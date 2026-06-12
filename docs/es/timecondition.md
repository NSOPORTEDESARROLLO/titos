# Módulo Time Condition

Verifica si la hora actual del servidor (en una zona horaria dada) está dentro de los rangos de tiempo configurados.

## Endpoint

### `POST /api/v1/timecondition`

Requiere header `Authorization: Bearer <token>`.

**Cuerpo de la solicitud:**
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

**Respuesta `200`:**
```json
{
  "status": "on",
  "online": "true",
  "msg": "Time: 10:30 is in the ranges"
}
```

**Respuesta `400`:** Zona horaria inválida o rango mal formado.

## Comportamiento

- La semana inicia el lunes (día 0).
- Los rangos se comparan con strings en formato `HH:MM`.
- Múltiples rangos son soportados; si alguno coincide, el resultado es `online: true`.
- Si `WEBHOOK_TESTER` está configurado, se envía una copia de la respuesta en segundo plano.
