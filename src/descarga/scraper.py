"""
src/descarga/scraper.py
───────────────────────
Automatiza el login y la descarga de reportes desde el sistema web
usando Playwright.  Se conecta al sistema, navega a cada reporte,
aplica los filtros necesarios y guarda los archivos en input_raw/.
"""

from __future__ import annotations

from pathlib import Path
from datetime import date

from loguru import logger
from playwright.sync_api import sync_playwright, Page, Download

from config.settings import (
    APP_URL,
    APP_USUARIO,
    APP_PASSWORD,
    CC_FECHA_DESDE,
    HEADLESS,
    TIMEOUT_MS,
    RUTA_DESCARGA,
)


import random


def _espera_humana(page: Page, min_ms: int = 1000, max_ms: int = 3000) -> None:
    """Añade una pausa aleatoria para simular comportamiento humano."""
    page.wait_for_timeout(random.randint(min_ms, max_ms))


# ─── Login ───────────────────────────────────────────────────────────────────


def _hacer_login(page: Page) -> None:
    """Navega al login y autentica con las credenciales."""
    logger.info(f"Navegando a {APP_URL}")
    page.goto(APP_URL, timeout=TIMEOUT_MS)

    _espera_humana(page, 2000, 4000)

    # Escribimos letra por letra para simular a una persona (delay)
    page.locator("#userName").press_sequentially(APP_USUARIO, delay=150)
    _espera_humana(page, 1000, 2000)

    page.locator("#Password").press_sequentially(APP_PASSWORD, delay=150)
    _espera_humana(page, 1000, 2000)

    # Clic en el botón LOGIN usando su ID
    page.click("#botonLogin")

    # Esperar a que cargue algún elemento post-login (ajustar selector)
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 3000, 5000)

    # ── Seleccionar empresa "Pose - 30-70910712-3" (id=1) ────────────────────
    # Interactuamos con el dropdown #bdDropdown de la navbar para que el JS
    # nativo de la página llame a SetBase correctamente (con CSRF y sesión).
    # select_option() cambia el valor del DOM pero NO dispara el evento
    # 'change' que el framework escucha → hay que dispararlo explícitamente.
    logger.info("Seleccionando empresa 'Pose - 30-70910712-3'...")
    page.wait_for_selector("#bdDropdown", state="visible", timeout=TIMEOUT_MS)
    page.select_option("#bdDropdown", value="1")
    page.evaluate(
        "document.querySelector('#bdDropdown')"
        ".dispatchEvent(new Event('change', {bubbles: true}))"
    )

    # Esperar a que el servidor procese SetBase y recargue el menú
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 2000, 3000)
    logger.info("Login y selección de empresa exitosos")


# ─── Descarga de un reporte individual ───────────────────────────────────────


def _descargar_archivo(
    page: Page,
    nav_url: str,
    nombre_destino: str,
) -> Path:
    """
    Navega a `nav_url`, hace clic en Actualizar con las fechas por defecto
    y descarga el Excel generado por DataTables.

    Retorna la ruta del archivo guardado.
    """
    logger.info(f"Descargando: {nombre_destino}")
    page.goto(nav_url, timeout=TIMEOUT_MS)
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 1500, 2500)

    # ── Clic en Actualizar (fechas por defecto, no se modifican) ─────────────
    # Algunos reportes tienen #botonActualizar;
    # otros cargan automáticamente al navegar.
    if page.locator("#botonActualizar").count() > 0:
        page.evaluate("document.getElementById('botonActualizar').click()")
        logger.info("  → Actualizando tabla con fechas por defecto...")
    else:
        logger.info("  → Tabla carga automáticamente (sin botonActualizar)...")

    # ── Esperar a que DataTables dibuje la tabla y aparezca el botón Excel ───
    try:
        page.wait_for_selector(
            "button.buttons-excel", state="attached", timeout=60000
        )
    except Exception:
        # Segundo intento: a veces DataTables tarda un poco más
        page.wait_for_timeout(5000)
        page.wait_for_selector(
            "button.buttons-excel", state="attached", timeout=30000
        )

    # ── Mostrar TODOS los registros antes de exportar ────────────────────────
    # DataTables exporta solo los registros visibles; cambiar el
    # selector a "All" (value="-1") para que el Excel contenga todo.
    page.select_option('select[name="Tabla_length"]', value="-1")
    logger.info("  → Selector de registros puesto en 'All'...")
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 1000, 2000)
    logger.info("  → Iniciando descarga Excel...")

    # ── Trigger descarga ─────────────────────────────────────────────────────
    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("button.buttons-excel", force=True)

    download: Download = dl_info.value
    destino = RUTA_DESCARGA / nombre_destino
    download.save_as(destino)
    logger.info(f"  → Guardado en: {destino}")
    return destino


