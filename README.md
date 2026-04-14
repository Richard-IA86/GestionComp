# GestionComp

Pipeline ETL para la distribución diaria de variables de un negocio.

## Descripción

Este proyecto implementa un proceso ETL (Extract, Transform, Load) completo para:

- **Ingesta (Extract)**: lectura de datos desde CSV, Excel, JSON, base de datos relacional y APIs REST.
- **Transformación (Transform)**: limpieza, normalización y aplicación de reglas de negocio (validaciones, cálculos de distribución, detección de alertas, categorización).
- **Carga (Load)**: persistencia de datos válidos en base de datos o archivos de salida; registro de rechazos en archivo de auditoría.
- **Reportes**: generación y descarga de reportes de gestión en formato Excel o CSV (resumen diario, alertas, distribución por centro de costo, reporte consolidado).

## Estructura del proyecto

```
GestionComp/
├── src/
│   ├── etl/
│   │   ├── config.py          # Configuración centralizada (variables de entorno)
│   │   ├── ingesta.py         # Módulo de Extracción
│   │   ├── transformacion.py  # Módulo de Transformación
│   │   ├── carga.py           # Módulo de Carga
│   │   ├── reportes.py        # Generación y descarga de reportes
│   │   └── pipeline.py        # Orquestador del pipeline ETL
│   └── reglas_negocio/
│       └── reglas.py          # Reglas de negocio (funciones puras y documentadas)
├── tests/
│   ├── test_ingesta.py
│   ├── test_transformacion.py
│   └── test_reportes.py
├── data/                      # Archivos de datos de entrada/salida (generado automáticamente)
├── reportes/                  # Reportes generados (generado automáticamente)
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+
- Ver `requirements.txt` para las dependencias de Python

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables (opcional; hay valores por defecto):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestion_comp
DB_USER=etl_user
DB_PASSWORD=tu_contraseña

API_REPORTES_URL=http://localhost:8080/api
API_REPORTES_TOKEN=tu_token

ETL_BATCH_SIZE=1000
ETL_FECHA_PROCESO=20240101   # Dejar vacío para usar la fecha de hoy
REPORTE_FORMATO=xlsx         # xlsx o csv
```

## Uso

### Desde línea de comandos

```bash
# Procesar un archivo CSV
python -m src.etl.pipeline --fuente csv --archivo data/variables.csv

# Procesar desde base de datos
python -m src.etl.pipeline --fuente bd --consulta "SELECT * FROM variables WHERE fecha = CURRENT_DATE"

# Procesar desde API REST y cargar en BD
python -m src.etl.pipeline --fuente api --endpoint variables/diarias --destino bd --tabla variables_diarias

# Especificar fecha del proceso
python -m src.etl.pipeline --fuente csv --archivo data/variables.csv --fecha 20240115
```

### Desde Python

```python
from src.etl.pipeline import Pipeline
from src.etl.config import ConfigETL

pipeline = Pipeline()
resultado = pipeline.ejecutar(fuente="csv", archivo="data/variables.csv")
print(resultado)
```

## Pruebas

```bash
pytest tests/ -v
```

## Reglas de negocio

Las reglas de negocio están centralizadas en `src/reglas_negocio/reglas.py` como funciones puras documentadas:

| Función | Descripción |
|---|---|
| `validar_campos_obligatorios` | Verifica que todos los campos requeridos estén presentes |
| `validar_rango_valor` | Valida que los valores estén dentro del rango permitido |
| `calcular_distribucion_diaria` | Calcula la participación porcentual de cada registro |
| `calcular_variacion_respecto_anterior` | Calcula la variación respecto al periodo anterior |
| `clasificar_alerta` | Marca registros con variación superior al umbral (20 %) |
| `asignar_categoria_distribucion` | Clasifica registros en categorías A/B/C/D (Pareto) |
