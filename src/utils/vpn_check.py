"""
src/utils/vpn_check.py
──────────────────────
Verifica y activa la VPN (WireGuard) antes de la descarga.

Requiere passwordless sudo para wg-quick en el host:
  echo "ALL=(ALL) NOPASSWD: /usr/bin/wg-quick" \\
      | sudo tee /etc/sudoers.d/wg-quick
"""

import subprocess

from loguru import logger

from config.settings import VPN_INTERFACE, VPN_TARGET_IP


def _vpn_activa() -> bool:
    """Devuelve True si el target IP responde a ping (max 3 s)."""
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "3", VPN_TARGET_IP],
        capture_output=True,
        timeout=5,
    )
    return result.returncode == 0


def _levantar_vpn() -> bool:
    """Intenta levantar la interfaz WireGuard con wg-quick."""
    logger.info(f"Levantando VPN: wg-quick up {VPN_INTERFACE}")
    try:
        result = subprocess.run(
            ["sudo", "wg-quick", "up", VPN_INTERFACE],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        logger.error("wg-quick tardó más de 30 s — abortado.")
        return False
    if result.returncode != 0:
        logger.error(
            f"wg-quick falló (rc={result.returncode}): "
            f"{result.stderr.strip()}"
        )
        return False
    return True


def asegurar_vpn() -> bool:
    """
    Verifica VPN activa; si no, intenta activarla con wg-quick.
    Retorna True si la VPN queda activa al final.
    """
    if _vpn_activa():
        logger.debug(f"VPN activa — {VPN_TARGET_IP} alcanzable.")
        return True
    logger.warning(f"VPN inactiva. Intentando wg-quick up {VPN_INTERFACE}...")
    if _levantar_vpn() and _vpn_activa():
        logger.success("VPN activada correctamente.")
        return True
    logger.error(
        "No se pudo establecer VPN. "
        f"Activar manualmente: sudo wg-quick up {VPN_INTERFACE}"
    )
    return False
