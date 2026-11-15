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
    echo.
    echo  [ERROR] winget is not available on this system.
    echo  Please install Python manually from:
    echo    https://www.python.org/downloads/
    echo  Make sure to check 'Add Python to PATH' during installation.
    echo.
    pause
    exit /b 1
)

winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install Python automatically.
    echo  Please install manually: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo  [INFO] Refreshing PATH...
set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%ProgramFiles%\Python312;%ProgramFiles%\Python312\Scripts;%PATH%"

:STEP2
REM ---- STEP 2: Install dependencies ----
echo.
echo  [Step 2/5] Installing required libraries...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade customtkinter requests pillow psutil py7zr
if %errorlevel% neq 0 (
    echo  [WARN] Some libraries may have failed to install. Continuing...
)
echo  [OK] Dependencies installed.

:STEP3
REM ---- STEP 3: Download latest launcher ----
echo.
echo  [Step 3/5] Downloading latest ARDA LAUNCHER...
set "INSTALL_DIR=%LOCALAPPDATA%\ArdaLauncher"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

set "LAUNCHER_URL=https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/launcher.pyw"
echo  [INFO] Downloading from: %LAUNCHER_URL%
powershell -NoProfile -Command "try {{ Invoke-WebRequest -Uri '%LAUNCHER_URL%' -OutFile '%INSTALL_DIR%\launcher.pyw' -UseBasicParsing; exit 0 }} catch {{ exit 1 }}"
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to download launcher.pyw
    echo  Check your internet connection and try again.
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\launcher.pyw" (
    echo  [ERROR] launcher.pyw was not saved properly.
    pause
    exit /b 1
)
echo  [OK] Latest launcher downloaded.

:STEP4
REM ---- STEP 4: Launch (consoleless) ----
echo.
echo  [Step 4/5] Launching ARDA LAUNCHER...
set "PYTHONW="
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHONW=pythonw"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe" (
        set "PYTHONW=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
    ) else if exist "%ProgramFiles%\Python312\pythonw.exe" (
        set "PYTHONW=%ProgramFiles%\Python312\pythonw.exe"
    ) else (
        set "PYTHONW=python"
    )
)

if "%PYTHONW%"=="pythonw" (
    start "" pythonw "%INSTALL_DIR%\launcher.pyw"
) else (
    start "" "%PYTHONW%" "%INSTALL_DIR%\launcher.pyw"
)
echo  [OK] ARDA LAUNCHER launched. A desktop shortcut will be created automatically.

:STEP5
REM ---- STEP 5: Success ----
echo.
echo  ============================================================
echo     SUCCESS!
echo  ============================================================
echo.
echo   ARDA LAUNCHER has been successfully installed and launched!
echo.
echo   Install location: %INSTALL_DIR%
echo   A desktop shortcut will be created automatically.
echo.
echo   You can close this window now.
echo.
pause
exit /b 0
