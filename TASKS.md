# TASKS — Compensaciones POSE

## Backlog

### En curso
- [ ] Proximo chat: prueba empirica de formulario de solicitud de reporte (usuario no tecnico)
- [ ] Completar lógica de `src/procesamiento/enriquecimiento.py` con columnas reales (ver archivos en `input_raw/`)
- [ ] Completar lógica de `src/reportes/generador.py` con formato final del informe de dirección

### Pendiente — Infraestructura
- [x] Configurar tarea programada en Windows (Programador de Tareas) para `ejecutar_diario.ps1`
- [x] Actualizar `scripts/ejecutar_diario.ps1`: eliminar bloque de ping VPN redundante (lo maneja `main.py` paso 0/4)
- [x] Definir política de retención de archivos en `output/reportes/` y `logs/`
- [ ] Definir esquema de BD destino para el ETL (`src/etl/carga.py` → `a_bd()`)

### Pendiente — Funcionalidad
- [x] Revisar y corregir selectores Playwright en `scraper.py` con sistema real
  - Fix: `dispatchEvent('change')` en `#bdDropdown` para que el JS de SetBase se dispare correctamente
- [ ] Completar `procesar_cuenta_corriente()`: columnas reales disponibles (1694 filas, 11 cols)
- [ ] Completar `procesar_listado_ordenes()`: columnas reales disponibles (1280 filas, 11 cols)
- [ ] Completar `procesar_ordenes_pago()`: columnas reales disponibles (768 filas, 52 cols)
- [ ] Completar `procesar_obras()`: columnas reales disponibles (572 filas, 14 cols)
- [ ] Paso 4/4 ETL: decidir si mapear columnas reales al schema ETL o sacar estos archivos del loop
- [ ] Completar lógica de `src/reportes/generador.py` con formato final del informe de dirección
- [ ] Agregar URL de Gastos y activar su descarga en `scraper.py` (actualmente comentado)

### Pendiente — QA
- [x] Agregar tests de humo para `src/etl/` con archivos Excel de muestra
- [x] Agregar test de integración `main.py --solo-procesar` con fixtures

### Ideas / futuro

- [ ] Notificación por email/Teams al finalizar el proceso
- [ ] Dashboard de seguimiento de errores por fecha

---

## Log de trabajo

### 2026-05-12 (Plan del día)
- [x] **Advertencias IR:** `WARN: Commits sin bajar` en `gestion_comp` (Resuelto con rebase).
- [x] **Tarea 1:** Definir y discutir la arquitectura de ingesta. (Implementado Registry Reportes para enrutamiento seguro).
- [x] **Tarea 2:** Probar flujo de archivos manuales vs automatizados. Testeado mock de arquitectura (`--solo-procesar`).
- [x] **Tarea 3:** Actualización docs de ProntoNet a la nueva arquitectura.\n- **Cierre de jornada**: El usuario se retira al curso de análisis de datos a las 19:00 hs.

### 2026-04-20
- **Inicio de jornada**: QA diario completo (black + flake8 + mypy + pytest)
- black: 28 archivos sin cambios
- flake8: 0 errores | mypy: 0 errores en 28 archivos | pytest: 36/36 passed
- Tarea programada `Compensaciones_Diario` configurada en Programador de Tareas (21:00 diario, pwsh ruta absoluta, RunLevel Highest)
- Política de retención: `src/utils/retencion.py`, vars en `config/settings.py` (90d reportes / 30d logs), integrado en `main.py`
- Tests de humo ETL: `tests/test_etl_smoke.py` (6 syntax + 2 pipeline E2E con CSV/Excel)
- Test integración: `tests/test_integracion.py` (`main --solo-procesar` mockeado)
- Suite total: 45/45 passed
- Bajada automática de Obras: `_descargar_obras()` en `scraper.py` (filtro #Activas="T"), `Obras - Pronto Hist.xlsx` en `ARCHIVOS_ESPERADOS`, `procesar_obras()` en `enriquecimiento.py`
- Fix routing enriquecimiento: "órdenes" con acento no matcheaba → condición adicional `"órdenes" in clave_lower`
- Fix `validar_rango_valor()`: defensivo ante ausencia de columna 'valor' (warning, no KeyError)
- `CC_FECHA_DESDE` movido de hardcode a `config/settings.py` + `.env` (default `01/04/2026`)
- Pausa 3-5s entre reportes en `descargar_todos_los_reportes()` para evitar solapamiento
- `.env.example` actualizado con `CC_FECHA_DESDE`, `RETENCION_REPORTES_DIAS`, `RETENCION_LOGS_DIAS`
- **Prueba end-to-end exitosa** `python main.py` (exit code 0): 4 archivos descargados correctamente
  - Listado Detallado de Órdenes de Pago: 1280 filas, 11 cols
  - Ordenes de Pago: 768 filas, 52 cols
  - Cuenta Corriente (01/04→20/04): 1694 filas, 11 cols
  - Obras (Todas): 572 filas, 14 cols
- Fix selector empresa: `dispatchEvent(new Event('change', {bubbles:true}))` sobre `#bdDropdown` para que el JS de SetBase se dispare (sin esto había que seleccionarla a mano)
- **Cierre de jornada**: black 31 archivos OK | flake8 0 errores | mypy 0 errores | pytest 45/45 passed

### 2026-04-15

- **Inicio de jornada**: QA diario completo (black + flake8 + mypy + pytest)
- black reformateó `src/utils/vpn_check.py` (1 archivo); resto sin cambios
- flake8: 0 errores | mypy: 0 errores en 22 archivos | pytest: 36/36 passed
- Fix `.gitignore`: agregados `.mypy_cache/` y `.pytest_cache/` que faltaban
- Fix `scripts/ejecutar_diario.ps1`: eliminado bloque de ping VPN redundante (tarea pendiente completada)
- `src/reportes/generador.py` y `src/reglas_negocio/reglas.py`: pendientes de lógica real (sin cambios)

### 2026-04-14

- **Inicio de jornada**: análisis de ramas remotas (`qa/onboarding-pipeline`, `copilot/download-ejection-reports`)
- Merge `qa/onboarding-pipeline` → `main`: VPN check, QA tooling
  (black/flake8/mypy), smoke tests, `scripts/debug_login.py`
- Merge `copilot/download-ejection-reports` → `main`: módulo ETL
  completo (`src/etl/`), `src/reglas_negocio/`, 3 archivos de tests.
  Conflictos resueltos en `README.md` y `requirements.txt`
- QA sobre módulos del agente: black reformateó 10 archivos, flake8/mypy a 0 errores, 36/36 tests OK
- Fix colisión de configs: `src/etl/config.py` alineado a rutas del
  proyecto (`output/reportes/`), eliminados directorios espurios `data/` y `reportes/`
- Integración ETL en `main.py` como paso 4/4 (después del scraping)
- `.env.example` completado con vars del ETL y VPN
- VPN reescrita: WireGuard/Linux → FortiClient IPSec/Windows (`FortiClientConsole.exe`, credenciales en `.env`)
- Credenciales VPN cargadas en `.env` local
