"""
tests/test_smoke.py
────────────────────
Smoke tests: estructura del proyecto y sintaxis de los módulos.
Sin dependencias externas — ejecutable con python3 del sistema.
"""

import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse(rel_path: str) -> None:
    src = (BASE_DIR / rel_path).read_text(encoding="utf-8")
    ast.parse(src)


def test_estructura_directorios():
    assert (BASE_DIR / "config").is_dir()
    assert (BASE_DIR / "src" / "descarga").is_dir()
    assert (BASE_DIR / "src" / "procesamiento").is_dir()
    assert (BASE_DIR / "src" / "reportes").is_dir()
    assert (BASE_DIR / "src" / "utils").is_dir()


def test_archivos_principales_existen():
    assert (BASE_DIR / "main.py").exists()
    assert (BASE_DIR / "requirements.txt").exists()
    assert (BASE_DIR / "config" / "settings.py").exists()


def test_syntax_main():
    _parse("main.py")


def test_syntax_settings():
    _parse("config/settings.py")


def test_syntax_scraper():
    _parse("src/descarga/scraper.py")


def test_syntax_enriquecimiento():
    _parse("src/procesamiento/enriquecimiento.py")


def test_syntax_generador():
    _parse("src/reportes/generador.py")


def test_syntax_logger():
    _parse("src/utils/logger.py")
