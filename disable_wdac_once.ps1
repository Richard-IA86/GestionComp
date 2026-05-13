# DisableWDAC_Permanently.ps1
# Deshabilita WDAC permanentemente para que GestionComp funcione
# Ejecutar COMO ADMINISTRADOR una sola vez

#Requires -RunAsAdministrator

Write-Host "Deshabilitando WDAC (política de control de aplicaciones de Windows)..." -ForegroundColor Yellow
Write-Host ""

# Obtener la política WDAC actual
$policy = Get-CimInstance -Namespace "root\cimv2\mdm\dmmap" -ClassName "MDM_ApplicationControl_PolicyManager01"

if ($policy) {
    try {
        # Cambiar a modo Audit (0) - permite todo pero registra
        Set-CimInstance -CimInstance $policy -Property @{PolicyStatus = 0} | Out-Null
        Write-Host "✓ WDAC deshabilitado (modo Audit)" -ForegroundColor Green
        Write-Host "Los binarios de Python ahora funcionarán sin restricciones." -ForegroundColor Green
    } catch {
        Write-Host "✗ Error: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠ No se detectó política WDAC activa." -ForegroundColor Yellow
    Write-Host "Tu sistema puede no tener WDAC habilitado." -ForegroundColor Gray
}

Write-Host ""
Write-Host "Puedes ejecutar GestionComp normalmente ahora:" -ForegroundColor Cyan
Write-Host "  cd C:\Dev\GestionComp" -ForegroundColor Gray
Write-Host "  .venv\Scripts\python.exe main.py --solo-procesar" -ForegroundColor Gray
Write-Host ""
Write-Host "Presiona Enter para cerrar..." -ForegroundColor Gray
Read-Host
