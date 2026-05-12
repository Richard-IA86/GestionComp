# Procedimiento A — Alta de Nuevo Reporte ProntoNet

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

Una vez recibido el formulario, el desarrollador determina el tipo de
implementación:

### Árbol de decisión

```
¿Tiene filtros especiales (fechas, checkboxes, dropdowns)?
│
├── NO → Reporte simple
│         Agregar a la lista REPORTES en scraper.py:
│         ("URL_relativa", "Nombre archivo.xlsx")
│
└── SÍ → Reporte especial
          Crear función dedicada en scraper.py:
          def _descargar_<nombre>(page, nombre_destino): ...
          Llamarla desde descargar_todos_los_reportes()
```

### Plantilla — Reporte simple

```python
# En scraper.py → lista REPORTES
REPORTES = [
    # ... existentes ...
    ("/URL/Del/Reporte", "Nombre Archivo - Pronto.xlsx"),
]
```

### Plantilla — Reporte especial con filtros

```python
def _descargar_<nombre>(
    page: Page, nombre_destino: Path
) -> None:
    """Descarga el reporte <Nombre> con filtros específicos."""
    page.goto(f"{APP_URL}/URL/Del/Reporte")
    page.wait_for_load_state("networkidle")

    # Ejemplo: dropdown de estado
    # page.select_option("#idDelDropdown", "valorDeOpcion")

    # Ejemplo: checkbox
    # page.check("#idDelCheckbox")

    # Ejemplo: rango de fechas
    # page.fill("#filtroFechaDesde", "01/04/2026")
    # page.fill("#filtroFechaHasta", fecha_hoy)

    # Botón actualizar (si existe)
    # page.click("#botonActualizar")
    # page.wait_for_load_state("networkidle")

    # Seleccionar "Todos" en DataTables
    page.select_option("select[name$='_length']", "-1")
    page.wait_for_load_state("networkidle")

    # Exportar a Excel
    with page.expect_download() as dl:
        page.click("button.buttons-excel")
    dl.value.save_as(nombre_destino)
    logger.info("Descargado: %s", nombre_destino.name)
```

### Checklist de validación post-implementación

- [ ] El archivo aparece en `input_raw/` con el nombre correcto.
- [ ] El archivo pesa más de 5 KB (no está vacío).
- [ ] Se puede abrir en Excel sin error.
- [ ] `enriquecimiento.py` lo reconoce por nombre de archivo
      (o se agregó la rama correspondiente).
- [ ] `config/settings.py` → `ARCHIVOS_ESPERADOS` actualizado.
- [ ] Se ejecutó `main.py --solo-procesar` y el pipeline completa sin error.

---

## Sección 5 — Reportes actualmente configurados

| Archivo descargado | Tipo | Función en scraper.py |
|---|---|---|
| `Listado Detallado de Órdenes de Pago - Pronto.xlsx` | Simple | `REPORTES` lista |
| `Ordenes de Pago - Pronto.xlsx` | Simple | `REPORTES` lista |
| `Cuenta Corriente Proveedores - Pronto.xlsx` | Especial | `_descargar_cuenta_corriente()` |
| `Obras - Pronto Hist.xlsx` | Especial | `_descargar_obras()` |
| `Gastos.xlsx` | Especial (opcional) | `GASTOS_URL` en `.env` |

---

*Última actualización: 2026-05-12*
