# Mapa de Auditoría — GestionComp: Reportes
**Generado:** 2026-05-12  
**Propósito:** Procedimiento para dar de alta nuevos reportes, mapa de archivos
involucrados y estado del proceso programado (21:00 hs).

---

## 1. Estado del Proceso Nocturno (21:00 hs)

| Campo | Valor |
|-------|-------|
| Tarea programada | `Compensaciones_Diario` (Programador de Tareas Windows) |
| Script ejecutado | `C:\Dev\GestionComp\scripts\ejecutar_diario.ps1` |
| Python invocado | `%LOCALAPPDATA%\Programs\Python\Python313\python.exe main.py` |
| Última ejecución | 11/05/2026 21:00:01 |
| Resultado | **FALLÓ** — exit code 1 |
| Próxima ejecución | 12/05/2026 21:00:00 |

### 1.1 Causa del fallo (11/05/2026)

**Error:** `AttributeError: Can only use .str accessor with string values, not boolean`

**Ubicación:** `src/procesamiento/enriquecimiento.py`, función `procesar_obras()`, línea ~238.

**Causa raíz:** `procesar_obras()` convierte la columna `Activa?` a `bool` en el
paso de normalización de valores, y luego el loop genérico `df[col].str.strip()`
sobre columnas object intenta operar sobre esa columna ya convertida.
La estructura del Excel cambió: el reporte ahora tiene **12 columnas** (antes 14)
y columnas como `Numero`, `Descripcion`, `Unidad operativa` ya no están presentes.

**Consecuencia:** El proceso se interrumpe en el Paso 2/4 (enriquecimiento). 
Los informes de dirección NO se generan desde el 05/05/2026.

**Archivos que SÍ se descargan (descarga exitosa cada noche):**
- `input_raw/Listado Detallado de Órdenes de Pago - Pronto.xlsx`
- `input_raw/Ordenes de Pago - Pronto.xlsx`
- `input_raw/Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx`
- `input_raw/Obras - Pronto Hist.xlsx`

---

## 2. Arquitectura del Flujo — Visión General

```
[ProntoNet — sistema web]
        │
        │  Playwright (scraper.py)
        ▼
input_raw/               ← Excel descargados (sobreescriben el anterior)
        │
        │  enriquecimiento.py
        ▼
DataFrames enriquecidos  ← en memoria
        │
        │  generador.py
        ├──────────────────► output/informes_direccion/Informe_Direccion_YYYYMMDD.xlsx
        └──────────────────► output/reportes/Reporte_Procesado_YYYYMMDD.xlsx
                                          (+ logs/run_YYYYMMDD.log)
```

---

## 3. Mapa de Archivos por Función

### 3.1 Archivos de configuración

| Archivo | Rol |
|---------|-----|
| `.env` | Credenciales, URLs, rutas, parámetros de retención |
| `.env.example` | Plantilla sin valores secretos (versionada) |
| `config/settings.py` | Lee `.env`, define rutas base y constantes globales |

**Variables clave en `.env`:**

```
APP_URL          → URL de login del sistema (http://10.2.1.81/Account/Login)
APP_USUARIO      → Usuario de ProntoNet
APP_PASSWORD     → Contraseña de ProntoNet
GASTOS_URL       → URL del reporte Gastos.xlsx (vacío = no se descarga)
CC_FECHA_DESDE   → Fecha de inicio para Cuenta Corriente (DD/MM/YYYY)
MODO_NAVEGADOR   → visible | headless
RUTA_DESCARGA    → Ruta destino de descarga (vacío = input_raw/ del proyecto)
```

### 3.2 Archivos de descarga

| Archivo | Qué hace |
|---------|----------|
| `src/descarga/scraper.py` | Orquestador Playwright: login + navegación + descarga |
| `src/descarga/__init__.py` | Módulo Python |

**Funciones internas del scraper:**

| Función | Reporte | Tipo de flujo |
|---------|---------|---------------|
| `_descargar_archivo()` | Genérico (Listado Órdenes, Órdenes de Pago) | Navega URL → botón Actualizar → All → Excel |
| `_descargar_cuenta_corriente()` | Cuenta Corriente CONSTRUYA | Flujo especial: checkboxes + rango de fecha |
| `_descargar_obras()` | Obras - Pronto Hist | Flujo especial: dropdown `#Activas = "T"` |
| `descargar_todos_los_reportes()` | Todos | Abre browser, login, llama a cada función |

