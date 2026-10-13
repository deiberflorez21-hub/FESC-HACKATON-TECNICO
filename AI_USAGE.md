# Uso de inteligencia artificial

## Uso 1
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Diagnosticar el fallo de inicio del contenedor cierre-worker y el error de conexión en la API.
- Prompt principal (resumido): "Diagnosticar por qué cierre-worker termina en Exited (1) y por qué cierre-api no conecta con la base de datos en docker-compose"
- Qué produjo: Identificó que WORKER_INTERVAL_SECONDS contenía '30s' causando ValueError al convertir con int(), y que DATABASE_HOST estaba configurado como cierre-database en vez del nombre del servicio en compose.
- Qué modificó o corrigió el equipo: El equipo corrigió WORKER_INTERVAL_SECONDS a 30 en las variables de entorno y ajustó el código del worker para limpiar cualquier sufijo no numérico adicional.

## Uso 2
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Identificar la causa raíz del error HTTP 500 en el endpoint de consulta GET /afiliados/{documento}.
- Prompt principal (resumido): "Analizar la función find_member en services/api/app.py y por qué retorna error interno 500 para ciertos afiliados"
- Qué produjo: Explicó que la concatenación de nombres falla con TypeError cuando nom2 o ape2 son valores None provenientes de columnas nulas de PostgreSQL, además de fallar por usar JOIN en vez de LEFT JOIN con empresa.
- Qué modificó o corrigió el equipo: El equipo implementó un ensamblado seguro de los nombres descartando campos nulos y vacíos, aplicó LEFT JOIN con empresa y protegió la consulta con códigos de estado por defecto.

## Uso 3
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Estructurar la lógica de conciliación, calidad de datos, normalización de fechas y cruce con Caja Oriente.
- Prompt principal (resumido): "Diseñar el script de cierre mensual para conciliar los afiliados activos, detectar excepciones y cuadrar con la hoja de control"
- Qué produjo: Proporcionó un esquema de procesamiento en Python y Bash para validar duplicados, códigos de estado, empresas faltantes, beneficiarios huérfanos, fechas corruptas y discrepancias de extracto externo.
- Qué modificó o corrigió el equipo: El equipo adaptó las reglas de negocio exactas de la hoja de control, eliminó la operación destructiva que borraba el archivo maestro original y aseguró la repetibilidad estricta del cierre.
