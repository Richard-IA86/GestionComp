# PowerShell — Setup inicial del proyecto Compensaciones
# Ejecutar UNA sola vez: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

$ROOT = Split-Path $PSScriptRoot -Parent
Set-Location $ROOT

Write-Host "`n══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Compensaciones — Setup del entorno" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════`n" -ForegroundColor Cyan

# ── 1. Verificar Python ──────────────────────────────────────────────────────
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonExe = $null
foreach ($cmd in @("python", "python3", "py")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) { $pythonExe = $cmd; break }
}
if (-not $pythonExe) {
    Write-Error "Python no encontrado. Instalá Python 3.10+ desde https://python.org"
    exit 1
}
$pyVersion = & $pythonExe --version
Write-Host "      $pyVersion" -ForegroundColor Green

# ── 2. Crear entorno virtual ─────────────────────────────────────────────────
Write-Host "[2/5] Creando entorno virtual .venv..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "      .venv ya existe, se omite la creación." -ForegroundColor DarkGray
} else {
    & $pythonExe -m venv .venv
    Write-Host "      .venv creado." -ForegroundColor Green
}

# ── 3. Instalar dependencias ─────────────────────────────────────────────────
Write-Host "[3/5] Instalando dependencias (requirements.txt)..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\.venv\Scripts\pip.exe install -r requirements.txt --quiet
Write-Host "      Dependencias instaladas." -ForegroundColor Green

# ── 4. Instalar browsers de Playwright ──────────────────────────────────────
Write-Host "[4/5] Instalando navegadores de Playwright (Chromium)..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m playwright install chromium
Write-Host "      Chromium instalado." -ForegroundColor Green

# ── 5. Configurar .env ───────────────────────────────────────────────────────
Write-Host "[5/5] Configurando .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "      .env ya existe, no se sobreescribe." -ForegroundColor DarkGray
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "      .env creado desde .env.example." -ForegroundColor Green
    Write-Host "      *** EDITÁ .env con tus credenciales antes de correr el script ***" -ForegroundColor Magenta
}

Write-Host "`n══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Setup completado exitosamente" -ForegroundColor Cyan
Write-Host "  Siguiente paso: editá .env y ejecutá:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\python.exe main.py" -ForegroundColor White
Write-Host "══════════════════════════════════════════`n" -ForegroundColor Cyan