### 3.3 Archivos de procesamiento

| Archivo | Qué hace |
|---------|----------|
| `src/procesamiento/enriquecimiento.py` | Lee input_raw/, aplica transformaciones por tipo de reporte |
| `src/reportes/generador.py` | Genera informe de dirección y reporte resumen en Excel |

**Funciones de transformación en `enriquecimiento.py`:**

| Función | Archivo fuente (clave de match) | Columnas clave |
|---------|--------------------------------|----------------|
| `procesar_cuenta_corriente()` | `"cuenta corriente"` en nombre | Imp.orig., Saldo Comp., SaldoTrs, Fecha, Fecha vto., Fecha cmp. |
| `procesar_listado_ordenes()` | `"listado"` + `"orden"` en nombre | Fecha Orden Pago, Importe, Centro de Costos |
| `procesar_ordenes_pago()` | `"orden"` en nombre (sin "listado") | Numero, Fecha Pago, Efectivo, Descuentos, Valores |
| `procesar_obras()` | `"obra"` en nombre | Numero, Descripcion, Activa?, Valor obra |
| `procesar_gastos()` | `"gasto"` en nombre | Fecha (TODO: columnas reales pendientes) |
| *(sin match)* | cualquier otro nombre | Se pasa sin transformación + warning |

**Lógica de routing en `enriquecer_datos()`:**

```python
# La clave de routing es el NOMBRE DEL ARCHIVO (sin extensión), en minúsculas
if "cuenta corriente" in clave_lower   → procesar_cuenta_corriente()
elif "gasto" in clave_lower            → procesar_gastos()
elif "listado" in clave_lower and "orden*" → procesar_listado_ordenes()
elif "orden*" in clave_lower           → procesar_ordenes_pago()
elif "obra" in clave_lower             → procesar_obras()
else                                   → sin transformación (warning)
```

**El nombre del archivo Excel descargado determina la transformación.**

### 3.4 Archivos de entrada/salida

| Ruta | Contenido | Política |
|------|-----------|----------|
| `input_raw/*.xlsx` | Archivos descargados de ProntoNet | Sobreescritos cada noche |
| `output/informes_direccion/Informe_Direccion_YYYYMMDD.xlsx` | Informe de dirección consolidado | Retención 90 días |
| `output/reportes/Reporte_Procesado_YYYYMMDD.xlsx` | Reporte resumen con todas las hojas | Retención 90 días |
| `logs/run_YYYYMMDD.log` | Log completo de ejecución (PowerShell + Python) | Retención 30 días |
| `logs/compensaciones.log` | Log rotativo del proceso Python (loguru) | Rotación automática |

---

## 4. Procedimiento — Alta de un Nuevo Reporte

Para agregar un reporte que no existe actualmente en el sistema, se deben
tocar **4 archivos en orden**:

### Paso 1 — `src/descarga/scraper.py`

**¿Qué datos necesito del sistema web antes de codificar?**

| Dato a relevar | Dónde buscarlo |
|---------------|----------------|
| URL del reporte | Barra de navegación del browser al acceder al reporte |
| ¿Tiene `#botonActualizar`? | Ver el HTML de la página (F12 → Elements) |
| ¿Tiene filtros de fecha? | ¿Aparece un campo `#filtroFecha` o similar? |
| ¿Tiene checkboxes de estado? | ¿Hay `#Pendiente_chk`, `#Todo_chk` u otros? |
| ¿Tiene dropdown de estado? | ¿Hay un `<select>` con opciones como Activas/Todas? |
| ¿El Excel se genera con DataTables? | ¿Aparece el botón `button.buttons-excel`? |
| Nombre exacto del archivo descargado | Inspeccionar la descarga del navegador |

**Caso A — Reporte simple (navegar y exportar sin filtros):**

```python
# En descargar_todos_los_reportes(), agregar en el dict REPORTES:
REPORTES = [
    ...
    (
        "http://10.2.1.81/MiModulo/ReporteNuevo",
        "Mi Nuevo Reporte - Pronto.xlsx",
    ),
]
```
La función `_descargar_archivo()` genérica lo maneja.

