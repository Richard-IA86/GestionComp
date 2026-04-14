"""
src/reportes/generador.py
──────────────────────────
Genera los informes de dirección diarios a partir de los DataFrames
enriquecidos.  Produce archivos Excel con formato y, opcionalmente, PDF.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from loguru import logger

from config.settings import INFORMES_DIR, REPORTES_DIR


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _nombre_informe(prefijo: str, fecha: date, extension: str = "xlsx") -> Path:
    """Genera el nombre del archivo de salida con fecha."""
    nombre = f"{prefijo}_{fecha.strftime('%Y%m%d')}.{extension}"
    return INFORMES_DIR / nombre


# ─── Generadores por tipo de informe ─────────────────────────────────────────

def generar_informe_diario(
    datos: dict[str, pd.DataFrame],
    fecha: date | None = None,
) -> Path:
    """
    Genera el informe de dirección diario consolidado en un Excel con
    múltiples hojas, una por cada fuente de datos.

    Args:
        datos:  Dict con DataFrames enriquecidos (salida de enriquecer_datos()).
        fecha:  Fecha del informe (default: hoy).

    Returns:
        Ruta del archivo Excel generado.
    """
    if fecha is None:
        fecha = date.today()

    ruta_salida = _nombre_informe("Informe_Direccion", fecha)
    logger.info(f"Generando informe diario → {ruta_salida.name}")

    with pd.ExcelWriter(ruta_salida, engine="xlsxwriter") as writer:
        workbook = writer.book

        # ── Formatos ──────────────────────────────────────────────────────────
        fmt_titulo = workbook.add_format({
            "bold": True, "font_size": 14, "bg_color": "#1F3864",
            "font_color": "white", "align": "center", "valign": "vcenter",
        })
        fmt_header = workbook.add_format({
            "bold": True, "bg_color": "#2F5496", "font_color": "white",
            "border": 1, "align": "center",
        })
        fmt_moneda = workbook.add_format({"num_format": "#,##0.00", "border": 1})
        fmt_fecha  = workbook.add_format({"num_format": "dd/mm/yyyy", "border": 1})
        fmt_celda  = workbook.add_format({"border": 1})

        for hoja, df in datos.items():
            if df.empty:
                logger.warning(f"  Hoja '{hoja}' vacía — se omite")
                continue

            df.to_excel(writer, sheet_name=hoja[:31], index=False, startrow=2)
            ws = writer.sheets[hoja[:31]]

            # Título de la hoja
            ws.merge_range(0, 0, 1, len(df.columns) - 1,
                           f"{hoja.replace('_', ' ').title()} — {fecha.strftime('%d/%m/%Y')}",
                           fmt_titulo)

            # Ancho automático de columnas
            for i, col in enumerate(df.columns):
                ancho = max(len(str(col)), df[col].astype(str).str.len().max() or 10)
                ws.set_column(i, i, min(ancho + 2, 50))

            logger.debug(f"  Hoja '{hoja}' → {len(df)} filas")

    logger.success(f"Informe generado: {ruta_salida}")
    return ruta_salida


def generar_resumen_excel(
    datos: dict[str, pd.DataFrame],
    fecha: date | None = None,
) -> Path:
    """
    Genera un Excel de reporte intermedio (datos limpios, sin formato de
    informe) en output/reportes/ para uso interno / auditoría.
    """
    if fecha is None:
        fecha = date.today()

    nombre = f"Reporte_Procesado_{fecha.strftime('%Y%m%d')}.xlsx"
    ruta_salida = REPORTES_DIR / nombre
    logger.info(f"Generando reporte procesado → {nombre}")

    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        for hoja, df in datos.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=hoja[:31], index=False)

    logger.success(f"Reporte procesado guardado: {ruta_salida}")
    return ruta_salida
