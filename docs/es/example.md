# Módulo Example

Este módulo sirve como plantilla de referencia para crear nuevos módulos en la API Titos.

## Endpoints

Todos los endpoints están prefijados con `/api/v1/example` y requieren autenticación mediante el header `Authorization: Bearer <token>`.

### `GET /api/v1/example/items`

Devuelve una lista de todos los items.

**Respuesta `200`:** Arreglo de objetos `ItemResponse`.

### `POST /api/v1/example/items`

Crea un nuevo item.

**Cuerpo de la solicitud:**
```json
{
  "name": "Nombre del item",
  "description": "Descripción opcional",
  "value": 42.5
}
```

**Respuesta `201`:** El objeto `ItemResponse` creado.

### `GET /api/v1/example/items/{item_id}`

Obtiene un item por su UUID.

**Respuesta `200`:** Objeto `ItemResponse`.
**Respuesta `404`:** Item no encontrado.

### `PUT /api/v1/example/items/{item_id}`

Actualiza un item existente. Mismo cuerpo que POST.

**Respuesta `200`:** Objeto `ItemResponse` actualizado.
**Respuesta `404`:** Item no encontrado.

### `DELETE /api/v1/example/items/{item_id}`

Elimina un item por su UUID.

**Respuesta `204`:** Sin contenido (éxito).
**Respuesta `404`:** Item no encontrado.

## Ejecutar el servidor

```bash
uvicorn src.main:app --host 0.0.0.0 --port 5001 --reload
# o
python -m src.main
```

## Cómo crear un nuevo módulo

1. Copia la carpeta `src/modules/example/` a `src/modules/tu_modulo/`.
2. Renombra las clases y actualiza el prefijo del router.
3. Reemplaza la lógica del servicio en memoria con llamadas a APIs externas usando `HttpClient` de `src/shared/http_client.py`.
4. Registra el router en `src/main.py`.
5. Agrega tus tests en `tests/`.
6. Documenta tu módulo en `docs/en/` y `docs/es/`.