**Caso B — Reporte con filtros propios (flujo especial):**

```python
# Crear una función dedicada (como _descargar_cuenta_corriente):
def _descargar_mi_nuevo_reporte(
    page: Page, nombre_destino: str
) -> Path:
    """Descarga Mi Nuevo Reporte con filtros específicos."""
    URL = "http://10.2.1.81/MiModulo/Reporte"
    # ... lógica de filtros
    # Al final, mismo patrón:
    with page.expect_download(timeout=TIMEOUT_MS) as dl_info:
        page.click("button.buttons-excel", force=True)
    download: Download = dl_info.value
    destino = RUTA_DESCARGA / nombre_destino
    download.save_as(destino)
    return destino

# Y en descargar_todos_los_reportes(), llamar fuera del loop genérico:
ruta_nuevo = _descargar_mi_nuevo_reporte(
    page, nombre_destino="Mi Nuevo Reporte - Pronto.xlsx"
)
archivos_descargados.append(ruta_nuevo)
```

### Paso 2 — `config/settings.py`

Agregar el nombre del archivo a la lista `ARCHIVOS_ESPERADOS`:

```python
ARCHIVOS_ESPERADOS = [
    "Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx",
    "Gastos.xlsx",
    "Listado Detallado de Órdenes de Pago - Pronto.xlsx",
    "Obras - Pronto Hist.xlsx",
    "Ordenes de Pago - Pronto.xlsx",
    "Mi Nuevo Reporte - Pronto.xlsx",   # ← AGREGAR AQUÍ
]
```

### Paso 3 — `src/procesamiento/enriquecimiento.py`

**Primero:** relevar las columnas reales del archivo descargado:

```python
# Script temporal para inspeccionar (ejecutar una sola vez):
import pandas as pd
df = pd.read_excel("input_raw/Mi Nuevo Reporte - Pronto.xlsx",
                   engine="openpyxl", header=1)
df = df.dropna(axis=1, how="all")
print(df.columns.tolist())
print(df.dtypes)
print(df.head(3))
```

**Luego:** crear la función de procesamiento con las columnas relevadas:

```python
def procesar_mi_nuevo_reporte(df: pd.DataFrame) -> pd.DataFrame:
    """
    Columnas reales (ProntoNet): Col1, Col2, Fecha, Importe ...
    """
    df = df.copy()
    # Fechas
    for col in ["Fecha"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    # Numéricos
    for col in ["Importe"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            )
    # IMPORTANTE: aplicar .str.strip() SOLO sobre columnas object
    # (no sobre bool, datetime, float — ese fue el bug de procesar_obras)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df
```

**Luego:** agregar el routing en `enriquecer_datos()`:

```python
# El match se hace sobre el nombre del archivo SIN extensión, en minúsculas.
# Usar palabras clave únicas que aparezcan en el nombre del archivo.
elif "nuevo reporte" in clave_lower:
    resultado["mi_nuevo_reporte"] = procesar_mi_nuevo_reporte(df)
```

> **Regla clave:** el routing usa `archivo.stem.lower()` como clave.
> El nombre del archivo descargado (`nombre_destino` en el scraper)
> es lo que determina qué función de transformación se aplica.

### Paso 4 — `src/reportes/generador.py` (si requiere sección en el informe)

Si el nuevo reporte debe aparecer en el `Informe_Direccion_YYYYMMDD.xlsx`,
agregar una hoja en `generar_informe_diario()`:

```python
# Los datos llegan como dict: datos["mi_nuevo_reporte"] = DataFrame
if "mi_nuevo_reporte" in datos:
    df_nuevo = datos["mi_nuevo_reporte"]
    df_nuevo.to_excel(
        writer, sheet_name="Mi Nuevo Reporte", index=False
    )
```

Y en `generar_resumen_excel()` si también debe aparecer en el resumen.

---

## 5. Checklista — Alta de Nuevo Reporte

