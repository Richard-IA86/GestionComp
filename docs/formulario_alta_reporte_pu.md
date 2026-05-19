# Formulario de Alta de Reporte ProntoNet

> **Estado:** Completado para Prueba de Usuario
> **Referencia:** Débitos y Créditos Bancarios

---

## 1) Datos generales

- **Fecha de solicitud:** 12 de mayo de 2026
- **Solicitante:** Ricardo Rivarola
- **Area:** Presidencia / CEO
- **Prioridad:** Alta
- **Fecha deseada de implementacion:** Inmediata

---

## 2) Identificacion del reporte

- **Nombre del reporte:** Débitos y Créditos Bancarios
- **Menu / seccion donde esta:** CAJA Y BANCOS
- **Para que sirve:** Control de movimientos bancarios para conciliación y auditoría de obras.
- **Nombre deseado del archivo descargado:** Reporte_Debitos_Creditos_Bancarios.xlsx

---

## 3) Como llegar al reporte

- **URL exacta de la pantalla del reporte:** <http://10.2.1.81/Valor/>
- **La tabla carga sola o requiere boton:** Requiere botón para aplicar el filtro de fechas.
- **Si requiere boton, nombre exacto del boton:** Icono de Lupa (azul).

---

## 4) Filtros visibles en pantalla

- [X] **Rango de fechas (Desde/Hasta)**
  - **Nombre exacto del campo:** Selector de rango (Datepicker).
  - **Valor esperado por defecto:** Mes actual (ej: 01/05/2026 - 12/05/2026).
- [X] **Campo de texto para buscar**
  - **Nombre exacto del campo:** "Buscar".
  - **Valor por defecto:** Vacío.

---

## 5) Exportacion

- **Hay boton Excel visible:** Si.
- **Nombre del boton o selector de exportacion:** Botón "Excel" en la barra gris.
- **Hay selector de cantidad de filas (10/25/All):** Si.
- **Si existe, debe usarse All/Todos:** Si (Acción: Seleccionar "All" en el dropdown antes de exportar).
- **Nombre real del archivo que baja:** Debitos y Créditos Bancarios.xlsx
- **Encabezados del Excel estan en:** Fila 1.

---

## 6) Frecuencia y alcance

- **Frecuencia de descarga:** Semanal / A demanda.
- **Ventana temporal que debe aplicar:** Mes en curso.
- **Debe descargar:** Todo.

---

## 7) Validacion funcional (usuario)

1. El archivo debe tener extensión .xlsx.
2. Debe contener movimientos de la cuenta seleccionada.
3. El total de filas debe coincidir con lo que muestra la web tras seleccionar "All".

---

## 12) Feedback de la Prueba de Usuario (Interno)

- **Observación técnica:** Es crítico que el script espere a que la grilla se refresque completamente tras cambiar el selector a "All" antes de intentar el clic en "Excel".
- **Ajuste:** Se validó que el botón Excel es un elemento directo del DOM y no requiere navegación adicional por menús.
