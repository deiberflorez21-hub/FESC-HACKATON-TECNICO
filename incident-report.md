# Informe de incidentes — Terminal Rescue

## Incidente 1
- **Síntoma:** `docker compose ps` muestra `cierre-worker  Exited (1)`.
- **Diagnóstico:** el log del worker indica `codigo=CIE-1107 WORKER_INTERVAL_SECONDS debe ser un entero de segundos` debido a que la variable contenía el valor `30s` en lugar de un entero numérico.
- **Comandos:** `docker compose ps`, `docker compose logs cierre-worker | tail -n 10`
- **Solución:** se corrigió `WORKER_INTERVAL_SECONDS=30` en `.env.example` y en `.env`, y se reforzó la función `load_interval()` en `worker.py` para ignorar sufijos no numéricos.
- **Evidencia:** evidence/01-worker.txt

## Incidente 2
- **Síntoma:** la API de consulta `cierre-api` responde con error HTTP 503 indicando que la base de datos no está disponible.
- **Diagnóstico:** en la configuración de entorno la variable `DATABASE_HOST` apuntaba al nombre erróneo `cierre-database`, mientras que en `docker-compose.yml` el servicio de base de datos se llama `cierre-db`.
- **Comandos:** `docker compose logs cierre-api`, `docker compose exec cierre-db psql -U cierre -d cierre -c "SELECT count(*) FROM afi_mae;"`
- **Solución:** se corrigió la variable de entorno a `DATABASE_HOST=cierre-db` en `.env.example` y `.env` para restablecer la conectividad entre contenedores.
- **Evidencia:** evidence/02-api-db.txt

## Incidente 3
- **Síntoma:** la ejecución del script `scripts/cierre.sh` falla con error al no encontrar el archivo de entrada maestro.
- **Diagnóstico:** el script heredado utilizaba una ruta absoluta inexistente `ENTRADA=/opt/cierre/entrada`, cuando los archivos reales residen en el directorio relativo `data/` del repositorio.
- **Comandos:** `find . -name "AFI_MAE.csv"`, `chmod +x scripts/cierre.sh run.sh`
- **Solución:** se ajustaron las rutas de entrada y salida relativas a la raíz del proyecto y se aseguraron los permisos de ejecución adecuados en los scripts.
- **Evidencia:** evidence/03-script-entrada.txt

## Incidente 4
- **Síntoma:** los registros del sistema acumulan miles de líneas de eventos y errores en `logs/api.log`, `logs/worker.log` y `logs/database.log`.
- **Diagnóstico:** mediante análisis con herramientas de terminal se identificó que el código de error `CIE-4012` es el más frecuente en todos los registros.
- **Comandos:** `grep -hoE 'CIE-[0-9]{4}' logs/*.log | sort | uniq -c | sort -nr | head -n 5`
- **Solución:** se determinó que `CIE-4012` acumuló 1424 ocurrencias y se automatizó su conteo para generar `output/top_error.txt` con los valores `codigo_error=CIE-4012` y `ocurrencias=1424`.
- **Evidencia:** evidence/04-top-error.txt

## Incidente 5
- **Síntoma:** el maestro de afiliados presenta inconsistencias de datos que impiden un cierre limpio y confiable.
- **Diagnóstico:** se detectaron 20 documentos duplicados, 14 con códigos de estado no válidos, 18 afiliados activos sin empresa asociada en `EMPRESA.csv` y 15 beneficiarios huérfanos sin titular en `AFI_MAE.csv`.
- **Comandos:** `awk -F',' 'NR>1 {print $1}' data/AFI_MAE.csv | sort | uniq -d | wc -l`, `sed -n '1,10p' data/AFI_MAE.csv`
- **Solución:** se conservó la primera aparición de duplicados y se clasificaron todas las anomalías en `output/excepciones.csv` bajo los tipos `DUPLICADO`, `CODIGO_INVALIDO`, `SIN_EMPRESA` y `BENEFICIARIO_HUERFANO`.
- **Evidencia:** evidence/05-calidad-datos.txt