```
[ ] 1. Acceder manualmente al reporte en ProntoNet y relevar:
        - URL exacta
        - Nombre del archivo descargado
        - Columnas presentes (F12 o descarga manual + inspección)
        - Filtros/checkboxes que requiere

[ ] 2. scraper.py → agregar entrada en REPORTES[] o función dedicada

[ ] 3. settings.py → agregar nombre a ARCHIVOS_ESPERADOS

[ ] 4. enriquecimiento.py → crear procesar_X() con columnas reales
        - CUIDADO: aplicar .str.strip() solo sobre select_dtypes("object")
        - CUIDADO: convertir bool DESPUÉS del loop de .str.strip()

[ ] 5. generador.py → agregar hoja si es necesaria en el informe

[ ] 6. Ejecutar prueba manual: python main.py --solo-procesar
        (asume que ya hay un archivo en input_raw/)

[ ] 7. QA: cd C:\Dev\.gemini && python task_manager.py (o crew --qa)
```

---

## 6. Bug Activo — procesar_obras() falla desde 11/05/2026

**Síntoma:** El proceso falla cada noche desde el 11/05. Los informes de
dirección **NO se están generando** (último generado: 05/05/2026).

**Error exacto:**
```
AttributeError: Can only use .str accessor with string values, not boolean.
File: src/procesamiento/enriquecimiento.py, procesar_obras(), línea ~238
```

**Causa:** El loop `for col in df.select_dtypes(include="object").columns:`
se ejecuta *después* de que `Activa?` ya fue convertida a `bool`.
Pandas en la versión actual puede inferir esta columna como `bool` al leer
el Excel antes del loop, dejándola como no-object pero siendo luego
referenciada por el `.str.strip()`.

**Fix requerido (tarea pendiente — Sauron diseña):**  
Mover la conversión de `Activa?` *después* del loop de `.str.strip()`, o
aplicar el loop solo sobre columnas que sigan siendo `object`:

```python
# Patrón correcto (ya implementado en procesar_ordenes_pago y otros):
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].str.strip()
# Conversiones de tipo DESPUÉS del strip:
if "Activa?" in df.columns:
    df["Activa?"] = df["Activa?"].astype(str).str.strip().str.lower().map(...)
```

**Adicionalmente:** El reporte `Obras - Pronto Hist.xlsx` cambió su schema:
columnas `Numero`, `Descripcion`, `Unidad operativa` ya no están presentes
(pasó de 14 a 12 columnas). `actualizar_obras_gerencias.py` registra error
`Obras - Pronto Hist.xlsx sin columnas requeridas`.

---

## 7. Reportes Actualmente Configurados

| # | Nombre en input_raw/ | URL ProntoNet | Función scraper | Función ETL | Estado |
|---|---------------------|---------------|-----------------|-------------|--------|
| 1 | `Listado Detallado de Órdenes de Pago - Pronto.xlsx` | `/Consulta/ProveedoresListadoOrdenesPagoDetallado3` | `_descargar_archivo()` | `procesar_listado_ordenes()` | ✅ OK |
| 2 | `Ordenes de Pago - Pronto.xlsx` | `/OrdenPago/` | `_descargar_archivo()` | `procesar_ordenes_pago()` | ✅ OK |
| 3 | `Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx` | `/CuentaCorriente/AcreedoresPorTransacciones?IdProveedor=43292` | `_descargar_cuenta_corriente()` | `procesar_cuenta_corriente()` | ✅ OK |
| 4 | `Obras - Pronto Hist.xlsx` | `/Obra/Index` | `_descargar_obras()` | `procesar_obras()` | ❌ BUG |
| 5 | `Gastos.xlsx` | `GASTOS_URL` (`.env`, vacío) | `_descargar_archivo()` | `procesar_gastos()` | ⚠️ Sin URL |

---

## 8. Referencias de Archivos

| Archivo | Ruta |
|---------|------|
| Punto de entrada | [main.py](../main.py) |
| Scraper Playwright | [src/descarga/scraper.py](../src/descarga/scraper.py) |
| Configuración global | [config/settings.py](../config/settings.py) |
| Variables de entorno | [.env.example](../.env.example) |
| Enriquecimiento | [src/procesamiento/enriquecimiento.py](../src/procesamiento/enriquecimiento.py) |
| Generador de informes | [src/reportes/generador.py](../src/reportes/generador.py) |
| Script tarea programada | [scripts/ejecutar_diario.ps1](../scripts/ejecutar_diario.ps1) |
| Tareas pendientes | [TASKS.md](../TASKS.md) |