# ─── Descarga especial: Cuenta Corriente Acreedores ──────────────────────────


def _descargar_cuenta_corriente(page: Page, nombre_destino: str) -> Path:
    """
    Descarga el reporte de Cuenta Corriente de Construya al Costo SRL.
    Flujo especial: destildar Pendiente, mostrar Todo, setear rango de fechas
    (inicio fijo 01/04/2026, fin = hoy) y exportar Excel.
    """
    URL = "http://10.2.1.81/CuentaCorriente/AcreedoresPorTransacciones?IdProveedor=43292"  # noqa: E501
    fecha_inicio = CC_FECHA_DESDE
    fecha_fin = date.today().strftime("%d/%m/%Y")
    rango_fecha = f"{fecha_inicio} - {fecha_fin}"

    logger.info(f"Descargando: {nombre_destino}")
    page.goto(URL, timeout=TIMEOUT_MS)
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 1500, 2500)

    # 1. Destildar "Pendiente" (primer checkbox)
    chk_pendiente = page.locator("#Pendiente_chk").first
    if chk_pendiente.is_checked():
        chk_pendiente.uncheck()
        logger.info("  → Destildado: Pendiente_chk")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
        _espera_humana(page, 500, 1000)

    # 2. Mostrar All en la primera tabla
    page.select_option('select[name="Tabla_length"]', value="-1")
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 500, 1000)

    # 3. Tildar "Todo"
    chk_todo = page.locator("#Todo_chk")
    if not chk_todo.is_checked():
        chk_todo.check()
        logger.info("  → Tildado: Todo_chk")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
        _espera_humana(page, 500, 1000)

    # 4. Setear rango de fecha (inicio fijo 01/04/2026, fin = hoy)
    page.fill("#filtroFecha", rango_fecha)
    logger.info(f"  → Fecha seteada: {rango_fecha}")
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 1000, 2000)

    # 5. Destildar Pendiente nuevamente (segundo checkbox del detalle)
    chk_pendiente2 = page.locator("#Pendiente_chk").last
    if chk_pendiente2.is_checked():
        chk_pendiente2.uncheck()
        logger.info("  → Destildado: Pendiente_chk (detalle)")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
        _espera_humana(page, 500, 1000)

    # 6. Esperar botón Excel y exportar
    page.wait_for_selector(
        "button.buttons-excel", state="attached", timeout=60000
    )
    _espera_humana(page, 500, 1000)
    logger.info("  → Iniciando descarga Excel...")

    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("button.buttons-excel", force=True)

    download: Download = dl_info.value
    destino = RUTA_DESCARGA / nombre_destino
    download.save_as(destino)
    logger.info(f"  → Guardado en: {destino}")
    return destino


# ─── Descarga especial: Obras ────────────────────────────────────────────────


