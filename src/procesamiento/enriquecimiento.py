"""
src/procesamiento/enriquecimiento.py
─────────────────────────────────────
Lee los archivos Excel de input_raw/, aplica transformaciones y cruces
de datos, y genera DataFrames enriquecidos listos para informes.
"""

from __future__ import annotations

import pandas as pd
from loguru import logger

from config.settings import INPUT_RAW_DIR

# ─── Carga de archivos raw ───────────────────────────────────────────────────


def cargar_archivos() -> dict[str, pd.DataFrame]:
    """
    Lee todos los Excel de input_raw/ y devuelve un dict:
        { "nombre_sin_extension": DataFrame }

    Los archivos exportados por ProntoNet tienen una fila de título en la
    fila 1 y los encabezados reales en la fila 2 → header=1.
    Las columnas 100 % vacías (artefactos de exportación) se descartan.
    """
    dfs: dict[str, pd.DataFrame] = {}
    archivos = list(INPUT_RAW_DIR.glob("*.xlsx")) + list(
        INPUT_RAW_DIR.glob("*.xls")
    )

    if not archivos:
        logger.warning(f"No se encontraron archivos en {INPUT_RAW_DIR}")
        return dfs

    for archivo in archivos:
        try:
            df = pd.read_excel(archivo, engine="openpyxl", header=1)
            # Eliminar columnas completamente vacías (artefactos)
            df = df.dropna(axis=1, how="all")
            # Eliminar filas completamente vacías
            df = df.dropna(axis=0, how="all")
            clave = archivo.stem
            dfs[clave] = df
            logger.info(
                f"  Cargado: {archivo.name}"
                f" → {len(df)} filas, {len(df.columns)} columnas"
            )
        except Exception as exc:
            logger.error(f"  Error al leer {archivo.name}: {exc}")

    return dfs


# ─── Transformaciones por reporte ────────────────────────────────────────────


def procesar_cuenta_corriente(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece el reporte de Cuenta Corriente.

    Columnas reales (ProntoNet): Comp., Numero, Ref., Fecha, Fecha vto.,
    Imp.orig., Saldo Comp., SaldoTrs, Fecha cmp., Mon.origen, Observaciones
    """
    df = df.copy()

    cols_fecha = ["Fecha", "Fecha vto.", "Fecha cmp."]
    for col in cols_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    cols_num = ["Imp.orig.", "Saldo Comp.", "SaldoTrs"]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            )

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Eliminar filas sin importe ni fecha (totales/subtotales)
    if "Imp.orig." in df.columns and "Fecha" in df.columns:
        df = df.dropna(subset=["Imp.orig.", "Fecha"], how="all")

    logger.debug("Cuenta corriente procesada")
    return df


def procesar_gastos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece el reporte de Gastos."""
    df = df.copy()

    # TODO: ajustar columnas reales
    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(
            df["Fecha"], dayfirst=True, errors="coerce"
        )

    logger.debug("Gastos procesados")
    return df


def procesar_ordenes_pago(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece las Órdenes de Pago.

    Columnas clave (ProntoNet): Numero, Fecha Pago, Cod, Tipo, Estado,
    Proveedor, Detalle de valores, Cuenta, Mon., Efectivo, Descuentos,
    Valores, Documentos, Acreedores, Obra, Observaciones, Confecciono,
    Fecha ing., Modifico, Fecha modif., Anulo, Fecha anulacion,
    Motivo anulacion, Rubro contable, ARBA, etc.
    """
    df = df.copy()

    cols_fecha = [
        "Fecha Pago",
        "Fecha ing.",
        "Fecha modif.",
        "Fecha anulacion",
        "Fecha Recibo Proveedor",
        "Fecha de reversion",
        "Fecha Rec.Prov.",
    ]
    for col in cols_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    cols_num = [
        "Efectivo",
        "Descuentos",
        "Valores",
        "Documentos",
        "Acreedores",
        "Ret.IVA",
        "Ret.gan.",
        "Ret.ing.b.",
        "Ret.SUSS",
        "Ret.OTROS",
        "Dev.F.F.",
        "Dif. Balanceo",
        "Cotiz. dolar",
    ]
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            )

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Eliminar filas sin numero ni fecha (totales/encabezados duplicados)
    if "Numero" in df.columns and "Fecha Pago" in df.columns:
        df = df.dropna(subset=["Numero", "Fecha Pago"], how="all")

    logger.debug("Órdenes de pago procesadas")
    return df


def procesar_listado_ordenes(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece el Listado Detallado de Órdenes de Pago.

    Columnas reales (ProntoNet): Fecha Orden Pago, Fecha Vencimiento Max,
    Entidad, Centro de Costos, Numero Orden Pago, Numero Valor,
    Importe, Fecha Valor.
    """
    df = df.copy()

    cols_fecha = ["Fecha Orden Pago", "Fecha Vencimiento Max", "Fecha Valor"]
    for col in cols_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    if "Importe" in df.columns:
        df["Importe"] = pd.to_numeric(
            df["Importe"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    if "Importe" in df.columns and "Fecha Orden Pago" in df.columns:
        df = df.dropna(subset=["Importe", "Fecha Orden Pago"], how="all")

    logger.debug("Listado detallado de órdenes procesado")
    return df


def procesar_obras(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y enriquece el reporte histórico de Obras.

    Columnas reales (ProntoNet): Numero, Tipo de obra, Descripcion, Cliente,
    Fecha inicio, Fecha entrega, Fecha finalizacion, Unidad operativa,
    Jefe de obra, Jefe regional, Activa?, Jerarquia contable,
    Valor obra, Régimen minero.
    """
    df = df.copy()

    cols_fecha = ["Fecha inicio", "Fecha entrega", "Fecha finalizacion"]
    for col in cols_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    if "Valor obra" in df.columns:
        df["Valor obra"] = pd.to_numeric(
            df["Valor obra"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

    if "Activa?" in df.columns:
        df["Activa?"] = (
            df["Activa?"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({"si": True, "sí": True, "s": True, "no": False, "n": False})
        )

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    logger.debug("Obras procesadas")
    return df

    logger.debug("Obras procesadas")
    return df


# ─── Orquestador ─────────────────────────────────────────────────────────────


def enriquecer_datos() -> dict[str, pd.DataFrame]:
    """
    Carga de archivos guiada por registry, aplica las transformaciones
    y devuelve un dict con los DataFrames enriquecidos mapeado a sus llaves.
    """
    logger.info("Iniciando enriquecimiento (guiado por Registry)...")
    raw = cargar_archivos()
    resultado: dict[str, pd.DataFrame] = {}
    # Procesadores asociados a sus llaves de registry
    procesadores = {
        "cuenta_corriente": procesar_cuenta_corriente,
        "gastos": procesar_gastos,
        "detallado_ordenes_pago": procesar_listado_ordenes,
        "ordenes_pago": procesar_ordenes_pago,
        "obras_activas": procesar_obras,
    }

    for key, df in raw.items():
        if key in procesadores:
            logger.info(f"  → Transformando: {key}")
            resultado[key] = procesadores[key](df)
        else:
            logger.warning(
                f"  → Reporte sin transformación especifica: '{key}'"
            )
            resultado[key] = df

    logger.success(f"Enriquecimiento completo: {list(resultado.keys())}")
    return resultado
