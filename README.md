# Compensaciones — Automatización de Reportes Diarios

Proyecto de automatización para la descarga, procesamiento y generación de
informes de dirección diarios basados en reportes del sistema interno.

## Arquitectura del proyecto

```
Compensaciones/
├── main.py                         ← Punto de entrada principal
├── requirements.txt                ← Dependencias Python
├── .env                            ← Credenciales (NO subir a Git)
├── .env.example                    ← Template de variables de entorno
├── .gitignore
│
├── config/
│   └── settings.py                 ← Configuración centralizada (rutas, parámetros)
│
├── src/
│   ├── descarga/
│   │   └── scraper.py              ← Playwright: login + descarga de reportes
│   ├── procesamiento/
│   │   └── enriquecimiento.py      ← Pandas: limpieza y transformación de datos
│   ├── reportes/
│   │   └── generador.py            ← Generación de Excel / informes de dirección
│   └── utils/
│       └── logger.py               ← Configuración de Loguru
│
├── input_raw/                      ← Archivos descargados del sistema (fuente)
├── output/
│   ├── reportes/                   ← Excel procesados / intermedios
│   └── informes_direccion/         ← Informes finales para dirección
├── logs/                           ← Logs rotativos (retención 30 días)
└── scripts/
    ├── setup.ps1                   ← Setup inicial del entorno
    └── ejecutar_diario.ps1         ← Ejecución programada (Programador de Tareas)
```

## Requisitos previos

- Python 3.10 o superior
- VPN de la empresa activa (servidor: `10.2.1.81`)

## Instalación (primera vez)

```powershell
# 1. Clonar / abrir el proyecto en VSCode
# 2. Ejecutar el setup (crea .venv, instala paquetes y Playwright)
.\scripts\setup.ps1

# 3. Editar .env con tus credenciales
notepad .env
```

## Uso

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Flujo completo: descarga + procesamiento + informe
python main.py

# Solo procesar archivos existentes en input_raw/ (sin descargar)
python main.py --solo-procesar

# Fecha específica
python main.py --fecha 2026-04-09
```

## Programar ejecución automática diaria

```powershell
# Ejecutar como Administrador para registrar la tarea
$action  = New-ScheduledTaskAction -Execute "pwsh.exe" `
             -Argument "-NonInteractive -File C:\Dev\Compensaciones\scripts\ejecutar_diario.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "07:00"
Register-ScheduledTask -TaskName "Compensaciones_Diario" -Action $action -Trigger $trigger
```

## Archivos fuente (input_raw/)

| Archivo | Descripción |
|---|---|
| `Cuenta corriente CONSTRUYA AL COSTO SRL - Pronto.xlsx` | Movimientos de cuenta corriente |
| `Gastos.xlsx` | Detalle de gastos del período |
| `Listado Detallado de Órdenes de Pago - Pronto.xlsx` | Detalle completo de órdenes de pago |
| `Ordenes de Pago - Pronto.xlsx` | Resumen de órdenes de pago |

## Personalización del scraper

El archivo `src/descarga/scraper.py` contiene marcadores `# TODO:` donde hay que
ajustar los selectores CSS según el HTML real de la aplicación web:

- Campos de usuario/contraseña del formulario de login
- Campos de filtro de fecha en cada reporte
- Botón de búsqueda/filtrado
- Botón de exportación/descarga
- URLs de cada sección de reporte

## Logs

Los logs se guardan en `logs/compensaciones.log` con rotación diaria y retención
de 30 días. Cada ejecución del script diario genera además un `logs/run_YYYYMMDD.log`.
