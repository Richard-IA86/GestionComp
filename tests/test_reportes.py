"""Pruebas unitarias del módulo de Reportes."""

import pandas as pd
import pytest

from src.etl.config import ConfigETL
from src.etl.reportes import GeneradorReportes


@pytest.fixture
def config(tmp_path):
    cfg = ConfigETL()
    cfg.reportes.directorio_salida = tmp_path
    cfg.reportes.formato = "xlsx"
    return cfg


@pytest.fixture
def generador(config):
    return GeneradorReportes(config)


@pytest.fixture
def df_procesado():
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                ["2024-01-01", "2024-01-01", "2024-01-02"]
            ),
            "variable": ["VAR_A", "VAR_B", "VAR_A"],
            "valor_num": [100.0, 200.0, 150.0],
            "centro_costo": ["CC01", "CC02", "CC01"],
            "participacion_pct": [33.33, 66.67, 100.0],
            "variacion_pct": [None, None, 50.0],
            "alerta": [False, False, True],
            "categoria": ["C", "B", "A"],
        }
    )


def test_resumen_diario_genera_archivo(generador, df_procesado, tmp_path):
    ruta = generador.resumen_diario(df_procesado, fecha="20240101")
    assert ruta.exists()
    assert "resumen_diario" in ruta.name


def test_alertas_diarias_genera_archivo(generador, df_procesado, tmp_path):
    ruta = generador.alertas_diarias(df_procesado, fecha="20240101")
    assert ruta.exists()
    assert "alertas_diarias" in ruta.name


def test_alertas_diarias_sin_columna_alerta(generador, tmp_path):
    df = pd.DataFrame({"variable": ["VAR_A"], "valor_num": [100.0]})
    ruta = generador.alertas_diarias(df, fecha="20240101")
    assert ruta.exists()


def test_distribucion_centro_costo_genera_archivo(
    generador, df_procesado, tmp_path
):
    ruta = generador.distribucion_centro_costo(df_procesado, fecha="20240101")
    assert ruta.exists()
    assert "distribucion_cc" in ruta.name


def test_reporte_completo_genera_excel_con_hojas(
    generador, df_procesado, tmp_path
):
    df_invalidos = pd.DataFrame(
        {"id_registro": ["99"], "motivo_rechazo": ["campo faltante"]}
    )
    ruta = generador.reporte_completo(
        df_procesado, df_invalidos, fecha="20240101"
    )
    assert ruta.exists()
    assert "reporte_completo" in ruta.name

    # Verificar que el Excel contiene múltiples hojas
    hojas = pd.ExcelFile(ruta).sheet_names
    assert len(hojas) >= 2


def test_resumen_diario_csv(config, df_procesado, tmp_path):
    config.reportes.formato = "csv"
    generador_csv = GeneradorReportes(config)
    ruta = generador_csv.resumen_diario(df_procesado, fecha="20240101")
    assert ruta.suffix == ".csv"
    assert ruta.exists()