## Incidente 6
- **Síntoma:** la consulta `GET /afiliados/{documento}` responde con error HTTP 500 en afiliados con nombres incompletos.
- **Diagnóstico:** en `services/api/app.py` la concatenación directa de cadenas fallaba con `TypeError` cuando `nom2` o `ape2` eran nulos en PostgreSQL, además de fallar ante empresas inexistentes por usar `JOIN` estricto.
- **Comandos:** `docker compose logs cierre-api | grep CIE-5003`, `curl -s http://localhost:8081/afiliados/88121168`
- **Solución:** se implementó `LEFT JOIN empresa`, ensamblado seguro de nombres con filtrado de nulos y obtención protegida de estados, devolviendo HTTP 200 con datos válidos o 404 para inexistentes.
- **Evidencia:** evidence/06-api-afiliados.txt

## Incidente 7
- **Síntoma:** múltiples registros en `AFI_MAE.csv` contienen fechas en formatos no estándar o con valores corruptos.
- **Diagnóstico:** la regla de negocio exige normalizar `DD/MM/YYYY` y `YYYYMMDD` a `YYYY-MM-DD`, detectándose además 12 registros cuyas fechas representan valores imposibles o no interpretables.
- **Comandos:** `grep -vE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' data/AFI_MAE.csv | wc -l`, `awk -F',' 'NR>1 {print $1, $9}' data/AFI_MAE.csv`
- **Solución:** las fechas válidas en formatos alternativos fueron normalizadas al formato oficial y las 12 fechas inválidas se reportaron como `FECHA_INVALIDA` en `output/excepciones.csv` sin descartar al afiliado.
- **Evidencia:** evidence/07-fechas.txt

## Incidente 8
- **Síntoma:** el archivo `data/extracto_caja_oriente.csv` presenta una estructura divergente con separador punto y coma, identificadores rellenados con ceros y estados propios.
- **Diagnóstico:** al comparar el extracto externo contra la base local se hallaron 25 discrepancias donde el documento no existía o la situación (`VIGENTE`/`RETIRADO`) no concordaba con el estado local (`A`/`I`).
- **Comandos:** `awk -F';' '{print $1, $3}' data/extracto_caja_oriente.csv | wc -l`, `grep -c '^' data/extracto_caja_oriente.csv`
- **Solución:** se removió el relleno de ceros de los identificadores, se homologaron los estados y las 25 diferencias se reportaron como `CRUCE_NO_COINCIDE` en `output/excepciones.csv`, preservando las columnas de activos.
- **Evidencia:** evidence/08-caja-oriente.txt

## Incidente 9
- **Síntoma:** los totales numéricos calculados por el proceso de cierre no coincidían con la hoja de control de Operaciones.
- **Diagnóstico:** el script anterior calculaba totales contando líneas sin depurar duplicados ni segregar afiliados inactivos, con estado erróneo o sin empresa.
- **Comandos:** `wc -l output/afiliados_activos.csv`, `wc -l output/excepciones.csv`
- **Solución:** se implementó el cálculo formal generando `output/totales.txt` con `total_afiliados=1500`, `activos=1194`, `inactivos=274` y `excepciones=104`, cuadrando con `control/hoja_control.csv`.
- **Evidencia:** evidence/09-totales.txt

## Incidente 10
- **Síntoma:** el script de cierre no era repetible y fallaba en ejecuciones sucesivas.
- **Diagnóstico:** al finalizar la ejecución, el script ejecutaba `mv $ENTRADA/AFI_MAE.csv $ENTRADA/procesados/`, retirando el archivo original de entrada e impidiendo corridas posteriores.
- **Comandos:** `find data/ -type f`, `chmod +x run.sh`
- **Solución:** se eliminó la instrucción de traslado destructivo y se aseguró la idempotencia completa de `./run.sh`, permitiendo ejecuciones continuas y tras restauraciones con `./reset.sh`.
- **Evidencia:** evidence/10-repetibilidad.txt
