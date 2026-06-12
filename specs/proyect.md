# API Multiproposito

## Descripcion tecnica

API Modular, cada entpoint representa una herramienta diferente. La finalidad es que funcione como Middleware API en diferentes softwares como: Live helper Chat, N8N, etc.

## Tecnologias a utilizar

1.  FastAPI
2.  Pyhton (venv)
3.  Sin API Gateway
4.  Sin Cola de Mensajes
5.  Sin capas separadas por modulo
6.  Estructura de carpetas por feature


## Reglas obligatorias

1.  Debe autenticar mediante API Token en el Header, usar variable de entorno AUTH_TOKEN.
2.  Debe de ser modular y poder reutilizar codigo.
3.  El codigo debe de estar correctamente comentado.
4.  Comenta cada ruta, metodo, clase, etc.
5.  Los nombres de las rutas deben estar en Ingles.
6.  Debe existir un directorio llamado docs donde se va almacenar toda la documentacion en Ingles y Espanol.
7. Se va a usar el puerto 5001 y se puede escuchar desde cualquier host.
8. Debe existir una variable de entorno: WEBHOOK_TESTER, si la variable contiene una url valida entonces cualquier modulo puede enviar datos de salida al Webhook tester para analizar los datos.