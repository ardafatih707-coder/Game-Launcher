@echo off
setlocal EnableDelayedExpansion
title ARDA LAUNCHER - Auto Installer
color 0B
echo.
echo  ============================================================
echo     ARDA LAUNCHER - Automatic Installer
echo  ============================================================
echo.
REM ---- STEP 1: Check / Install Python ----
echo  [Step 1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Python is already installed.
    goto :STEP2
)
echo  [INFO] Python not found. Attempting to install via winget...
where winget >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] winget is not available. Install Python manually:
    echo    https://www.python.org/downloads/
    pause
    exit /b 1
)
winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install Python.
    pause
    exit /b 1
)
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"
:STEP2
echo.
echo  [Step 2/5] Installing required libraries...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade customtkinter requests pillow psutil py7zr
echo  [OK] Dependencies installed.
:STEP3
echo.
echo  [Step 3/5] Downloading latest ARDA LAUNCHER...
set "INSTALL_DIR=%LOCALAPPDATA%\ArdaLauncher"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
set "LAUNCHER_URL=https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/launcher.pyw"
echo  [INFO] Downloading from: %LAUNCHER_URL%
powershell -NoProfile -Command "try {{ Invoke-WebRequest -Uri '%LAUNCHER_URL%' -OutFile '%INSTALL_DIR%\launcher.pyw' -UseBasicParsing; exit 0 }} catch {{ exit 1 }}"
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to download launcher.pyw
    pause
    exit /b 1
)
echo  [OK] Latest launcher downloaded.
:STEP4
echo.
echo  [Step 4/5] Launching ARDA LAUNCHER...
set "PYTHONW="
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHONW=pythonw"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" (
    set "PYTHONW=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
) else if exist "%ProgramFiles%\Python312\pythonw.exe" (
    set "PYTHONW=%ProgramFiles%\Python312\pythonw.exe"
) else (
    set "PYTHONW=python"
)
start "" "%PYTHONW%" "%INSTALL_DIR%\launcher.pyw"
:STEP5
echo.
echo  ============================================================
echo     SUCCESS!
echo  ============================================================
echo   ARDA LAUNCHER has been successfully installed and launched!
pause
exit /b 0
