# Procedimiento A — Alta de Nuevo Reporte ProntoNet

> Formulario para usuario no tecnico:
> [docs/formulario_alta_reporte_prontonet.md](formulario_alta_reporte_prontonet.md)

> Estado funcional: aprobado por el usuario (2026-05-12).
> Validacion empirica en curso con usuario final.

> **Para quién es esto:** Cualquier usuario que necesite solicitar la
> automatización de un reporte nuevo de ProntoNet. No se requieren
> conocimientos técnicos. Solo hay que responder las preguntas de
> la Sección 2 mirando el sistema.
>
> **Quién lo implementa:** El desarrollador (o Copilot con acceso al repo)
> usa el formulario completado para escribir el código sin necesidad de
> acceder a ProntoNet.

---

## Sección 1 — Requisitos previos

Antes de completar el formulario, confirmar:

- [ ] El reporte existe en ProntoNet y es accesible con tu usuario.
- [ ] La VPN "VPN POSE IP SEC" está conectada.
- [ ] Podés descargarlo manualmente (haciendo clic en el botón de Excel).
- [ ] Sabés el nombre que querés darle al archivo descargado.

---

## Sección 2 — Formulario de relevamiento

Completar una fila por reporte a dar de alta.
Si no sabés una respuesta, escribir "no sé" — el desarrollador lo
investiga.

### 2.1 Identificación del reporte

| Campo | Tu respuesta |
|---|---|
| Nombre del reporte (como aparece en el menú) | |
| ¿En qué menú o sección está? (ej: "Consultas > Proveedores") | |
| ¿Para qué sirve? (una línea de descripción) | |
| Nombre que querés darle al archivo descargado (ej: `Gastos Mensuales - Pronto.xlsx`) | |

### 2.2 Cómo llegar al reporte

| Pregunta | Tu respuesta |
|---|---|
| ¿Podés copiar la URL de la barra del navegador cuando estás en ese reporte? | |
| ¿La página carga los datos automáticamente, o hay que hacer clic en un botón "Actualizar" / "Buscar" / "Consultar"? | |

### 2.3 Filtros de la página

Marcar con **X** todo lo que veas en la pantalla del reporte:

| ¿Qué ves en la página? | Presente (X) | Detalle / nombre exacto |
|---|---|---|
| Campo "Desde" y "Hasta" (rango de fechas) | | |
| Dropdown o lista desplegable (ej: "Estado", "Tipo") | | ¿Qué opciones tiene? |
| Checkboxes (casillas de verificación, ej: "Pendiente", "Todo") | | ¿Cómo se llaman? |
| Campo de texto para buscar o filtrar | | |
| Ningún filtro — los datos aparecen directamente | | |

### 2.4 Exportación

| Pregunta | Tu respuesta |
|---|---|
| ¿Hay un botón de Excel en la página? (puede decir "Excel", tener ícono de hoja, etc.) | |
| ¿Hay un selector de cantidad de filas? (ej: "Mostrar 10 / 25 / Todos") | |
| Cuando descargás el archivo a mano, ¿cómo se llama el archivo que aparece en Descargas? | |
| ¿El archivo tiene encabezados en la primera fila, o la primera fila está vacía/tiene otro contenido? | |

### 2.5 Frecuencia y alcance

| Pregunta | Tu respuesta |
|---|---|
| ¿Este reporte debe descargarse todos los días? ¿O solo en ciertos períodos? | |
| ¿Necesita un rango de fechas fijo (ej: desde el 01/04/2026) o siempre el día de hoy? | |
| ¿Querés descargar solo registros "activos", o todos (activos + inactivos)? | |

---

## Sección 3 — Capturas de pantalla recomendadas

Si podés, adjuntar las siguientes capturas para acelerar la implementación:

1. **Vista general del reporte** — toda la página antes de hacer clic en nada.
2. **Filtros aplicados** — con los valores que querés que use la automatización.
3. **Tabla con datos** — con el selector "Todos" seleccionado (si existe).
4. **Nombre del archivo descargado** — la barra de descargas del navegador.

