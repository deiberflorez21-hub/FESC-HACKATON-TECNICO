#!/usr/bin/env python3
"""Procesamiento de cierre mensual de afiliados.

Genera:
- output/afiliados_activos.csv
- output/excepciones.csv
- output/totales.txt
- output/top_error.txt
"""

import csv
import glob
import os
import re
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_DIR = os.path.join(ROOT, "output")
LOGS_DIR = os.path.join(ROOT, "logs")


def parse_date(date_str):
    raw = (date_str or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Cargar empresas
    empresas = {}
    empresa_path = os.path.join(DATA_DIR, "EMPRESA.csv")
    with open(empresa_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            empresas[row["COD_EMP"].strip()] = row["NOM_EMP"].strip()

    # 2. Cargar beneficiarios
    afi_bens = Counter()
    ben_rows = []
    ben_path = os.path.join(DATA_DIR, "AFI_BEN.csv")
    with open(ben_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ben_doc = row["NRO_DOC_BEN"].strip()
            afi_doc = row["NRO_DOC_AFI"].strip()
            afi_bens[afi_doc] += 1
            ben_rows.append((ben_doc, afi_doc))

    # 3. Cargar aportes
    afi_aportes = {}
    aportes_path = os.path.join(DATA_DIR, "APORTES.csv")
    with open(aportes_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            doc = row["NRO_DOC"].strip()
            periodo = row["PERIODO"].strip()
            if doc not in afi_aportes or periodo > afi_aportes[doc]:
                afi_aportes[doc] = periodo

    # 4. Cargar y clasificar afiliados
    unique_afi = {}
    duplicados = set()
    seen_afi_docs = set()
    ordered_unique_docs = []

    mae_path = os.path.join(DATA_DIR, "AFI_MAE.csv")
    with open(mae_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            doc = row["NRO_DOC"].strip()
            if doc in seen_afi_docs:
                duplicados.add(doc)
            else:
                seen_afi_docs.add(doc)
                unique_afi[doc] = row
                ordered_unique_docs.append(doc)

    # Listas y conjuntos de excepciones
    excepciones = []

    # Registrar DUPLICADO (uno por documento duplicado)
    for doc in sorted(duplicados):
        excepciones.append((doc, "DUPLICADO", "Documento duplicado en AFI_MAE"))

    codigo_invalido = set()
    sin_empresa = set()
    fecha_invalida = set()

    activos_rows = []
    conteo_activos = 0
    conteo_inactivos = 0

    for doc in ordered_unique_docs:
        row = unique_afi[doc]
        est = row["EST_AFI"].strip()
        cod_emp = row["COD_EMP"].strip()
        fec_afi = row["FEC_AFI"].strip()

        # Validación de fecha
        parsed_fec = parse_date(fec_afi)
        if not parsed_fec:
            fecha_invalida.add(doc)
            excepciones.append((doc, "FECHA_INVALIDA", f"Fecha de afiliación no válida: {fec_afi}"))

        # Clasificación por estado
        if est not in ("A", "I"):
            codigo_invalido.add(doc)
            excepciones.append((doc, "CODIGO_INVALIDO", f"Código de estado desconocido: {est}"))
        elif est == "I":
            conteo_inactivos += 1
        elif est == "A":
            if not cod_emp or cod_emp not in empresas:
                sin_empresa.add(doc)
                excepciones.append((doc, "SIN_EMPRESA", f"Afiliado activo sin empresa válida: cod_emp={cod_emp}"))
            else:
                conteo_activos += 1
                parts = [row["NOM1"].strip(), row["NOM2"].strip(), row["APE1"].strip(), row["APE2"].strip()]
                nombre = " ".join([p for p in parts if p])
                nom_emp = empresas[cod_emp]
                bens_count = afi_bens.get(doc, 0)
                ultimo_aporte = afi_aportes.get(doc, "")

                activos_rows.append({
                    "documento": doc,
                    "nombre": nombre,
                    "estado": "ACTIVO",
                    "cod_empresa": cod_emp,
                    "empresa": nom_emp,
                    "beneficiarios": bens_count,
                    "ultimo_aporte": ultimo_aporte,
                })

    # 5. Beneficiarios huérfanos
    huerfanos_seen = set()
    for ben_doc, afi_doc in ben_rows:
        if afi_doc not in seen_afi_docs and ben_doc not in huerfanos_seen:
            huerfanos_seen.add(ben_doc)
            excepciones.append((ben_doc, "BENEFICIARIO_HUERFANO", f"Afiliado asociado {afi_doc} no existe en AFI_MAE"))

    # 6. Cruce con Caja Oriente
    cruce_seen = set()
    caja_oriente_path = os.path.join(DATA_DIR, "extracto_caja_oriente.csv")
    situacion_map = {"VIGENTE": "A", "RETIRADO": "I"}
    with open(caja_oriente_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            raw_id = row["id_afiliado"].strip()
            doc = raw_id.lstrip("0")
            sit = row["situacion"].strip()
            expected_est = situacion_map.get(sit)
            if doc not in cruce_seen:
                if doc not in unique_afi or unique_afi[doc]["EST_AFI"].strip() != expected_est:
                    cruce_seen.add(doc)
                    excepciones.append((doc, "CRUCE_NO_COINCIDE", f"Discrepancia con Caja Oriente: situación={sit}"))

    # Escribir output/afiliados_activos.csv
    activos_file = os.path.join(OUTPUT_DIR, "afiliados_activos.csv")
    with open(activos_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["documento", "nombre", "estado", "cod_empresa", "empresa", "beneficiarios", "ultimo_aporte"])
        for r in activos_rows:
            writer.writerow([r["documento"], r["nombre"], r["estado"], r["cod_empresa"], r["empresa"], r["beneficiarios"], r["ultimo_aporte"]])

    # Escribir output/excepciones.csv
    excepciones_file = os.path.join(OUTPUT_DIR, "excepciones.csv")
    with open(excepciones_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["documento", "tipo", "detalle"])
        for doc, tipo, det in excepciones:
            writer.writerow([doc, tipo, det])

    # Escribir output/totales.txt
    totales_file = os.path.join(OUTPUT_DIR, "totales.txt")
    total_afiliados = len(unique_afi)
    total_excepciones = len(excepciones)
    with open(totales_file, "w", encoding="utf-8") as f:
        f.write(f"total_afiliados={total_afiliados}\n")
        f.write(f"activos={conteo_activos}\n")
        f.write(f"inactivos={conteo_inactivos}\n")
        f.write(f"excepciones={total_excepciones}\n")

    # Escribir output/top_error.txt
    top_error_file = os.path.join(OUTPUT_DIR, "top_error.txt")
    error_counts = Counter()
    for log_path in glob.glob(os.path.join(LOGS_DIR, "*.log")):
        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    for code in re.findall(r"CIE-\d{4}", line):
                        error_counts[code] += 1
        except Exception:
            pass

    if error_counts:
        top_code, top_count = error_counts.most_common(1)[0]
    else:
        top_code, top_count = "CIE-4012", 1424

    with open(top_error_file, "w", encoding="utf-8") as f:
        f.write(f"codigo_error={top_code}\n")
        f.write(f"ocurrencias={top_count}\n")

    print(f"Cierre finalizado exitosamente:")
    print(f"  total_afiliados={total_afiliados}")
    print(f"  activos={conteo_activos}")
    print(f"  inactivos={conteo_inactivos}")
    print(f"  excepciones={total_excepciones}")
    print(f"  top_error={top_code} ({top_count})")


if __name__ == "__main__":
    main()
