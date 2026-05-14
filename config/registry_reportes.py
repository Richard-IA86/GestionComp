"""
config/registry_reportes.py
───────────────────────────
Registro de reportes a extraer desde ProntoNet para Compensaciones.
Centraliza qué reportes se descargan, contra qué tabla de BD van, y
sus columnas de validación.
"""

from typing import Any

# Estructura del Registry
# - archivo_esperado: Nombre real del archivo devuelto por el portal.
# - activo: True si se debe descargar/procesar en el ciclo actual.
# - tabla_bd_destino: Tabla en PostgreSQL donde se inyectará.
# - funcion_scraper: Alias lógico usado por el scraper (Playwright).
# - columnas_esperadas: Columnas indispensables para validación QA.

REGISTRY_REPORTES: dict[str, dict[str, Any]] = {
    "cuenta_corriente": {
        "archivo_esperado": (
            "Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx"
        ),
        "activo": True,
        "tabla_bd_destino": "compensaciones.cuenta_corriente",
        "funcion_scraper": "descargar_cuenta_corriente",
        "columnas_esperadas": [],
    },
    "obras_activas": {
        "archivo_esperado": "Obras - Pronto Hist.xlsx",
        "activo": True,
        "tabla_bd_destino": "compensaciones.obras",
        "funcion_scraper": "descargar_obras",
        "columnas_esperadas": [],
    },
    "gastos": {
        "archivo_esperado": "Gastos.xlsx",
        "activo": False,  # Se activará en Paso 2 al agregar la funcionalidad
        "tabla_bd_destino": "compensaciones.gastos",
        "funcion_scraper": "descargar_gastos",
        "columnas_esperadas": [],
    },
    "ordenes_pago": {
        "archivo_esperado": "Ordenes de Pago - Pronto.xlsx",
        "activo": True,
        "tabla_bd_destino": "compensaciones.ordenes_pago",
        "funcion_scraper": "descargar_ordenes_pago",
        "columnas_esperadas": [],
    },
    "detallado_ordenes_pago": {
        "archivo_esperado": (
            "Listado Detallado de Órdenes de Pago - Pronto.xlsx"
        ),
        "activo": True,
        "tabla_bd_destino": "compensaciones.ordenes_pago_detalle",
        "funcion_scraper": "descargar_detallado_ordenes_pago",
        "columnas_esperadas": [],
    },
    "debitos_creditos_bancarios": {
        "archivo_esperado": "Reporte_Debitos_Creditos_Bancarios.xlsx",
        "activo": True,
        "tabla_bd_destino": "compensaciones.debitos_creditos_bancarios",
        "funcion_scraper": "descargar_debitos_creditos",
        "columnas_esperadas": [],
    },
}
