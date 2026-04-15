"""
src/utils/vpn_check.py
──────────────────────
Verifica y activa la VPN (FortiClient IPSec) antes de la descarga.

Credenciales en .env:
  VPN_NAME=VPN POSE IP SEC
  VPN_USER=rrivarola
  VPN_PASSWORD=tu_contraseña_vpn
  VPN_TARGET_IP=10.2.1.81
"""

import subprocess
import time
from pathlib import Path

from loguru import logger

from config.settings import VPN_NAME, VPN_PASSWORD, VPN_TARGET_IP, VPN_USER

_FORTI_EXE = Path(
    r"C:\Program Files\Fortinet\FortiClient\FortiClientConsole.exe"
)


def _vpn_activa() -> bool:
    """Devuelve True si el target IP responde a ping."""
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "3000", VPN_TARGET_IP],
        capture_output=True,
        timeout=10,
    )
    return result.returncode == 0


def _levantar_vpn() -> bool:
    """Intenta conectar la VPN con FortiClientConsole."""
    if not _FORTI_EXE.exists():
        logger.error(
            f"FortiClientConsole no encontrado: {_FORTI_EXE}"
        )
        return False
    logger.info(f"Conectando VPN '{VPN_NAME}' (usuario: {VPN_USER})")
    try:
        result = subprocess.run(
            [
                str(_FORTI_EXE),
                "-vpnconnect", VPN_NAME,
                "-vpnuser", VPN_USER,
                "-vpnpassword", VPN_PASSWORD,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        logger.error("FortiClient tardó más de 60 s — abortado.")
        return False
    if result.returncode != 0:
        logger.error(
            f"FortiClient falló (rc={result.returncode}): "
            f"{result.stderr.strip()}"
        )
        return False
    # Esperar a que el túnel quede completamente establecido
    time.sleep(5)
    return True


def asegurar_vpn() -> bool:
    """
    Verifica VPN activa; si no, intenta conectar con FortiClient.
    Retorna True si la VPN queda activa al final.
    """
    if _vpn_activa():
        logger.debug(f"VPN activa — {VPN_TARGET_IP} alcanzable.")
        return True
    logger.warning(
        f"VPN inactiva. Intentando conectar '{VPN_NAME}'..."
    )
    if _levantar_vpn() and _vpn_activa():
        logger.success("VPN activada correctamente.")
        return True
    logger.error(
        "No se pudo establecer VPN. "
        "Conectar manualmente con FortiClient."
    )
    return False
