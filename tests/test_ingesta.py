"""Pruebas unitarias del módulo de Ingesta."""

import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.etl.config import ConfigETL
from src.etl.ingesta import Ingesta


@pytest.fixture
def config(tmp_path):
    cfg = ConfigETL()
    cfg.directorio_datos = tmp_path
    return cfg


@pytest.fixture
def ingesta(config):
    return Ingesta(config)


# ---------------------------------------------------------------------------
# Ingesta CSV
# ---------------------------------------------------------------------------


def test_desde_csv_lee_archivo(tmp_path, ingesta):
    contenido = (
        "id_registro;fecha;variable;valor;unidad;centro_costo\n"
        "1;2024-01-01;VAR_A;100;USD;CC01\n"
    )
    ruta = tmp_path / "datos.csv"
    ruta.write_text(contenido, encoding="utf-8")

    df = ingesta.desde_csv(ruta)

    assert len(df) == 1
    assert list(df.columns) == [
        "id_registro",
        "fecha",
        "variable",
        "valor",
        "unidad",
        "centro_costo",
    ]
    assert df["valor"].iloc[0] == "100"


def test_desde_csv_archivo_inexistente_lanza_error(ingesta):
    with pytest.raises(FileNotFoundError):
        ingesta.desde_csv("/ruta/inexistente/datos.csv")


# ---------------------------------------------------------------------------
# Ingesta Excel
# ---------------------------------------------------------------------------


def test_desde_excel_lee_archivo(tmp_path, ingesta):
    df_origen = pd.DataFrame(
        {"id_registro": ["1"], "fecha": ["2024-01-01"], "valor": ["50"]}
    )
    ruta = tmp_path / "datos.xlsx"
    df_origen.to_excel(ruta, index=False)

    df = ingesta.desde_excel(ruta)

    assert len(df) == 1
    assert "id_registro" in df.columns


# ---------------------------------------------------------------------------
# Ingesta JSON
# ---------------------------------------------------------------------------


def test_desde_json_lee_archivo(tmp_path, ingesta):
    datos = [{"id_registro": "1", "valor": "200"}]
    ruta = tmp_path / "datos.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")

    df = ingesta.desde_json(ruta)

    assert len(df) == 1
    assert df["valor"].iloc[0] == "200"


# ---------------------------------------------------------------------------
# Ingesta API
# ---------------------------------------------------------------------------


def test_desde_api_lista(ingesta):
    respuesta_mock = MagicMock()
    respuesta_mock.json.return_value = [{"id": "1", "valor": "300"}]
    respuesta_mock.raise_for_status = MagicMock()

    with patch("src.etl.ingesta.requests.get", return_value=respuesta_mock):
        df = ingesta.desde_api("variables/diarias")

    assert len(df) == 1
    assert df["valor"].iloc[0] == "300"


def test_desde_api_objeto_con_data(ingesta):
    respuesta_mock = MagicMock()
    respuesta_mock.json.return_value = {
        "data": [{"id": "2", "valor": "400"}],
        "total": 1,
    }
    respuesta_mock.raise_for_status = MagicMock()

    with patch("src.etl.ingesta.requests.get", return_value=respuesta_mock):
        df = ingesta.desde_api("variables/diarias")

    assert len(df) == 1
    assert df["valor"].iloc[0] == "400"
