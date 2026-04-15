# TASKS — Compensaciones POSE

## Backlog

### En curso
- [ ] Prueba end-to-end del flujo completo con VPN FortiClient activa
- [ ] Validar paso 4/4 ETL con archivos reales de `input_raw/`

### Pendiente — Infraestructura
- [ ] Configurar tarea programada en Windows (Programador de Tareas) para `ejecutar_diario.ps1`
- [ ] Actualizar `scripts/ejecutar_diario.ps1`: eliminar bloque de ping VPN redundante (lo maneja `main.py` paso 0/4)
- [ ] Definir política de retención de archivos en `output/reportes/` y `logs/`

### Pendiente — Funcionalidad
- [ ] Revisar selectores Playwright en `scraper.py` con el sistema real (pueden haber cambiado)
- [ ] Completar lógica de `src/procesamiento/enriquecimiento.py` con reglas de negocio reales
- [ ] Completar lógica de `src/reportes/generador.py` con formato final del informe de dirección
- [ ] Definir esquema de BD destino para el ETL (`src/etl/carga.py` → `a_bd()`)

### Pendiente — QA
- [ ] Agregar tests de humo para `src/etl/` con archivos Excel de muestra
- [ ] Agregar test de integración `main.py --solo-procesar` con fixtures

### Ideas / futuro
- [ ] Notificación por email/Teams al finalizar el proceso
- [ ] Dashboard de seguimiento de errores por fecha

---

## Log de trabajo

### 2026-04-14
- **Inicio de jornada**: análisis de ramas remotas (`qa/onboarding-pipeline`, `copilot/download-ejection-reports`)
- Merge `qa/onboarding-pipeline` → `main`: VPN check, QA tooling (black/flake8/mypy), smoke tests, `scripts/debug_login.py`
- Merge `copilot/download-ejection-reports` → `main`: módulo ETL completo (`src/etl/`), `src/reglas_negocio/`, 3 archivos de tests. Conflictos resueltos en `README.md` y `requirements.txt`
- QA sobre módulos del agente: black reformateó 10 archivos, flake8/mypy a 0 errores, 36/36 tests OK
- Fix colisión de configs: `src/etl/config.py` alineado a rutas del proyecto (`output/reportes/`), eliminados directorios espurios `data/` y `reportes/`
- Integración ETL en `main.py` como paso 4/4 (después del scraping)
- `.env.example` completado con vars del ETL y VPN
- VPN reescrita: WireGuard/Linux → FortiClient IPSec/Windows (`FortiClientConsole.exe`, credenciales en `.env`)
- Credenciales VPN cargadas en `.env` local
