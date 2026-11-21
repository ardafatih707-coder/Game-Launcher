@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ARDA LAUNCHER V12.1 - Installer and Updater

rem ============================================================
rem ARDA LAUNCHER - Automatic Windows installer and updater
rem English-language installer. Requires Windows 10/11 and internet.
rem ============================================================

set "OWNER=ardafatih707-coder"
set "REPO=Game-Launcher"
set "BRANCH=main"
set "MIN_PYTHON=3.10"
set "PYTHON_INSTALLER_VERSION=3.13.17"

if defined LOCALAPPDATA (
    set "INSTALL_DIR=%LOCALAPPDATA%\ArdaLauncher"
) else (
    set "INSTALL_DIR=%USERPROFILE%\AppData\Local\ArdaLauncher"
)
set "ARDA_INSTALL_DIR=%INSTALL_DIR%"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if errorlevel 1 goto :FAIL_DIR

echo.
echo ============================================================
echo                 ARDA LAUNCHER V12.1
echo             Automatic Installer and Updater
echo ============================================================
echo.

echo [1/4] Checking for a compatible Python installation...
call :FIND_PYTHON
if not defined PYTHON_EXE goto :INSTALL_PYTHON
"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 goto :INSTALL_PYTHON
goto :PYTHON_READY

:INSTALL_PYTHON
echo.
echo Python 3.10 or newer was not found. Installing Python 3.13...
where winget >nul 2>&1
if not errorlevel 1 (
    echo Attempting installation through Windows Package Manager...
    winget install --id Python.Python.3.13 --exact --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
    call :FIND_PYTHON
    if defined PYTHON_EXE (
        "%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
        if not errorlevel 1 goto :PYTHON_READY
    )
    echo Windows Package Manager did not provide a usable Python installation.
)

echo Trying the official Python installer from python.org...
set "PYTHON_INSTALLER=%TEMP%\arda-python-installer.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $arch=$env:PROCESSOR_ARCHITECTURE; if($arch -eq 'ARM64'){$file='python-3.13.17-arm64.exe'} elseif($arch -eq 'AMD64'){$file='python-3.13.17-amd64.exe'} else {throw 'Automatic Python installation is supported on 64-bit Intel/AMD and ARM64 Windows.'}; $url='https://www.python.org/ftp/python/3.13.17/'+$file; $installer=Join-Path $env:TEMP 'arda-python-installer.exe'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing -TimeoutSec 180; $sig=Get-AuthenticodeSignature -FilePath $installer; if($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Python Software Foundation'){throw 'The downloaded Python installer signature could not be verified.'}; $p=Start-Process -FilePath $installer -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1 Include_pip=1 Include_test=0' -Wait -PassThru; if($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010){throw ('Python setup failed with exit code '+$p.ExitCode)}; Remove-Item -LiteralPath $installer -Force -ErrorAction SilentlyContinue"
if errorlevel 1 goto :FAIL_PYTHON
call :FIND_PYTHON
if not defined PYTHON_EXE goto :FAIL_PYTHON
"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 goto :FAIL_PYTHON

:PYTHON_READY
echo Python detected: 
echo %PYTHON_EXE%

echo.
echo [2/4] Installing required Python packages...
"%PYTHON_EXE%" -m ensurepip --upgrade >nul 2>&1
"%PYTHON_EXE%" -m pip install --user --upgrade --disable-pip-version-check pip
if errorlevel 1 goto :FAIL_PIP
"%PYTHON_EXE%" -m pip install --user --upgrade --disable-pip-version-check customtkinter Pillow requests psutil
if errorlevel 1 goto :FAIL_PIP
"%PYTHON_EXE%" -c "import customtkinter, PIL, requests, psutil" >nul 2>&1
if errorlevel 1 goto :FAIL_VERIFY_PACKAGES

echo.
echo [3/4] Downloading the launcher from GitHub and verifying its checksum...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $base='https://raw.githubusercontent.com/%OWNER%/%REPO%/%BRANCH%'; $meta=Invoke-RestMethod -Uri ($base+'/version.json') -TimeoutSec 30; if([string]$meta.launcher_file -ne 'ArdaLauncher.pyw'){throw 'Unexpected or unsafe launcher filename in version.json.'}; $name=[IO.Path]::GetFileName([string]$meta.launcher_file); if($name -ne 'ArdaLauncher.pyw'){throw 'The launcher filename is invalid.'}; $expectedUrl=$base+'/ArdaLauncher.pyw'; $url=[string]$meta.launcher_url; if($url -ne $expectedUrl){throw 'The launcher URL does not match the configured repository and branch.'}; $expected=([string]$meta.sha256).ToLowerInvariant(); if($expected -notmatch '^[0-9a-f]{64}$'){throw 'The SHA-256 value in version.json is missing or invalid.'}; $dest=Join-Path $env:ARDA_INSTALL_DIR $name; $tmp=$dest+'.download'; try { Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing -TimeoutSec 120; $actual=(Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash.ToLowerInvariant(); if($actual -ne $expected){throw 'SHA-256 verification failed. The downloaded file was not installed.'}; Move-Item -LiteralPath $tmp -Destination $dest -Force } finally { if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue} }; Write-Host ('ARDA LAUNCHER v'+$meta.version+' downloaded. SHA-256 verification passed.')"
if errorlevel 1 goto :FAIL_DOWNLOAD

echo.
echo [4/4] Starting ARDA LAUNCHER...
for %%P in ("%PYTHON_EXE%") do set "PYTHONW_EXE=%%~dpPpythonw.exe"
if exist "%PYTHONW_EXE%" (
    start "" /D "%INSTALL_DIR%" "%PYTHONW_EXE%" "%INSTALL_DIR%\ArdaLauncher.pyw"
) else (
    start "" /D "%INSTALL_DIR%" "%PYTHON_EXE%" "%INSTALL_DIR%\ArdaLauncher.pyw"
)
echo.
echo Installation completed successfully.
echo You can close this window now.
goto :END

:FIND_PYTHON
set "PYTHON_EXE="
if defined LOCALAPPDATA if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if defined PYTHON_EXE goto :EOF
where py >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)
if defined PYTHON_EXE goto :EOF
where python >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%P"
)
goto :EOF

:FAIL_DIR
echo ERROR: The installation directory could not be created:
echo %INSTALL_DIR%
goto :FAILED

:FAIL_PYTHON
echo ERROR: Python could not be installed or a compatible Python version could not be found.
echo Install Python 3.10 or newer from the official Python website, then run this installer again:
start "" "https://www.python.org/downloads/windows/"
goto :FAILED

:FAIL_PIP
echo ERROR: Required Python packages could not be installed.
echo Check your internet connection and Python package installation permissions.
goto :FAILED

:FAIL_VERIFY_PACKAGES
echo ERROR: One or more required Python packages could not be imported after installation.
echo Please run the installer again or check the Python installation.
goto :FAILED

:FAIL_DOWNLOAD
echo ERROR: The launcher could not be downloaded from GitHub or its SHA-256 verification failed.
echo Check the repository, branch, version.json file, and internet connection.
goto :FAILED

:FAILED
echo.
echo Installation failed. Review the error messages above.
echo Press any key to close this window.
pause >nul
exit /b 1

:END
echo Press any key to close this window.
pause >nul
endlocal
exit /b 0
