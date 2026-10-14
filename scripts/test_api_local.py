#!/usr/bin/env python3
"""Prueba local de la lógica de la API sin requerir Docker."""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, "data")

ESTADOS = {"A": "ACTIVO", "I": "INACTIVO"}


def get_member(documento):
    empresas = {}
    with open(os.path.join(DATA_DIR, "EMPRESA.csv"), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            empresas[row["COD_EMP"].strip()] = row["NOM_EMP"].strip()

    with open(os.path.join(DATA_DIR, "AFI_MAE.csv"), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["NRO_DOC"].strip() == str(documento).strip():
                parts = [row["NOM1"].strip(), row["NOM2"].strip(), row["APE1"].strip(), row["APE2"].strip()]
                nombre = " ".join([p for p in parts if p]).strip()
                est_raw = row["EST_AFI"].strip()
                estado = ESTADOS.get(est_raw, est_raw)
                cod_emp = row["COD_EMP"].strip()
                nom_emp = empresas.get(cod_emp, "")
                return {"documento": row["NRO_DOC"].strip(), "nombre": nombre, "estado": estado, "empresa": nom_emp}

    return None


if __name__ == "__main__":
    doc = sys.argv[1] if len(sys.argv) > 1 else "1098765432"
    result = get_member(doc)
    if result is None:
        print(f"HTTP 404 Not Found")
        print(json.dumps({"error": "afiliado no encontrado"}, indent=2, ensure_ascii=False))
    else:
        print(f"HTTP 200 OK")
        print(json.dumps(result, indent=2, ensure_ascii=False))
