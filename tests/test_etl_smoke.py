"""
tests/test_etl_smoke.py
────────────────────────
Tests de humo para src/etl/.
Verifican la sintaxis de todos los módulos y ejecutan el pipeline
extremo a extremo con fixtures CSV y Excel mínimos.
"""

import ast
from pathlib import Path

import pandas as pd
import pytest

from src.etl.config import ConfigETL
from src.etl.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse(rel_path: str) -> None:
    src = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    ast.parse(src)


# ---------------------------------------------------------------------------
# Sintaxis
# ---------------------------------------------------------------------------


def test_syntax_etl_config():
    _parse("src/etl/config.py")


def test_syntax_etl_ingesta():
    _parse("src/etl/ingesta.py")


def test_syntax_etl_transformacion():
    _parse("src/etl/transformacion.py")


def test_syntax_etl_carga():
    _parse("src/etl/carga.py")


def test_syntax_etl_reportes():
    _parse("src/etl/reportes.py")


def test_syntax_etl_pipeline():
    _parse("src/etl/pipeline.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def config_tmp(tmp_path: Path) -> ConfigETL:
    cfg = ConfigETL()
    cfg.directorio_datos = tmp_path
    cfg.reportes.directorio_salida = tmp_path
    return cfg


@pytest.fixture
def csv_fixture(tmp_path: Path) -> Path:
    contenido = (
        "id_registro;fecha;variable;valor;unidad;centro_costo\n"
        "1;2024-01-15;VAR_A;150;USD;CC01\n"
        "2;2024-01-15;VAR_B;200;USD;CC02\n"
        "3;2024-01-16;VAR_A;180;USD;CC01\n"
    )
    ruta = tmp_path / "muestra.csv"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


@pytest.fixture
def excel_fixture(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "id_registro": ["1", "2"],
            "fecha": ["2024-01-15", "2024-01-15"],
            "variable": ["VAR_A", "VAR_B"],
            "valor": ["150", "200"],
            "unidad": ["USD", "USD"],
            "centro_costo": ["CC01", "CC02"],
        }
    )
    ruta = tmp_path / "muestra.xlsx"
    df.to_excel(ruta, index=False)
    return ruta


# ---------------------------------------------------------------------------
# Smoke: pipeline extremo a extremo
# ---------------------------------------------------------------------------


def test_pipeline_csv_smoke(csv_fixture: Path, config_tmp: ConfigETL):
    pipeline = Pipeline(config_tmp)
    stats = pipeline.ejecutar(
        fuente="csv",
        archivo=str(csv_fixture),
        fecha="20240115",
    )
    assert stats["registros_extraidos"] == 3
    assert stats["registros_validos"] >= 0
    assert Path(stats["ruta_reporte"]).exists()


def test_pipeline_excel_smoke(excel_fixture: Path, config_tmp: ConfigETL):
    pipeline = Pipeline(config_tmp)
    stats = pipeline.ejecutar(
        fuente="excel",
        archivo=str(excel_fixture),
        fecha="20240115",
    )
    assert stats["registros_extraidos"] == 2
    assert Path(stats["ruta_reporte"]).exists()
