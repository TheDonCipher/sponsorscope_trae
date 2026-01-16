<#
.SYNOPSIS
    SponsorScope System Startup Script
    Automates dependency installation and service launching for the SponsorScope platform.

.DESCRIPTION
    1. Checks and installs Python backend dependencies.
    2. Checks and installs Node.js frontend dependencies.
    3. Launches the FastAPI backend server in a separate process.
    4. Launches the Next.js frontend server in the current process.
#>

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot

function Print-Logo {
    Write-Host "
   _____                                 _____                         
  / ____|                               / ____|                        
 | (___  _ __   ___  _ __  ___  ___  __| (___   ___ ___  _ __   ___  
  \___ \| '_ \ / _ \| '_ \/ __|/ _ \/ _ \___ \ / __/ _ \| '_ \ / _ \ 
  ____) | |_) | (_) | | | \__ \ (_) | | |____) | (_| (_) | |_) |  __/ 
 |_____/| .__/ \___/|_| |_|___/\___/|_| |_____/ \___\___/| .__/ \___| 
        | |                                              | |         
        |_|                                              |_|         
    " -ForegroundColor Green
    Write-Host "    >>> INTELLIGENCE SUITE V2.4 <<<" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param($Message)
    Write-Host "[:] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host " [OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host " [!] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param($Message)
    Write-Host " [X] $Message" -ForegroundColor Red
}

# --- Main Execution ---

Print-Logo

# 1. Backend Initialization
Write-Step "Initializing Neural Backend Node..."

if (Test-Path "$ScriptRoot\requirements.txt") {
    Write-Host "    Verifying python dependencies..." -ForegroundColor Gray
    try {
        # Check if modules are installed to save time, or just run install (pip is usually fast if cached)
        pip install -r "$ScriptRoot\requirements.txt" | Out-Null
        Write-Success "Backend dependencies verified."
    } catch {
        Write-ErrorMsg "Failed to install backend dependencies. Ensure Python/Pip is in PATH."
        exit 1
    }
} else {
    Write-ErrorMsg "Critical Error: requirements.txt missing."
    exit 1
}

# 2. Frontend Initialization
Write-Step "Initializing Interface Layer..."

$FrontendPath = Join-Path $ScriptRoot "apps\frontend"

if (Test-Path $FrontendPath) {
    Push-Location $FrontendPath
    if (Test-Path "package.json") {
        Write-Host "    Verifying node modules..." -ForegroundColor Gray
        try {
            # Use npm ci if package-lock exists for faster/cleaner install, else npm install
            if (Test-Path "package-lock.json") {
                npm ci | Out-Null
            } else {
                npm install | Out-Null
            }
            Write-Success "Frontend dependencies verified."
        } catch {
            Write-ErrorMsg "Failed to install frontend dependencies. Ensure Node/NPM is in PATH."
            Pop-Location
            exit 1
        }
    } else {
        Write-ErrorMsg "package.json not found in frontend directory."
        Pop-Location
        exit 1
    }
    Pop-Location
} else {
    Write-ErrorMsg "Frontend directory structure invalid."
    exit 1
}

# 3. Launch Services
Write-Step "Engaging Core Systems..."

# Start Backend (New Window)
Write-Host "    > Spawning API Process (Port 8000)..." -ForegroundColor Gray
try {
    $BackendCmd = "uvicorn services.api.main:app --reload"
    # Start-Process allows us to open a new window so the backend logs don't clutter the frontend logs
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptRoot'; $BackendCmd" -WorkingDirectory $ScriptRoot
    Write-Success "Backend signal established."
} catch {
    Write-ErrorMsg "Failed to launch backend process."
    exit 1
}

# Wait briefly for backend to spin up
Start-Sleep -Seconds 3

# Start Frontend (Current Window)
Write-Host "    > Spawning Interface Process..." -ForegroundColor Gray
Write-Step "SponsorScope Systems Online."
Write-Host "    Press Ctrl+C to terminate frontend session." -ForegroundColor DarkGray

Push-Location $FrontendPath
npm run dev
