#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Cierre mensual de afiliados activos.
# Ejecuta la conciliación de afiliados, cálculo de activos, excepciones,
# hoja de control y reporte de errores de logs.
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p output

# Determinar comando de Python
PYTHON_CMD="python3"
if command -v python3 >/dev/null 2>&1 && python3 -c "import sys" >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1 && python -c "import sys" >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v py >/dev/null 2>&1 && py -c "import sys" >/dev/null 2>&1; then
    PYTHON_CMD="py"
elif [ -f "/c/Users/deibe/AppData/Local/Programs/Python/Python314/python.exe" ]; then
    PYTHON_CMD="/c/Users/deibe/AppData/Local/Programs/Python/Python314/python.exe"
fi

echo ">> Ejecutando proceso de cierre de afiliados..."
"$PYTHON_CMD" scripts/procesar_cierre.py

# Extracción de error más frecuente utilizando herramientas de terminal
if compgen -G "logs/*.log" > /dev/null; then
    grep -hoE 'CIE-[0-9]{4}' logs/*.log 2>/dev/null | sort | uniq -c | sort -nr | head -n 1 | awk '{print "codigo_error=" $2 "\nocurrencias=" $1}' > output/top_error.txt
fi

echo ">> Cierre completado con éxito."
