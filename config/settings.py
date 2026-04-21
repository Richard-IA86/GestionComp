"""
config/settings.py
──────────────────
Configuración centralizada del proyecto.
Lee variables desde .env y define rutas, constantes y parámetros globales.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ─── Rutas base ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ─── Rutas del proyecto ──────────────────────────────────────────────────────
INPUT_RAW_DIR = BASE_DIR / "input_raw"
OUTPUT_DIR = BASE_DIR / "output"
REPORTES_DIR = OUTPUT_DIR / "reportes"
INFORMES_DIR = OUTPUT_DIR / "informes_direccion"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "src" / "reportes" / "templates"

# Crear directorios si no existen
for _dir in [
    INPUT_RAW_DIR,
    REPORTES_DIR,
    INFORMES_DIR,
    LOGS_DIR,
    TEMPLATES_DIR,
]:
    _dir.mkdir(parents=True, exist_ok=True)

# ─── Credenciales y URL ──────────────────────────────────────────────────────
APP_URL = os.getenv("APP_URL", "http://10.2.1.81/Account/Login")
APP_USUARIO = os.getenv("APP_USUARIO", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

# ─── Configuración del navegador ─────────────────────────────────────────────
MODO_NAVEGADOR = os.getenv(
    "MODO_NAVEGADOR", "visible"
)  # "visible" | "headless"
HEADLESS = MODO_NAVEGADOR.lower() == "headless"
TIMEOUT_MS = 30_000  # 30 segundos por defecto para esperas Playwright

# ─── Configuración de descargas ──────────────────────────────────────────────
_ruta_descarga = os.getenv("RUTA_DESCARGA", "")
RUTA_DESCARGA = Path(_ruta_descarga) if _ruta_descarga else INPUT_RAW_DIR

# ─── Archivos esperados (nombres como aparecen en el sistema) ────────────────
ARCHIVOS_ESPERADOS = [
    "Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx",
    "Gastos.xlsx",
    "Listado Detallado de Órdenes de Pago - Pronto.xlsx",
    "Obras - Pronto Hist.xlsx",
    "Ordenes de Pago - Pronto.xlsx",
]

# ─── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
# ─── VPN ─────────────────────────────────────────────────────────────────────
VPN_NAME = os.getenv("VPN_NAME", "VPN POSE IP SEC")
VPN_USER = os.getenv("VPN_USER", "")
VPN_PASSWORD = os.getenv("VPN_PASSWORD", "")
VPN_TARGET_IP = os.getenv("VPN_TARGET_IP", "10.2.1.81")

LOG_FILE = LOGS_DIR / "compensaciones.log"

# ─── Política de retención ───────────────────────────────────────────────────
RETENCION_REPORTES_DIAS = int(os.getenv("RETENCION_REPORTES_DIAS", "90"))
RETENCION_LOGS_DIAS = int(os.getenv("RETENCION_LOGS_DIAS", "30"))

# ─── Rango de fechas de análisis ────────────────────────────────────────────
# Fecha de inicio fija del período analizado (formato DD/MM/YYYY).
# Cambiar en .env cuando se quiera ampliar el período histórico.
CC_FECHA_DESDE = os.getenv("CC_FECHA_DESDE", "01/04/2026")
