@echo off
setlocal enabledelayedexpansion

title ComfyUI Server Startup
color 0A

if "%comfyui_env%"=="" (
    set comfyui_env=prod
)

echo.
echo ========================================
echo   ComfyUI Server Startup
echo   Environment: %comfyui_env%
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION%
echo.

echo [2/5] Checking uv package manager...
where uv >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing uv...
    
    python -m pip install uv
    
    if errorlevel 1 (
        echo [ERROR] Failed to install uv
        echo.
        pause
        exit /b 1
    )
    
    echo [OK] uv installed
) else (
    echo [OK] uv found
)
echo.

echo [3/5] Checking config file...
if not exist "config_%comfyui_env%.yml" (
    echo [ERROR] Config file not found: config_%comfyui_env%.yml
    echo Please create config file based on config.example.yml
    echo.
    pause
    exit /b 1
)
echo [OK] config_%comfyui_env%.yml
echo.

echo [4/5] Checking MySQL...
if not exist "bin\mysql" (
    echo [ERROR] MySQL directory not found: bin\mysql
    echo Please deploy MySQL to bin\mysql directory
    echo.
    pause
    exit /b 1
)
echo [OK] MySQL directory found
echo.

echo [5/5] Starting services...
echo ========================================
echo.

uv run --with-requirements requirements.txt start_windows.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Program exited with code: %errorlevel%
    echo ========================================
    echo.
    pause
)

endlocal
