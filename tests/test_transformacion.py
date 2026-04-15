"""Pruebas unitarias del módulo de Transformación y Reglas de Negocio."""

import pandas as pd
import pytest

from src.etl.transformacion import Transformacion
from src.reglas_negocio.reglas import (
    asignar_categoria_distribucion,
    calcular_distribucion_diaria,
    calcular_variacion_respecto_anterior,
    clasificar_alerta,
    validar_campos_obligatorios,
    validar_rango_valor,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def df_valido():
    return pd.DataFrame(
        {
            "id_registro": ["1", "2", "3"],
            "fecha": ["2024-01-01", "2024-01-01", "2024-01-01"],
            "variable": ["VAR_A", "VAR_A", "VAR_B"],
            "valor": ["100", "300", "200"],
            "unidad": ["USD", "USD", "USD"],
            "centro_costo": ["CC01", "CC02", "CC01"],
        }
    )


@pytest.fixture
def df_con_errores():
    return pd.DataFrame(
        {
            "id_registro": ["1", None, "3"],
            "fecha": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "variable": ["VAR_A", "VAR_B", "VAR_C"],
            "valor": ["100", "-5", "200"],
            "unidad": ["USD", "USD", "USD"],
            "centro_costo": ["CC01", "CC02", None],
        }
    )


# ---------------------------------------------------------------------------
# Normalización de columnas
# ---------------------------------------------------------------------------


def test_normalizar_columnas_minusculas():
    t = Transformacion()
    df = pd.DataFrame({"FECHA Proceso": [1], "Valor $": [2]})
    resultado = t.normalizar_columnas(df)
    assert "fecha_proceso" in resultado.columns
    assert "valor__" in resultado.columns or "valor_" in resultado.columns


def test_normalizar_columnas_tildes():
    t = Transformacion()
    df = pd.DataFrame({"Año Período": [1]})
    resultado = t.normalizar_columnas(df)
    # ñ → n, tilde en é → e, espacio → _
    assert "ano_periodo" in resultado.columns


# ---------------------------------------------------------------------------
# Limpieza de espacios
# ---------------------------------------------------------------------------


def test_limpiar_espacios_texto():
    t = Transformacion()
    df = pd.DataFrame({"nombre": ["  Juan  ", " Ana "]})
    resultado = t.limpiar_espacios(df)
    assert resultado["nombre"].tolist() == ["Juan", "Ana"]


# ---------------------------------------------------------------------------
# Conversión de fecha
# ---------------------------------------------------------------------------


def test_convertir_fecha_iso():
    t = Transformacion()
    df = pd.DataFrame({"fecha": ["2024-01-15"]})
    resultado = t.convertir_fecha(df)
    assert pd.api.types.is_datetime64_any_dtype(resultado["fecha"])


def test_convertir_fecha_invalida_genera_nat():
    t = Transformacion()
    df = pd.DataFrame({"fecha": ["no-es-fecha"]})
    resultado = t.convertir_fecha(df)
    assert resultado["fecha"].isna().all()


# ---------------------------------------------------------------------------
# Conversión de valor numérico
# ---------------------------------------------------------------------------


def test_convertir_valor_numerico_punto_decimal():
    t = Transformacion()
    df = pd.DataFrame({"valor": ["1234.56"]})
    resultado = t.convertir_valor_numerico(df)
    assert resultado["valor"].iloc[0] == pytest.approx(1234.56)


def test_convertir_valor_coma_decimal():
    t = Transformacion()
    df = pd.DataFrame({"valor": ["1.234,56"]})
    resultado = t.convertir_valor_numerico(df)
    assert resultado["valor"].iloc[0] == pytest.approx(1234.56)


# ---------------------------------------------------------------------------
# Reglas de negocio: validaciones
# ---------------------------------------------------------------------------


def test_validar_campos_obligatorios_detecta_nulos(df_con_errores):
    resultado = validar_campos_obligatorios(df_con_errores)
    # Fila 1 (índice 1) tiene id_registro=None
    assert resultado["error_campos"].iloc[1] != ""
    # Fila 0 y 2 también: fila 2 tiene centro_costo=None
    assert resultado["error_campos"].iloc[2] != ""


def test_validar_rango_valor_marca_negativos(df_con_errores):
    df = df_con_errores.copy()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    # Reemplazar para que la función pueda operar
    df["valor"] = df["valor"].astype(str)
    resultado = validar_rango_valor(df)
    # Valor "-5" debe quedar fuera de rango
    assert resultado["fuera_rango"].iloc[1]


def test_validar_rango_valor_acepta_valores_normales(df_valido):
    resultado = validar_rango_valor(df_valido)
    assert not resultado["fuera_rango"].any()


# ---------------------------------------------------------------------------
# Reglas de negocio: cálculos
# ---------------------------------------------------------------------------


def test_calcular_distribucion_diaria_suma_100(df_valido):
    df = df_valido.copy()
    df["valor_num"] = pd.to_numeric(df["valor"])
    resultado = calcular_distribucion_diaria(df)
    # Para VAR_A en 2024-01-01: valores 100 y 300 → total 400
    fila_var_a_cc01 = resultado[
        (resultado["variable"] == "VAR_A")
        & (resultado["centro_costo"] == "CC01")
    ]
    assert fila_var_a_cc01["participacion_pct"].iloc[0] == pytest.approx(
        25.0, rel=1e-3
    )


def test_calcular_variacion_genera_columna(df_valido):
    df = df_valido.copy()
    df["valor"] = pd.to_numeric(df["valor"])
    df["valor_num"] = df["valor"]
    resultado = calcular_variacion_respecto_anterior(df)
    assert "variacion_pct" in resultado.columns


def test_clasificar_alerta_marca_variacion_alta():
    df = pd.DataFrame(
        {
            "variable": ["VAR_A", "VAR_A"],
            "centro_costo": ["CC01", "CC01"],
            "fecha": ["2024-01-01", "2024-01-02"],
            "valor": [100.0, 200.0],
            "valor_num": [100.0, 200.0],
        }
    )
    df = calcular_variacion_respecto_anterior(df)
    df = clasificar_alerta(df)
    # Variación del 100 % > umbral del 20 %
    assert df["alerta"].iloc[1]


def test_asignar_categoria_distribucion():
    df = pd.DataFrame(
        {
            "fecha": ["2024-01-01"] * 4,
            "variable": ["VAR_A"] * 4,
            "valor": [70.0, 30.0, 10.0, 5.0],
            "valor_num": [70.0, 30.0, 10.0, 5.0],
        }
    )
    resultado = calcular_distribucion_diaria(df)
    resultado = asignar_categoria_distribucion(resultado)
    assert "categoria" in resultado.columns


# ---------------------------------------------------------------------------
# Pipeline de transformación completo
# ---------------------------------------------------------------------------


def test_transformar_separa_validos_e_invalidos(df_valido, df_con_errores):
    t = Transformacion()
    df_mixto = pd.concat([df_valido, df_con_errores], ignore_index=True)
    validos, invalidos = t.transformar(df_mixto)
    assert len(validos) + len(invalidos) == len(df_mixto)
    assert "motivo_rechazo" in invalidos.columns


def test_transformar_dataframe_valido_sin_rechazos(df_valido):
    t = Transformacion()
    validos, invalidos = t.transformar(df_valido)
    assert len(validos) == len(df_valido)
    assert invalidos.empty
