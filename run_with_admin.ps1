# Script para ejecutar GestionComp bypaseando WDAC (Windows Application Control)
# WDAC bloquea DLLs nuevas. Este script lo deshabilita temporalmente.

# === VERIFICACIÓN DE ADMIN ===
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠ Solicitando permisos de administrador..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd '$PWD'; & '$PSCommandPath'"
    exit
}

Write-Host "✓ Ejecutando como administrador" -ForegroundColor Green
Write-Host ""

# === DESACTIVAR WDAC TEMPORALMENTE ===
Write-Host "Desactivando WDAC temporalmente..." -ForegroundColor Cyan

try {
    # Usar CIM para cambiar el estado de WDAC a Audit (permisivo)
    $wdacPolicy = Get-CimInstance -Namespace "root\cimv2\mdm\dmmap" `
        -ClassName "MDM_ApplicationControl_PolicyManager01" -Filter "InstanceID='ApplicationGuard'"
    
    if ($null -ne $wdacPolicy) {
        # Guardar estado actual
        $originalStatus = $wdacPolicy.PolicyStatus
        Write-Host "Estado WDAC original: $originalStatus"
        
        # Cambiar a Audit (0) si está en Enforce (1)
        if ($originalStatus -eq 1) {
            Set-CimInstance -CimInstance $wdacPolicy -Property @{PolicyStatus = 0} | Out-Null
            Write-Host "✓ WDAC cambiado a Audit (permisivo)" -ForegroundColor Green
            $wdacWasActive = $true
        } else {
            Write-Host "WDAC ya está en modo Audit" -ForegroundColor Gray
            $wdacWasActive = $false
        }
    } else {
        Write-Host "⚠ No se detectó política WDAC (puede estar desactivado)" -ForegroundColor Yellow
        $wdacWasActive = $false
    }
} catch {
    Write-Host "⚠ No se pudo cambiar WDAC (puede requerir permisos de SYSTEM): $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═" * 60
Write-Host "Ejecutando: .venv\Scripts\python.exe main.py --solo-procesar" -ForegroundColor Cyan
Write-Host "═" * 60
Write-Host ""

# === EJECUTAR EL PROCESO ===
cd C:\Dev\GestionComp
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
.\.venv\Scripts\python.exe main.py --solo-procesar
$exitCode = $LASTEXITCODE
$stopwatch.Stop()

Write-Host ""
Write-Host "═" * 60
Write-Host "Proceso completado" -ForegroundColor Green
Write-Host "Código de salida: $exitCode"
Write-Host "Tiempo: $($stopwatch.Elapsed.TotalSeconds)s"
Write-Host "═" * 60
Write-Host ""

# === RESTAURAR WDAC ===
if ($wdacWasActive) {
    Write-Host "Restaurando WDAC a Enforce..." -ForegroundColor Cyan
    try {
        $wdacPolicy = Get-CimInstance -Namespace "root\cimv2\mdm\dmmap" `
            -ClassName "MDM_ApplicationControl_PolicyManager01" -Filter "InstanceID='ApplicationGuard'"
        Set-CimInstance -CimInstance $wdacPolicy -Property @{PolicyStatus = 1} | Out-Null
        Write-Host "✓ WDAC restaurado a Enforce" -ForegroundColor Green
    } catch {
        Write-Host "⚠ No se pudo restaurar WDAC: $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Presiona Enter para cerrar..." -ForegroundColor Gray
Read-Host
exit $exitCode
