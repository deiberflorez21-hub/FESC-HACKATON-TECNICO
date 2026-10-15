# Terminal Rescue — Equipo FESC Legacy

Documentación técnica y operativa de la solución implementada para el reto Terminal Rescue del Hackathon FESC Legacy Challenge 2026.

## Descripción

Terminal Rescue es una solución integral diseñada para el área de Operaciones y la división de Subsidios de la Caja de Compensación Familiar. Resuelve las fallas críticas en el proceso mensual de cierre de afiliados activos, automatizando la conciliación de datos, la depuración de inconsistencias, la integración con sistemas externos y la disponibilidad de una API de consulta de alto rendimiento, garantizando que los subsidios se otorguen con base en información precisa, verificable y trazable.

## Integrantes

- Deiber Adrian Florez Castillo (Ingeniería de Software - Nivel Técnico)
- Jose Yesid Gonzalez Ortiz (Ingeniería de Software - Nivel Técnico)

## Requisitos

Para desplegar y ejecutar esta solución se requiere contar con:
- Docker Engine versión 24.0 o superior
- Docker Compose v2.20 o superior
- Git para control de versiones
- Sistema operativo Linux, macOS o Windows (con WSL2 / Git Bash)
- Python 3.8 o superior y utilidades estándar de terminal (`bash`, `curl`, `grep`, `awk`, `sed`, `sort`, `uniq`, `wc`, `find`, `chmod`, `psql`)

## Instalación y ejecución

Para desplegar y levantar el entorno completo desde una copia limpia del repositorio, ejecute en orden los comandos docker compose con el subcomando up y luego ./run.sh:

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
./run.sh
```

El comando docker compose up -d inicia los servicios y ./run.sh ejecuta el proceso de cierre mensual en la terminal.

## Configuración

Las variables de entorno se definen en el archivo `.env` tomando como base `.env.example`. A continuación se detalla cada variable:

| Variable | Descripción | Valor de ejemplo |
|---|---|---|
| `POSTGRES_DB` | Nombre de la base de datos principal de PostgreSQL para el cierre | `cierre` |
| `POSTGRES_USER` | Usuario administrador de la base de datos PostgreSQL | `cierre` |
| `POSTGRES_PASSWORD` | Contraseña asignada al usuario de la base de datos PostgreSQL | `cierre2026` |
| `DATABASE_HOST` | Host de red o nombre de servicio para conectar a la base (apunta al servicio compose) | `cierre-db` |
| `DATABASE_PORT` | Puerto TCP de escucha de la base de datos PostgreSQL | `5432` |
| `DATABASE_NAME` | Nombre de la base de datos a la que conectan API y Worker | `cierre` |
| `DATABASE_USER` | Usuario utilizado por API y Worker para autenticarse en la base | `cierre` |
| `DATABASE_PASSWORD` | Contraseña utilizada por API y Worker para autenticarse en la base | `cierre2026` |
| `API_PORT` | Puerto expuesto en el host para atender solicitudes HTTP de la API | `8081` |
| `WORKER_INTERVAL_SECONDS` | Intervalo en segundos entre cada conciliación periódica ejecutada por el worker | `30` |

## Arquitectura

La arquitectura del sistema está compuesta por tres servicios desacoplados definidos en `docker-compose.yml` que interactúan de manera coordinada dentro de una red aislada de Docker:

1. `cierre-db`: Contenedor basado en PostgreSQL 16 Alpine encargado del almacenamiento relacional persistente del maestro de afiliados, empresas, beneficiarios e historial de aportes, inicializado automáticamente mediante scripts SQL.
2. `cierre-api`: Microservicio REST implementado en Python que expone endpoints de consulta rápida de afiliados para Subsidios, conectándose directamente a la base de datos con políticas de tolerancia a fallos.
3. `cierre-worker`: Proceso en segundo plano en Python que realiza auditorías y conciliaciones periódicas de conteo de afiliados contra la base de datos de forma recurrente y sin bloquear el procesamiento.

Adicionalmente, el proceso batch de cierre corre orquestado por scripts Bash y Python que procesan los insumos de datos y extraen métricas analíticas.

## Uso

### Consulta a la API

Para consultar el estado de un afiliado mediante la API REST, realice una petición HTTP GET a la ruta `/afiliados/{documento}`:

```bash
curl -s http://localhost:8081/afiliados/1043217865
```

Ejemplo de respuesta exitosa (HTTP 200):
```json
{
  "documento": "1043217865",
  "nombre": "DEIBER ADRIAN FLOREZ CASTILLO",
  "estado": "ACTIVO",
  "empresa": "CAJA DE COMPENSACION FESC"
}
```

Si el documento no existe en el sistema, la API retornará HTTP 404:
```bash
curl -s -i http://localhost:8081/afiliados/9999999999
```

### Proceso de cierre batch

Al ejecutar `./run.sh`, se generan cuatro archivos en el directorio `output/`:

1. `output/afiliados_activos.csv`: Contiene el maestro consolidado de afiliados activos con empresa vigente (`documento,nombre,estado,cod_empresa,empresa,beneficiarios,ultimo_aporte`).
2. `output/excepciones.csv`: Detalla los registros que presentaron inconsistencias (`documento,tipo,detalle`) clasificadas en `DUPLICADO`, `SIN_EMPRESA`, `BENEFICIARIO_HUERFANO`, `CODIGO_INVALIDO`, `FECHA_INVALIDA` y `CRUCE_NO_COINCIDE`.
3. `output/totales.txt`: Resumen cuantitativo del cierre en formato clave=valor (`total_afiliados`, `activos`, `inactivos`, `excepciones`).
4. `output/top_error.txt`: Diagnóstico de los logs que identifica el código de error más frecuente (`codigo_error=CIE-4012`) y su cantidad de ocurrencias (`ocurrencias=1424`).

## Pruebas

Para comprobar que todos los componentes y verificaciones funcionan correctamente, ejecute los comandos del validador oficial:

```bash
./validator check --quick
./validator entregables
```

El validador comprueba que la API responda adecuadamente, que los servicios se mantengan estables y que las salidas de la carpeta output cumplan con la totalidad de los criterios exigidos.

## Documentación

Consulte los demás documentos de soporte técnico y trazabilidad en el repositorio:
- [incident-report.md](file:///c:/Users/deibe/Desktop/fesc-tecnico/incident-report.md): Informe detallado de los diez incidentes diagnosticados y reparados con comandos y soluciones.
- [evidence/](file:///c:/Users/deibe/Desktop/fesc-tecnico/evidence): Carpeta con las capturas de terminal que respaldan cada incidente resuelto.
- [AI_USAGE.md](file:///c:/Users/deibe/Desktop/fesc-tecnico/AI_USAGE.md): Declaración transparente sobre el uso de herramientas de inteligencia artificial durante el desarrollo.

## Qué resolvimos

El equipo resolvió diez incidentes críticos: se reparó la configuración del servicio `cierre-worker` eliminando valores no numéricos; se corrigió la resolución de nombres DNS para que `cierre-api` conecte a la base `cierre-db`; se refactorizó la consulta de la API para soportar nombres con valores nulos sin generar errores 500; se automatizó el procesamiento del script de cierre con rutas relativas e idempotencia absoluta; se normalizaron fechas inconsistentes; se cuadraron los totales con la hoja de control oficial; y se reportaron todas las excepciones de calidad de datos y cruces externos de forma transparente.

## Limitaciones y pendientes

Actualmente el sistema procesa los archivos batch de forma síncrona en memoria, por lo que para volúmenes superiores a decenas de millones de registros se recomendaría migrar el procesamiento hacia streaming con chunks o Apache Spark.
