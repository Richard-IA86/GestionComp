# Ejecutar GestionComp como administrador (bypass WDAC)
param(
    [switch]$NoExit = $false
)

# Verificar admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Solicitando permisos de administrador..." -ForegroundColor Yellow
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $scriptPath
    exit
}

Write-Host "Administrador OK" -ForegroundColor Green

# Ejecutar proceso
cd C:\Dev\GestionComp
Write-Host "Iniciando main.py --solo-procesar..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe main.py --solo-procesar

$code = $LASTEXITCODE
Write-Host ""
Write-Host "Completado con codigo: $code" -ForegroundColor Green

if ($NoExit) {
    Write-Host "Presiona Enter para cerrar..." -ForegroundColor Gray
    Read-Host
}

exit $code
