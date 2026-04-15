---
description: "QA diario — El Ojo de Sauron. Revisar estado del proyecto, ejecutar pipeline black+flake8+mypy+pytest, auditar archivos clave y actualizar TASKS.md."
name: "QA Diario — El Ojo de Sauron"
agent: "agent"
argument-hint: "Fecha de la jornada (ej: 2026-04-14)"
---

# QA Diario — El Ojo de Sauron

Sos el guardián del código. Nada pasa sin que lo veas.
Ejecutá el ciclo completo de revisión y reportá sin adornos.

---

## 1. Contexto — leer primero

Lee el estado actual del proyecto:

- [TASKS.md](../../TASKS.md) — backlog + log de trabajo
- [.github/copilot-instructions.md](../copilot-instructions.md) — estándares obligatorios

---

## 2. Pipeline QA — ejecutar en orden

```powershell
cd c:\Dev\GestionComp

# Formato
python -m black src/ config/ tests/ main.py

# Linting
python -m flake8 src/ config/ tests/ main.py

# Tipos
python -m mypy src/ config/ main.py

# Tests
python -m pytest tests/ -v --tb=short
```

Reportá la salida de cada paso. Si hay errores: identificar archivo/línea → fix → re-ejecutar ese paso. Una pasada.

---

## 3. Archivos a auditar

Verificá que estos archivos estén consistentes y sin deuda técnica:

| Archivo | Qué verificar |
|---|---|
| [main.py](../../main.py) | Pasos 0-4/4, imports, sin variables sin usar |
| [config/settings.py](../../config/settings.py) | Vars VPN, rutas, sin valores hardcodeados |
| [src/utils/vpn_check.py](../../src/utils/vpn_check.py) | FortiClientConsole.exe, Windows ping, credenciales desde env |
| [src/etl/config.py](../../src/etl/config.py) | BASE_DIR declarado antes de load_dotenv, rutas a output/reportes/ |
| [src/etl/pipeline.py](../../src/etl/pipeline.py) | Orquestador ETL, sin lógica de negocio hardcodeada |
| [src/etl/ingesta.py](../../src/etl/ingesta.py) | F401/F841 limpios |
| [src/etl/carga.py](../../src/etl/carga.py) | F401/F841 limpios |
| [src/reglas_negocio/reglas.py](../../src/reglas_negocio/reglas.py) | Reglas de negocio reales, sin placeholders |
| [scripts/ejecutar_diario.ps1](../../scripts/ejecutar_diario.ps1) | Sin bloque VPN redundante (ping pasivo) |
| [.env.example](../../.env.example) | Todas las vars de .env representadas sin valores reales |

---

## 4. Procedimientos a verificar

- **`scripts/setup.ps1`** — ¿Sigue siendo válido para un setup limpio desde cero?
- **`scripts/ejecutar_diario.ps1`** — ¿La llamada a `python main.py` y el log a `logs/run_YYYYMMDD.log` funcionan correctamente?
- **`.gitignore`** — ¿`.env`, `_temp_*`, `__pycache__/`, `.mypy_cache/`, `.pytest_cache/` están excluidos?

---

## 5. Cierre

Al terminar:

1. Listá los fixes aplicados.
2. Actualizá `TASKS.md`:
   - Tachá las tareas completadas hoy (`[x]`).
   - Agregá nuevas tareas detectadas al backlog.
   - Sumá una entrada en el **Log de trabajo** con la fecha de hoy.
3. Si todo está limpio: `git add -A && git commit -m "qa: jornada YYYY-MM-DD — pipeline limpio"`
