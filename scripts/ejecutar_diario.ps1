# PowerShell — Ejecución diaria programada del proceso Compensaciones
# Configurar en el Programador de Tareas de Windows para correr cada mañana.
#
# Ejemplo de tarea programada (ejecutar como Administrador):
#   $action  = New-ScheduledTaskAction -Execute "pwsh.exe" `
#                -Argument "-NonInteractive -File C:\Dev\Compensaciones\scripts\ejecutar_diario.ps1"
#   $trigger = New-ScheduledTaskTrigger -Daily -At "07:00"
#   Register-ScheduledTask -TaskName "Compensaciones_Diario" -Action $action -Trigger $trigger

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

# Verificar conectividad VPN (ping al servidor)
Write-Host "[VPN] Verificando conectividad con 10.2.1.81..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName "10.2.1.81" -Count 1 -Quiet -ErrorAction SilentlyContinue
if (-not $ping) {
    $msg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | ERROR | No hay conectividad con 10.2.1.81. ¿VPN activa?"
    Add-Content $LOG_RUN $msg
    Write-Error "Sin conexión al servidor. Verificá que la VPN esté conectada."
    exit 1
}
Write-Host "       Conectividad OK." -ForegroundColor Green

# Ejecutar el proceso principal
Write-Host "[RUN]  Iniciando proceso de compensaciones..." -ForegroundColor Cyan
& $PYTHON main.py 2>&1 | Tee-Object -FilePath $LOG_RUN -Append

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[OK]   Proceso completado. Ver logs en: $LOG_RUN" -ForegroundColor Green
} else {
    Write-Error "El proceso terminó con errores (código $LASTEXITCODE). Revisá $LOG_RUN"
    exit $LASTEXITCODE
}
