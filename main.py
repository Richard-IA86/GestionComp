"""
main.py
────────
Punto de entrada principal del proyecto Compensaciones.

Flujo:
  0. Verificar VPN activa (WireGuard)
  1. Descargar reportes desde el sistema web (requiere VPN activa)
  2. Enriquecer / procesar los datos descargados
  3. Generar informe de dirección diario
  4. Ejecutar pipeline ETL sobre los archivos descargados

Uso:
    python main.py                        # ejecuta el flujo completo
    python main.py --solo-procesar  # omite la descarga
    python main.py --fecha 2026-04-09     # fecha específica para los filtros
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from src.utils.logger import configurar_logger
from loguru import logger


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compensaciones — Automatización de reportes diarios"
    )
    parser.add_argument(
        "--solo-procesar",
        action="store_true",
        help="Salta la descarga; usa los archivos existentes en input_raw/",
    )
    parser.add_argument(
        "--fecha",
        type=str,
        default=None,
        help="Fecha de referencia en formato YYYY-MM-DD (default: hoy)",
    )
    return parser.parse_args()


def main() -> int:
    configurar_logger()
    args = parsear_argumentos()

    # ── Fecha de referencia ──────────────────────────────────────────────────
    if args.fecha:
        try:
            fecha = datetime.strptime(args.fecha, "%Y-%m-%d").date()
        except ValueError:
            logger.error(
                f"Formato de fecha inválido: '{args.fecha}'. Use YYYY-MM-DD."
            )
            return 1
    else:
        fecha = date.today()

    logger.info(
        f"═══ Compensaciones — Informe {fecha.strftime('%d/%m/%Y')} ═══"
    )
    # ── 0. VPN ──────────────────────────────────────────────────────────────
    if not args.solo_procesar:
        logger.info("Paso 0/4 — Verificando conectividad VPN")
        from src.utils.vpn_check import asegurar_vpn

        if not asegurar_vpn():
            logger.error("Abortando: VPN no disponible.")
            return 1
    # ── 1. Descarga ──────────────────────────────────────────────────────────
    if not args.solo_procesar:
        logger.info("Paso 1/4 — Descarga de reportes")
        try:
            from src.descarga.scraper import descargar_todos_los_reportes

            descargar_todos_los_reportes(fecha_hasta=fecha)
        except Exception as exc:
            logger.error(f"Fallo en la descarga: {exc}")
            logger.warning(
                "Continuando con archivos existentes en input_raw/..."
            )
    else:
        logger.info("Paso 1/4 — Descarga omitida (--solo-procesar)")

    # ── 2. Procesamiento ─────────────────────────────────────────────────────
    logger.info("Paso 2/4 — Enriquecimiento de datos")
    from src.procesamiento.enriquecimiento import enriquecer_datos

    datos = enriquecer_datos()

    if not datos:
        logger.error(
            "No hay datos para procesar."
            " Verificá que input_raw/ tenga archivos."
        )
        return 1

    # ── 3. Generación de informes ────────────────────────────────────────────
    logger.info("Paso 3/4 — Generación de informes")
    from src.reportes.generador import (
        generar_informe_diario,
        generar_resumen_excel,
    )

    informe = generar_informe_diario(datos, fecha=fecha)
    reporte = generar_resumen_excel(datos, fecha=fecha)

    # ── 4. ETL Pipeline ──────────────────────────────────────────────────────
    logger.info("Paso 4/4 — ETL: transformación y carga de variables")
    from config.settings import ARCHIVOS_ESPERADOS, INPUT_RAW_DIR
    from src.etl.pipeline import Pipeline as ETLPipeline

    etl = ETLPipeline()
    fecha_str = fecha.strftime("%Y%m%d")
    for nombre in ARCHIVOS_ESPERADOS:
        ruta_archivo = INPUT_RAW_DIR / nombre
        if not ruta_archivo.exists():
            logger.debug(f"ETL: archivo no encontrado, omitido: {nombre}")
            continue
        logger.info(f"ETL procesando: {nombre}")
        try:
            stats = etl.ejecutar(
                fuente="excel",
                archivo=str(ruta_archivo),
                fecha=fecha_str,
            )
            logger.info(
                f"  válidos={stats['registros_validos']}"
                f" rechazados={stats['registros_rechazados']}"
                f" → {stats['ruta_salida']}"
            )
        except Exception as exc:
            logger.warning(f"ETL falló para '{nombre}': {exc}")

    logger.success("═══ Proceso completado exitosamente ═══")
    logger.info(f"  Informe de dirección : {informe}")
    logger.info(f"  Reporte procesado    : {reporte}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