def _descargar_obras(page: Page, nombre_destino: str) -> Path:
    """
    Descarga el reporte de Obras (histórico completo).

    Flujo:
      1. Navegar a /Obra/Index.
      2. Seleccionar "Todas" en el dropdown #Activas (value="T") y
         esperar a que el formulario recargue la tabla.
      3. Mostrar todos los registros en DataTables (value="-1").
      4. Exportar con el botón Excel.
    """
    URL = "http://10.2.1.81/Obra/Index"

    logger.info(f"Descargando: {nombre_destino}")
    page.goto(URL, timeout=TIMEOUT_MS)
    page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
    _espera_humana(page, 1500, 2500)

    # 1. Seleccionar "Todas" en el dropdown de estado
    page.wait_for_selector("#Activas", state="visible", timeout=TIMEOUT_MS)
    valor_actual = page.locator("#Activas").input_value()
    if valor_actual != "T":
        page.select_option("#Activas", value="T")
        logger.info("  → Estado puesto en 'Todas'")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
        _espera_humana(page, 1000, 2000)
    else:
        logger.info("  → Estado ya era 'Todas'")

    # 2. Mostrar todos los registros antes de exportar
    length_select = 'select[name="Tabla_length"]'
    if page.locator(length_select).count() > 0:
        page.select_option(length_select, value="-1")
        logger.info("  → Selector de registros puesto en 'All'")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
        _espera_humana(page, 1000, 2000)

    # 3. Esperar botón Excel y exportar
    page.wait_for_selector(
        "button.buttons-excel", state="attached", timeout=60000
    )
    _espera_humana(page, 500, 1000)
    logger.info("  → Iniciando descarga Excel...")

    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("button.buttons-excel", force=True)

    download: Download = dl_info.value
    destino = RUTA_DESCARGA / nombre_destino
    download.save_as(destino)
    logger.info(f"  → Guardado en: {destino}")
    return destino


# ─── Orquestador principal ───────────────────────────────────────────────────


def descargar_todos_los_reportes(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> list[Path]:
    """
    Abre el navegador, hace login, selecciona la empresa
    y descarga todos los reportes.
    Las fechas se dejan por defecto (el sistema las pre-carga automáticamente).
    """
    if fecha_hasta is None:
        fecha_hasta = date.today()

    # ── Definir reportes a descargar ─────────────────────────────────────────
    # Cada entrada: (url_relativa_al_login, nombre_archivo_destino)
    REPORTES = [
        (
            "http://10.2.1.81/Consulta/ProveedoresListadoOrdenesPagoDetallado3",  # noqa: E501
            "Listado Detallado de Órdenes de Pago - Pronto.xlsx",
        ),
        (
            "http://10.2.1.81/OrdenPago/",
            "Ordenes de Pago - Pronto.xlsx",
        ),
        # Pendientes con URLs reales:
        # (
        #     "http://10.2.1.81/Reportes/Gastos",
        #     "Gastos.xlsx",
        # ),
    ]

    archivos_descargados: list[Path] = []

    with sync_playwright() as pw:
        # Configuramos Chromium para evitar detección de bots
        browser = pw.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        context = browser.new_context(
            accept_downloads=True,
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",  # noqa: E501
            viewport={"width": 1366, "height": 768},
        )

        # Ocultar webdriver mediante un script en cada página nueva
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"  # noqa: E501
        )

        page = context.new_page()

        try:
            _hacer_login(page)

            for url_reporte, nombre in REPORTES:
                ruta = _descargar_archivo(
                    page,
                    nav_url=url_reporte,
                    nombre_destino=nombre,
                )
                archivos_descargados.append(ruta)
                _espera_humana(page, 3000, 5000)

            # Cuenta corriente: flujo especial con filtros propios
            ruta_cc = _descargar_cuenta_corriente(
                page,
                nombre_destino="Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx",  # noqa: E501
            )
            archivos_descargados.append(ruta_cc)
            _espera_humana(page, 3000, 5000)

            # Obras: flujo especial con filtro de estado
            ruta_obras = _descargar_obras(
                page,
                nombre_destino="Obras - Pronto Hist.xlsx",
            )
            archivos_descargados.append(ruta_obras)

        except Exception as exc:
            logger.error(f"Error durante la descarga: {exc}")
            raise
        finally:
            context.close()
            browser.close()

    logger.success(f"Descarga completa: {len(archivos_descargados)} archivos")
    return archivos_descargados
