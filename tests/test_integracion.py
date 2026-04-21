"""
tests/test_integracion.py
──────────────────────────
Test de integración para main.py --solo-procesar.

Verifica que los pasos 2-4 del flujo principal se ejecutan
sin errores usando mocks para módulos que requieren sistema real.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import main as main_mod


def test_main_solo_procesar_retorna_0(tmp_path: Path, monkeypatch):
    """main() --solo-procesar debe retornar 0 con dependencias mockeadas."""
    monkeypatch.setattr(sys, "argv", ["main.py", "--solo-procesar"])

    mock_informe = tmp_path / "informe.xlsx"
    mock_reporte = tmp_path / "reporte.xlsx"
    mock_informe.touch()
    mock_reporte.touch()

    with (
        patch(
            "src.procesamiento.enriquecimiento.enriquecer_datos",
            return_value={"datos": "mock"},
        ),
        patch(
            "src.reportes.generador.generar_informe_diario",
            return_value=mock_informe,
        ),
        patch(
            "src.reportes.generador.generar_resumen_excel",
            return_value=mock_reporte,
        ),
    ):
        resultado = main_mod.main()

    assert resultado == 0