---

## Sección 4 — Referencia técnica (solo para el desarrollador)

Una vez recibido el formulario, el desarrollador aplica el patrón de arquitectura **Registry Reportes** (no hay recuento ciego, todo es explícito).

### Paso 1: Registrar el reporte en el Registry

En `config/registry_reportes.py`, agregar un nuevo bloque a `REGISTRY_REPORTES`:

```python
    "nuevo_reporte": {
        "archivo_esperado": "El Archivo Descargado - Pronto.xlsx",
        "activo": True,
        "tabla_bd_destino": "compensaciones.tabla_destino",
        "funcion_scraper": "descargar_nuevo_reporte",
        "columnas_esperadas": ["Columna 1", "Columna 2"],
    },
```

### Paso 2: Implementar la extracción (Árbol de decisión en `scraper.py`)

Dependiendo de los filtros marcados en el formulario:

**A. Reporte Simple (Sin filtros, exportación directa)**
Agregar la URL al diccionario `URLS_ESTANDAR` dentro de la función `descargar_todos_los_reportes()` usando el mismo alias que en el registry:

```python
    URLS_ESTANDAR = {
        # ... otros ...
        "descargar_nuevo_reporte": "http://10.2.1.81/URL/Fija/Del/Reporte",
    }
```
Esto utilizará la función genérica `_descargar_archivo()`.

**B. Reporte Especial (Con fechas, dropdowns, DataTables)**
Crear una función privada e invocarla en el clasificador iterativo de `descargar_todos_los_reportes()`:

```python
def _descargar_nuevo_reporte(page: Page, nombre_destino: str) -> Path:
    page.goto(f"{APP_URL}/URL/Del/Reporte")
    page.wait_for_load_state("networkidle")
    
    # Manejar filtros, dropdowns, checkboxes
    # page.select_option("#idDelDropdown", "valor")
    
    # Exportar y descargar
    with page.expect_download() as dl:
        page.click("button.buttons-excel")
    
    ruta_destino = RUTA_DESCARGA / nombre_destino
    dl.value.save_as(ruta_destino)
    return ruta_destino
```
Añadir el bloque `elif` al bucle de descargas en `descargar_todos_los_reportes()`:
```python
    elif funcion == "descargar_nuevo_reporte":
        ruta = _descargar_nuevo_reporte(page, nombre)
```

### Paso 3: Enrutador de procesamiento

En `src/procesamiento/enriquecimiento.py`, registrar formalmente la función de procesamiento en el diccionario `procesadores` en función del ID del Registry:

```python
    procesadores = {
        # El nombre del archivo se recupera del registry
        REGISTRY_REPORTES["nuevo_reporte"]["archivo_esperado"]: procesar_nuevo_reporte,
    }
```

### Checklist de validación post-implementación

- [ ] Nueva entrada configurada en `REGISTRY_REPORTES`.
- [ ] Función (o URL estándar) añadida correctamente en `scraper.py`.
- [ ] Función de procesamiento asociada en `procesadores` (`enriquecimiento.py`).
- [ ] El archivo tiene las columnas mínimas registradas en `columnas_esperadas`.
- [ ] `python3 main.py --solo-procesar` ejecuta el ciclo sin errores para los reportes mockeados en `input_raw/`.

---

## Sección 5 — Reportes actualmente configurados (vía Registry)

El sistema ahora está desacoplado y gobernado por `config/registry_reportes.py`. Los tipos actualmente soportados en `scraper.py` son:

| Alias (`funcion_scraper`) | Tipo según scraper.py | Mecanismo |
|---|---|---|
| `descargar_detallado_ordenes_pago` | Simple | `URLS_ESTANDAR` estático |
| `descargar_ordenes_pago` | Simple | `URLS_ESTANDAR` estático |
| `descargar_cuenta_corriente` | Especial | `_descargar_cuenta_corriente()` |
| `descargar_obras` | Especial | `_descargar_obras()` |
| `descargar_gastos` | Simple | `URLS_ESTANDAR` estático |

---

*Última actualización: 2026-05-12*
