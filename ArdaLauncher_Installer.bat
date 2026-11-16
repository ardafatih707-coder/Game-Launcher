@echo off
setlocal EnableDelayedExpansion
title ARDA LAUNCHER Installer
color 0B
echo [1/5] Python check...
python --version >nul 2>&1
if %errorlevel% equ 0 goto :STEP2
winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
:STEP2
echo [2/5] Libraries...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade customtkinter requests pillow psutil py7zr
:STEP3
echo [3/5] Download...
set "INSTALL_DIR=%LOCALAPPDATA%\ArdaLauncher"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
set "LAUNCHER_URL=https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/launcher.pyw"
powershell -NoProfile -Command "try {{ Invoke-WebRequest -Uri '%LAUNCHER_URL%' -OutFile '%INSTALL_DIR%\launcher.pyw' -UseBasicParsing; exit 0 }} catch {{ exit 1 }}"
:STEP4
echo [4/5] Launching...
where pythonw >nul 2>&1
if %errorlevel% equ 0 (start "" pythonw "%INSTALL_DIR%\launcher.pyw") else (start "" python "%INSTALL_DIR%\launcher.pyw")
:STEP5
echo SUCCESS!
pause
