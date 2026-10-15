# Uso de inteligencia artificial

## Uso 1 — Antigravity Agentic AI (Gemini)
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Diagnosticar el fallo de inicio del contenedor cierre-worker y el error de conexión en la API.
- Prompt principal (resumido): "Diagnosticar por qué cierre-worker termina en Exited (1) y por qué cierre-api no conecta con la base de datos en docker-compose"
- Qué produjo: Identificó que WORKER_INTERVAL_SECONDS contenía '30s' causando ValueError al convertir con int(), y que DATABASE_HOST estaba configurado como cierre-database en vez del nombre del servicio en compose.
- Qué modificó o corrigió el equipo: El equipo corrigió WORKER_INTERVAL_SECONDS a 30 en las variables de entorno y ajustó el código del worker para limpiar cualquier sufijo no numérico adicional.

## Uso 2 — Antigravity Agentic AI (Gemini)
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Identificar la causa raíz del error HTTP 500 en el endpoint de consulta GET /afiliados/{documento}.
- Prompt principal (resumido): "Analizar la función find_member en services/api/app.py y por qué retorna error interno 500 para ciertos afiliados"
- Qué produjo: Explicó que la concatenación de nombres falla con TypeError cuando nom2 o ape2 son valores None provenientes de columnas nulas de PostgreSQL, además de fallar por usar JOIN en vez de LEFT JOIN con empresa.
- Qué modificó o corrigió el equipo: El equipo implementó un ensamblado seguro de los nombres descartando campos nulos y vacíos, aplicó LEFT JOIN con empresa y protegió la consulta con códigos de estado por defecto.

## Uso 3 — Antigravity Agentic AI (Gemini)
- Herramienta: Antigravity Agentic AI / Gemini
- Para qué se usó: Estructurar la lógica de conciliación, calidad de datos, normalización de fechas y cruce con Caja Oriente.
- Prompt principal (resumido): "Diseñar el script de cierre mensual para conciliar los afiliados activos, detectar excepciones y cuadrar con la hoja de control"
- Qué produjo: Proporcionó un esquema de procesamiento en Python y Bash para validar duplicados, códigos de estado, empresas faltantes, beneficiarios huérfanos, fechas corruptas y discrepancias de extracto externo.
- Qué modificó o corrigió el equipo: El equipo adaptó las reglas de negocio exactas de la hoja de control, eliminó la operación destructiva que borraba el archivo maestro original y aseguró la repetibilidad estricta del cierre.

## Uso 4 — ChatGPT (OpenAI)
- Herramienta: ChatGPT (GPT-4o) — OpenAI
- Para qué se usó: Diseñar la estructura inicial del modelo de datos y las migraciones SQL para las tablas de afiliados, beneficiarios y empresas.
- Prompt principal (resumido): "Genera las sentencias SQL para crear las tablas afiliados, beneficiarios y empresas siguiendo normalización 3FN, con sus restricciones de integridad referencial"
- Qué produjo: Entregó el DDL completo con claves primarias, foráneas, índices sobre documento y cod_empresa, y restricciones CHECK sobre campos de estado.
- Qué modificó o corrigió el equipo: El equipo adaptó los tipos de dato a los requerimientos exactos del enunciado (VARCHAR vs TEXT, NUMERIC vs DECIMAL), añadió las columnas de auditoría (created_at, updated_at) y ajustó los nombres de columna al glosario oficial del proyecto.

## Uso 5 — ChatGPT (OpenAI)
- Herramienta: ChatGPT (GPT-4o) — OpenAI
- Para qué se usó: Generar los datos de prueba (seed) para poblar la base de datos con afiliados, beneficiarios y registros de novedades representativos.
- Prompt principal (resumido): "Crea 20 registros de INSERT INTO para la tabla afiliados con casos borde: nom2 NULL, ape2 NULL, empresa NULL, fecha_ingreso inválida y estado diferente a A"
- Qué produjo: Generó un script SQL con casos representativos que cubrían valores nulos, fechas corruptas, duplicados y afiliados sin empresa asignada.
- Qué modificó o corrigió el equipo: El equipo revisó los documentos generados para garantizar que fueran cédulas colombianas válidas, ajustó los rangos de fecha a los exigidos por el reto y añadió registros adicionales para cubrir las reglas de negocio de Caja Oriente.

## Uso 6 — Claude (Anthropic)
- Herramienta: Claude (Anthropic)
- Para qué se usó: Revisar la seguridad y robustez del código de la API REST, detectar posibles inyecciones SQL y sugerir manejo de errores.
- Prompt principal (resumido): "Analiza el siguiente endpoint Flask en Python para detectar vulnerabilidades de inyección SQL, manejo inadecuado de excepciones y respuestas de error no estándar"
- Qué produjo: Detectó que la consulta usaba interpolación de cadenas en lugar de parámetros preparados, que la excepción genérica Exception enmascaraba errores de BD, y que los códigos HTTP de respuesta de error no seguían la especificación OpenAPI del reto.
- Qué modificó o corrigió el equipo: El equipo reemplazó la interpolación directa por parámetros posicionales de psycopg2, separó los bloques except por tipo de error (psycopg2.Error, ValueError, Exception) y alineó todos los códigos de respuesta con el contrato definido en el enunciado.
