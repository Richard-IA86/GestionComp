# PowerShell — Ejecución diaria programada del proceso Compensaciones
# Configurar en el Programador de Tareas de Windows para correr a las 21:00.
#
# Ejemplo de tarea programada (ejecutar como Administrador):
#   $action  = New-ScheduledTaskAction -Execute "pwsh.exe" `
#                -Argument "-NonInteractive -File C:\Dev\GestionComp\scripts\ejecutar_diario.ps1"
#   $trigger = New-ScheduledTaskTrigger -Daily -At "21:00"
#   Register-ScheduledTask -TaskName "Compensaciones_Diario" `
#                          -Action $action -Trigger $trigger -RunLevel Highest

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ROOT    = Split-Path $PSScriptRoot -Parent
$PYTHON  = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
$LOG_DIR = "$ROOT\logs"
$FECHA   = Get-Date -Format "yyyyMMdd"
$LOG_RUN = "$LOG_DIR\run_$FECHA.log"

Set-Location $ROOT

# Verificar que Python existe
if (-not (Test-Path $PYTHON)) {
    Write-Error "Python no encontrado en $PYTHON"
    exit 1
}

# Ejecutar el proceso principal (incluye verificación/activación de VPN en paso 0/4)
Write-Host "[RUN]  Iniciando proceso de compensaciones..." -ForegroundColor Cyan
& $PYTHON main.py 2>&1 | Tee-Object -FilePath $LOG_RUN -Append

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK]   Proceso completado. Ver logs en: $LOG_RUN" -ForegroundColor Green
} else {
    Write-Error "El proceso terminó con errores (código $LASTEXITCODE). Revisá $LOG_RUN"
    exit $LASTEXITCODE
}
