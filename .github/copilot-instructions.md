# Principio Operativo #1 — NO NEGOCIABLE

> **"Diagnósticos cortos, claros, breves y efectivos."**

- Ver el error → identificar archivo/línea → fix → verificar. Una pasada.
- Si el mismo análisis se repite: parar, cambiar enfoque.
- **"Tenemos que salir de la rotonda."**

---

# Instrucciones Copilot — gestion_comp

## Propósito del Proyecto

Automatización de descarga, procesamiento y generación de informes
de compensaciones POSE usando Playwright + pandas + xlsxwriter.

## Protocolo de Scripts Temporales — Obligatorio

Cuando crees un script Python (.py) u otro archivo para un fin
puntual (diagnóstico, análisis, escaneo, verificación, depuración,
benchmark, extracción de datos), aplica este ciclo:

### Opción A — fuera del proyecto (PREFERIDA)

1. Crea el script en `/tmp/` → `python /tmp/_temp_check.py`
2. Ejecuta y procesa la salida.
3. El archivo desaparece solo al cerrar sesión.

### Opción B — dentro del proyecto (solo si es estrictamente necesario)

1. Usa el prefijo obligatorio `_temp_` → `_temp_analisis.py`
2. Ejecuta: `python _temp_analisis.py`
3. Elimínalo inmediatamente: `rm _temp_analisis.py`
4. NUNCA hagas `git add` sobre archivos `_temp_*.py`.

### Patrones de nombre = script efímero (aplica el protocolo)

`debug_*`, `diagnostico_*`, `analisis_*`, `analizar_*`,
`analyze_*`, `scan_*`, `verificar_*`, `prueba_*`,
`test_fix_*`, `benchmark_*`, `extract_*` (cuando no es módulo).

## Estándares de Código Python — Obligatorios

El pipeline QA usa **black** + **flake8** + **mypy**
(`max-line-length = 79`, `extend-ignore = E203, W503`).
Todo código generado debe pasar sin errores ni advertencias.

### Longitud de línea (E501) — MÁX. 79 caracteres

- Llamadas largas → paréntesis implícitos (NO usar `\`):

  ```python
  resultado = funcion_larga(
      arg1, arg2, arg3,
  )
  ```

- Docstrings y comentarios → cortar en la palabra antes de la col 79.
- f-strings y literales largas → concatenación implícita en paréntesis:

  ```python
  mensaje = (
      f"Primera parte {var}"
      " segunda parte fija"
  )
  ```

- URLs, user-agent strings, JS inline → `# noqa: E501`
  (semántica destruida si se cortan).
- `# noqa: E501` SOLO cuando el corte destruye semántica.
- NUNCA añadir `# noqa: E501` a comentarios o docstrings — cortarlos.

### f-strings vacíos (F541)

- NUNCA: `f"texto sin llaves"` → usar: `"texto sin llaves"`.

### Variables sin usar (F841)

- NUNCA asignar una variable que no se lee después.
- Resultados descartados intencionalmente → prefijo `_`:
  `_ok = funcion_con_efectos()`

### Tipado mypy — anotaciones correctas

- Dicts con valores mixtos → `resultado: dict[str, Any]`
  (importar siempre `from typing import Any`).
- `dict.get("k")` → anotar la variable destino como `T | None`.
- `sys.stdout.reconfigure(...)` → añadir `# type: ignore[union-attr]`.

### Imports y nombres de módulos

- Módulos Python siempre en `snake_case`.
- Imports no usados → eliminar.

---

## Protocolo de Jornada — Obligatorio

Copilot actualiza `config/estado_proyecto.json` ÚNICAMENTE ante los
triggers explícitos del desarrollador. No en ningún otro momento.

### Trigger: "inicio de jornada"

1. Leer `config/estado_proyecto.json` → sección `jornada.fin`
   (archivos locales — estado al cierre de ayer).
2. Ejecutar `git pull` para bajar novedades del remoto.
3. Recién entonces reportar al desarrollador:
   - `tareas_pendientes_manana` (lo que quedó pendiente ayer)
   - `notas_qa` (observación del cierre anterior)
   - `estado_pipeline` (VERDE / AMARILLO / ROJO)
   - Commits nuevos descargados (si los hay)
4. **No modificar el archivo en este trigger.**

### Trigger: "fin de jornada"

Actualizar `config/estado_proyecto.json` — sección `jornada`:

```json
"jornada": {
  "fin": {
    "fecha": "YYYY-MM-DD",
    "tareas_completadas": ["lo realizado hoy"],
    "tareas_pendientes_manana": ["lo que queda"],
    "notas_qa": "observación para El Ojo de Sauron",
    "estado_pipeline": "VERDE | AMARILLO | ROJO"
  }
}
```

También actualizar (retrocompatibilidad):

- `desarrollo_local.fecha_actualizacion` → fecha de hoy
- `desarrollo_local.punto_de_partida_manana` → resumen en 1 línea

Luego:

```bash
git add config/estado_proyecto.json
git commit -m "chore(jornada): cierre YYYY-MM-DD"
git push
```
