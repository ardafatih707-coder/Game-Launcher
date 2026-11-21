@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ARDA LAUNCHER V12.1 - Kurulum ve Guncelleme

set "OWNER=ardafatih707-coder"
set "REPO=Game-Launcher"
set "BRANCH=main"
if defined LOCALAPPDATA (
    set "INSTALL_DIR=%LOCALAPPDATA%\ArdaLauncher"
) else (
    set "INSTALL_DIR=%USERPROFILE%\AppData\Local\ArdaLauncher"
)
set "ARDA_INSTALL_DIR=%INSTALL_DIR%"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if errorlevel 1 goto :FAIL_DIR

where py >nul 2>&1
if errorlevel 1 goto :NO_PYTHON
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 goto :OLD_PYTHON

echo [1/3] Python paketleri kontrol ediliyor...
py -3 -m ensurepip --upgrade >nul 2>&1
py -3 -m pip install --user --upgrade customtkinter Pillow requests psutil
if errorlevel 1 goto :FAIL_PIP

echo [2/3] GitHub'dan surum bilgisi ve launcher indiriliyor...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $base='https://raw.githubusercontent.com/%OWNER%/%REPO%/%BRANCH%'; $meta=Invoke-RestMethod -Uri ($base+'/version.json') -TimeoutSec 30; $name=[string]$meta.launcher_file; if($name -ne 'ArdaLauncher.pyw' -or [IO.Path]::GetFileName($name) -ne $name){throw 'version.json launcher_file degeri guvensiz veya beklenmeyen.'}; $expectedUrl=$base+'/ArdaLauncher.pyw'; $url=[string]$meta.launcher_url; if($url -ne $expectedUrl){throw 'Launcher URL depo/branch ile eslesmiyor.'}; $expected=([string]$meta.sha256).ToLowerInvariant(); if($expected -notmatch '^[0-9a-f]{64}$'){throw 'version.json SHA256 alani eksik veya gecersiz.'}; $dest=Join-Path $env:ARDA_INSTALL_DIR $name; $tmp=$dest+'.download'; try { Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing -TimeoutSec 90; $actual=(Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash.ToLowerInvariant(); if($actual -ne $expected){throw 'SHA256 dogrulamasi basarisiz.'}; Move-Item -LiteralPath $tmp -Destination $dest -Force } finally { if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue} }; Write-Host ('ARDA LAUNCHER v'+$meta.version+' indirildi ve SHA256 dogrulandi.')"
if errorlevel 1 goto :FAIL_DOWNLOAD

echo [3/3] Launcher baslatiliyor...
for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%P"
for %%P in ("%PYTHON_EXE%") do set "PYTHONW_EXE=%%~dpPpythonw.exe"
if exist "%PYTHONW_EXE%" (
    start "" /D "%INSTALL_DIR%" "%PYTHONW_EXE%" "%INSTALL_DIR%\ArdaLauncher.pyw"
) else (
    start "" /D "%INSTALL_DIR%" "%PYTHON_EXE%" "%INSTALL_DIR%\ArdaLauncher.pyw"
)
echo Kurulum tamamlandi.
goto :END

:NO_PYTHON
echo Python 3.10 veya daha yenisi bulunamadi. Python kurulumu gerekiyor.
start "" "https://www.python.org/downloads/windows/"
pause
exit /b 1

:OLD_PYTHON
echo Python 3.10 veya daha yenisi gerekli. Lutfen Python'u guncelleyin.
start "" "https://www.python.org/downloads/windows/"
pause
exit /b 1

:FAIL_DIR
echo Kurulum klasoru olusturulamadi: %INSTALL_DIR%
pause
exit /b 1

:FAIL_PIP
echo Gerekli Python paketleri yuklenemedi. Internet ve pip ayarlarini kontrol edin.
pause
exit /b 1

:FAIL_DOWNLOAD
echo GitHub'dan dosya indirilemedi veya SHA256 dogrulamasi basarisiz.
echo Depo/branch ve version.json dosyasini kontrol edin.
pause
exit /b 1

:END
pause
endlocal
