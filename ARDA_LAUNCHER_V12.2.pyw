#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ARDA LAUNCHER v12.2 - GitHub dagitim dosyasi, yerel kurtarma ve guvenli indirme."""
import sys, os, json, time, hashlib, hmac, secrets, threading, shutil, queue
import subprocess, ctypes, zipfile, re, base64, random, webbrowser, stat
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlparse, quote
from datetime import datetime, timedelta

def _show_fatal(title, msg):
    try:
        import tkinter as tk
        from tkinter import scrolledtext
        r = tk.Tk(); r.title(title); r.geometry("1000x600"); r.configure(bg="#0B0E14")
        tk.Label(r, text="⚠ " + title, bg="#0B0E14", fg="#FF4D6D",
                 font=("Arial", 13, "bold")).pack(pady=8)
        t = scrolledtext.ScrolledText(r, bg="#131823", fg="#E6EAF2", font=("Consolas", 10))
        t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("end", msg); t.configure(state="disabled")
        tk.Button(r, text="Kapat", command=r.destroy).pack(pady=6)
        r.mainloop()
    except Exception:
        sys.stderr.write(title + "\n" + msg + "\n")

sys.excepthook = lambda t, v, tb: _show_fatal(
    "Beklenmeyen Hata",
    "".join(__import__("traceback").format_exception(t, v, tb)))

try: import requests
except ImportError:
    _show_fatal("Eksik", "pip install customtkinter Pillow requests psutil"); sys.exit(1)
try: import customtkinter as ctk
except ImportError:
    _show_fatal("Eksik", "pip install customtkinter Pillow requests psutil"); sys.exit(1)
try: from PIL import Image, ImageDraw, ImageOps
except ImportError:
    _show_fatal("Eksik", "pip install customtkinter Pillow requests psutil"); sys.exit(1)
from tkinter import filedialog, messagebox
try: import winreg
except ImportError: winreg = None
try: import psutil
except ImportError: psutil = None

APP_NAME = "ARDA LAUNCHER"
APP_VERSION = "12.2"
GITHUB_REPO = "ardafatih707-coder/Game-Launcher"

INSTALLER_BAT_TEMPLATE = r"""@echo off
setlocal EnableExtensions
chcp 65001 >nul
title ARDA LAUNCHER V12.2 - Installer and Updater

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
echo                 ARDA LAUNCHER V12.2
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
exit /b 0"""
FEEDBACK_URL = "https://docs.google.com/forms/d/e/1FAIpQLScd8YSQxVNtVBbiyJtZg-UAkhOkPhK_dwA0ZjOJKP9Q9tH8PQ/viewform?usp=dialog"
STEAM_CDNS = ["https://cdn.akamai.steamstatic.com", "https://cdn.cloudflare.steamstatic.com", "https://steamstatic.com"]
DATA_DIR = Path(os.environ.get("LOCALAPPDATA") or str(Path.home())) / "ArdaLauncher"
DATA_DIR.mkdir(parents=True, exist_ok=True)
COVERS_DIR = DATA_DIR / "covers"; COVERS_DIR.mkdir(exist_ok=True)
DOWNLOADS_DIR = DATA_DIR / "downloads"; DOWNLOADS_DIR.mkdir(exist_ok=True)
ICON_FILE = DATA_DIR / "arda_icon.ico"
SETTINGS_FILE = DATA_DIR / "settings.json"
LIBRARY_FILE = DATA_DIR / "library.json"
WISHLIST_FILE = DATA_DIR / "wishlist.json"
DOWNLOAD_LOG_FILE = DATA_DIR / "download_log.json"
ERROR_LOG = DATA_DIR / "errors.log"
SECURITY_LOCKOUT_FILE = DATA_DIR / "lockout.json"

def log_error(msg):
    try:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except: pass

def hash_password(password, salt=None):
    if salt is None: salt = secrets.token_bytes(32)
    iterations = 260000
    if not isinstance(password, str):
        raise TypeError("password must be str")
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return {"salt": base64.b64encode(salt).decode(),
            "hash": base64.b64encode(h).decode(),
            "iterations": iterations}

def verify_password(password, stored):
    try:
        salt = base64.b64decode(stored["salt"])
        expected = base64.b64decode(stored["hash"])
        iterations = int(stored.get("iterations", 260000))
        if not 100000 <= iterations <= 1000000:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except Exception: return False


# Sabit V12 geliştirici kimlik doğrulaması. Düz metin parola kaynakta tutulmaz.
DEV_LOGIN_HASH = {'salt': 'jD6aTyXRe2DkosnxPXtQhqG05sjwktOnXB6LT2oNknM=', 'hash': 'XIl/Z1SmdenA3VVwegMEamJ4m/uakqEg91X5iSEpHHM=', 'iterations': 260000}

def is_strong_password(password):
    return bool(
        isinstance(password, str) and len(password) >= 12
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[^A-Za-z0-9]", password)
    )


def _dpapi_blob_type():
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
    return DATA_BLOB


def _dpapi_encrypt(data):
    if os.name != "nt":
        raise OSError("Windows DPAPI yalnızca Windows'ta kullanılabilir.")
    DATA_BLOB = _dpapi_blob_type()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptProtectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.c_wchar_p,
        ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(DATA_BLOB)]
    crypt32.CryptProtectData.restype = ctypes.c_int
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    source_buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source = DATA_BLOB(len(data), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte)))
    output = DATA_BLOB()
    if not crypt32.CryptProtectData(ctypes.byref(source), "ARDA LAUNCHER secret",
                                    None, None, None, 0, ctypes.byref(output)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))


def _dpapi_decrypt(data):
    if os.name != "nt":
        raise OSError("Windows DPAPI yalnızca Windows'ta kullanılabilir.")
    DATA_BLOB = _dpapi_blob_type()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crypt32.CryptUnprotectData.argtypes = [ctypes.POINTER(DATA_BLOB), ctypes.POINTER(ctypes.c_wchar_p),
        ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.POINTER(DATA_BLOB)]
    crypt32.CryptUnprotectData.restype = ctypes.c_int
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    source_buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source = DATA_BLOB(len(data), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_ubyte)))
    output = DATA_BLOB()
    if not crypt32.CryptUnprotectData(ctypes.byref(source), None, None, None, None, 0,
                                      ctypes.byref(output)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))

def encrypt_secret(text):
    try: return base64.b64encode(_dpapi_encrypt(text.encode())).decode()
    except: return ""

def decrypt_secret(enc):
    if not enc: return ""
    try: return _dpapi_decrypt(base64.b64decode(enc)).decode()
    except: return ""

def load_json(path, default=None):
    """Load JSON, falling back to a backup and finally to a fresh default."""
    fallback = {} if default is None else default
    path = Path(path)
    for candidate in (path, Path(str(path) + ".bak")):
        try:
            with candidate.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            log_error(f"load_json {candidate.name}: {exc}")
    return fallback

def save_json(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.flush(); os.fsync(f.fileno())
        if path.exists():
            # Never replace a known-good backup with a corrupt/truncated current file.
            try:
                with path.open("r", encoding="utf-8") as current:
                    json.load(current)
                shutil.copy2(path, Path(str(path) + ".bak"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                pass
        os.replace(tmp, path)
        return True
    except Exception as e:
        log_error(f"save_json: {e}")
        try: tmp.unlink()
        except: pass
        return False

def safe_extract_zip(zip_path, target_dir, max_files=10000, max_uncompressed=4 * 1024**3):
    """Extract a ZIP without path traversal, symlink or oversized-archive writes."""
    target = Path(target_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)
    extracted = 0
    total_size = 0
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            infos = archive.infolist()
            if len(infos) > max_files:
                raise ValueError("ZIP içinde izin verilenden fazla dosya var.")
            for info in infos:
                try:
                    raw_name = info.filename.replace("\\", "/")
                    posix_name = PurePosixPath(raw_name)
                    windows_name = PureWindowsPath(info.filename)
                    if (not raw_name or posix_name.is_absolute() or windows_name.is_absolute()
                            or windows_name.drive or any(part in ("..", "") for part in posix_name.parts)):
                        continue
                    mode = (info.external_attr >> 16) & 0xFFFF
                    if stat.S_ISLNK(mode):
                        continue
                    total_size += max(0, int(info.file_size))
                    if total_size > max_uncompressed:
                        raise ValueError("ZIP açılma boyutu güvenlik sınırını aşıyor.")
                    destination = (target / Path(*posix_name.parts)).resolve()
                    destination.relative_to(target)
                    archive.extract(info, target)
                    extracted += 1
                except ValueError:
                    raise
                except Exception as exc:
                    log_error(f"zip member skipped {info.filename!r}: {exc}")
    except Exception as exc:
        log_error(f"zip: {exc}")
    return extracted

LANGS = {"tr":"Türkçe","en":"English","de":"Deutsch","fr":"Français","es":"Español",
         "it":"Italiano","pt":"Português","ru":"Русский","zh":"中文","ja":"日本語","ko":"한국어","ar":"العربية"}

TR = {
    "tagline":"ULTIMATE v12.2","home":"🏠 Ana Sayfa","browse":"🔎 Gözat","library":"📚 Kütüphane",
    "downloads":"⬇ İndirmeler","wishlist":"⭐ İstek","tasks":"🎯 Görevler","profile":"👤 Profil","settings":"⚙ Ayarlar",
    "installed":"Yüklü Oyunlar","installed_count":"({}) Yüklü","credits":"💎 {:,} Kredi",
    "search_ph":"Oyun ara... (Ctrl+K)","daily_wheel":"🎡 Günlük Çark","report":"💬 Hata Bildir / Öneri",
    "hero_tag":"ARDA LAUNCHER v12.2","hero_title":"105+ Ücretsiz Oyun",
    "hero_desc":"Steam kütüphanenle senkronize, GitHub'dan doğrudan indir.",
    "btn_browse":"▶ Gözat","btn_library":"📚 Kütüphane","btn_download":"İndir","btn_cancel":"İptal",
    "btn_pause":"⏸ Duraklat","btn_resume":"▶ Devam","btn_open":"📂 Aç","btn_install":"⬇ Kur",
    "free":"ÜCRETSİZ","mb":"{} MB",
    "featured":"🔥 Öne Çıkanlar","popular":"🎁 Popüler","opensource":"🛠 Açık Kaynak","newest":"🆕 Yeni",
    "found":"{} oyun bulundu","empty_lib":"Henüz oyun yok. Gözat!","no_dl":"Aktif indirme yok.","empty_wish":"İstek listesi boş.",
    "shop":"🛍 Kozmetik Mağazası","insufficient":"Yetersiz Kredi","insufficient_msg":"Bu ürün için {} kredi gerekli.",
    "purchased":"Satın Alma","purchased_msg":"'{}' satın alındı! (-{} 💎)",
    "tab_storage":"Dizin & Depolama","tab_network":"Ağ & İndirme","tab_perf":"Performans",
    "tab_appear":"Görünüm","tab_sound":"Ses & Bildirim","tab_maint":"Bakım",
    "dev_mode_tab":"🛠 Geliştirici Modu",
    "data_dir":"Veri Klasörü","open_folder":"📂 Aç","clear_cache":"🧹 Önbellek Temizle","cache_cleared":"Önbellek temizlendi.",
    "github_repo":"GitHub Repo","network_info":"İndirmeler GitHub'ın herkese açık HTTPS API'si üzerinden yapılır. Gmail/SMTP gerekmez. Depoya dosya göndermek yalnızca geliştirici modunda GitHub tokeni ister.",
    "save":"💾 Kaydet","saved":"Kaydedildi","game_booster":"Game Booster","startup":"Windows başlangıcında çalıştır",
    "language":"Dil","theme":"Tema:","card_size":"Kart Boyutu:","volume":"Ses: {}%","notifications":"Masaüstü bildirimleri",
    "check_update":"🔄 Güncelleme Denetle","create_shortcut":"🖥 Kısayol Oluştur","export_installer":"📤 Installer .bat",
    "backup_json":"💾 JSON Yedek Al","uninstall":"🗑 Tamamen Kaldır",
    "error":"Hata","critical":"Kritik Hata","page_error":"Sayfa hatası: {}",
    "download_start":"İndiriliyor","download_done":"Tamamlandı","download_error":"Hata: {}",
    "download_success":"{} indirildi","download_paused":"Duraklatıldı","download_cancelled":"İptal edildi",
    "download_fail":"İndirme Hatası","steam_start":"Steam Kurulumu","steam_started":"Steam başlatıldı",
    "steam_not_found":"Steam bulunamadı. Kurmak ister misiniz?","steam_install_btn":"Steam'i İndir",
    "steam_already":"Oyun zaten Steam'de kurulu","steam_error":"Steam Hatası",
    "library_added":"Oyun eklendi.","library_title":"Kütüphane","wishlist_added":"Eklendi.","wishlist_removed":"Çıkarıldı.",
    "wheel_title":"🎡 Günlük Çark","wheel_win":"Tebrikler! +{} 💎!","wheel_daily":"Bugün zaten çevirdiniz!",
    "task_login":"Günlük Giriş","task_login_d":"Bugün giriş yap","task_download":"İlk İndirme","task_download_d":"Bir oyun indir",
    "task_librarian":"Kütüphaneci","task_librarian_d":"5 oyun ekle","task_explorer":"Kâşif","task_explorer_d":"3 tür incele",
    "task_social":"Sosyal","task_social_d":"3 istek ekle","task_wheel":"Çark Ustası","task_wheel_d":"Günlük çarkı çevir",
    "profile_stats_lib":"Kütüphane","profile_stats_wish":"İstek","profile_stats_dl":"İndirme","profile_stats_ach":"Başarım",
    "level":"Seviye 1 • Yeni Oyuncu","neon_banner":"🌸 Neon Banner",
    "dev_title":"🔒 Geliştirici Girişi","dev_authorized":"Geliştirici moduna yalnızca şifreyi doğru girenler girebilir.",
    "dev_password_ph":"Şifre","dev_login":"Giriş Yap","dev_forgot":"","dev_wrong":"Hatalı şifre.",
    "dev_already":"Zaten giriş yapılmış.","dev_welcome":"Hoş geldin","dev_active":"Geliştirici modu aktif.",
    "dev_setup_title":"","dev_setup_desc":"",
    "dev_locked":"Çok fazla yanlış deneme. {} dakika bekleyin.",
    "reset_title":"🔑 Şifre Sıfırlama","reset_desc":"E-posta gönderilmez. Bu cihaz için oluşturulan kurtarma anahtarını girin.",
    "reset_send":"Kurtarma anahtarı","reset_code_ph":"Kurtarma anahtarı","reset_new_ph":"Yeni şifre (min 12)",
    "reset_confirm_ph":"Yeni şifreyi tekrar girin","reset_send_first":"Kurtarma anahtarını girin.","reset_wrong":"Kurtarma anahtarı yanlış.","reset_weak":"Şifre güçlü değil veya eşleşmiyor.",
    "reset_done":"Şifre güncellendi!","reset_verify":"✅ Şifreyi Sıfırla","reset_expired":"Kurtarma anahtarı geçersiz.",
    "reset_sent":"Kurtarma anahtarı doğrulandı.",
    "recovery_code_title":"🔐 Yerel Kurtarma Anahtarınız","recovery_code_desc":"Bu anahtarı güvenli bir yere kaydedin. Yalnızca şimdi gösterilir; e-posta veya internet gerekmez.",
    "recovery_copy":"📋 Anahtarı Kopyala","recovery_saved":"Anahtarı kaydettim","recovery_key_ph":"Kurtarma anahtarı",
    "detail_type":"Tür: {}  •  Boyut: {} MB  •  RAM: {} GB","close":"Kapat","ok":"Tamam",
    "add_wish":"⭐ İstek Listesine Ekle","add_lib":"📚 Kütüphaneye Ekle",
}

EN = {
    "tagline":"ULTIMATE v12.2","home":"🏠 Home","browse":"🔎 Browse","library":"📚 Library",
    "downloads":"⬇ Downloads","wishlist":"⭐ Wishlist","tasks":"🎯 Tasks","profile":"👤 Profile","settings":"⚙ Settings",
    "installed":"Installed Games","installed_count":"({}) Installed","credits":"💎 {:,} Credits",
    "search_ph":"Search games... (Ctrl+K)","daily_wheel":"🎡 Daily Spin","report":"💬 Report / Suggest",
    "hero_tag":"ARDA LAUNCHER v12.2","hero_title":"105+ Free Games",
    "hero_desc":"Sync with Steam, download from GitHub.",
    "btn_browse":"▶ Browse","btn_library":"📚 Library","btn_download":"Download","btn_cancel":"Cancel",
    "btn_pause":"⏸ Pause","btn_resume":"▶ Resume","btn_open":"📂 Open","btn_install":"⬇ Install",
    "free":"FREE","mb":"{} MB",
    "featured":"🔥 Featured","popular":"🎁 Popular","opensource":"🛠 Open Source","newest":"🆕 New",
    "found":"{} games found","empty_lib":"No games yet. Browse!","no_dl":"No active downloads.","empty_wish":"Wishlist empty.",
    "shop":"🛍 Cosmetic Shop","insufficient":"Insufficient Credits","insufficient_msg":"You need {} credits.",
    "purchased":"Purchase","purchased_msg":"'{}' purchased! (-{} 💎)",
    "tab_storage":"Directory & Storage","tab_network":"Network & Download","tab_perf":"Performance",
    "tab_appear":"Appearance","tab_sound":"Sound & Notifications","tab_maint":"Maintenance",
    "dev_mode_tab":"🛠 Developer Mode",
    "data_dir":"Data Folder","open_folder":"📂 Open","clear_cache":"🧹 Clear Cache","cache_cleared":"Cache cleared.",
    "github_repo":"GitHub Repo","network_info":"Downloads use GitHub's public HTTPS API. No Gmail or SMTP is required. Uploading repository files requires a GitHub token in Developer Mode.",
    "save":"💾 Save","saved":"Saved","game_booster":"Game Booster","startup":"Run at Windows startup",
    "language":"Language","theme":"Theme:","card_size":"Card Size:","volume":"Volume: {}%","notifications":"Desktop notifications",
    "check_update":"🔄 Check Updates","create_shortcut":"🖥 Create Shortcut","export_installer":"📤 Export Installer",
    "backup_json":"💾 Backup JSON","uninstall":"🗑 Uninstall",
    "error":"Error","critical":"Critical Error","page_error":"Page error: {}",
    "download_start":"Downloading","download_done":"Completed","download_error":"Error: {}",
    "download_success":"{} downloaded","download_paused":"Paused","download_cancelled":"Cancelled",
    "download_fail":"Download Error","steam_start":"Steam Installation","steam_started":"Steam started",
    "steam_not_found":"Steam not found. Install it?","steam_install_btn":"Download Steam",
    "steam_already":"Game already installed in Steam","steam_error":"Steam Error",
    "library_added":"Game added.","library_title":"Library","wishlist_added":"Added.","wishlist_removed":"Removed.",
    "wheel_title":"🎡 Daily Spin","wheel_win":"Congrats! +{} 💎!","wheel_daily":"Already spun today!",
    "task_login":"Daily Login","task_login_d":"Log in today","task_download":"First Download","task_download_d":"Download a game",
    "task_librarian":"Librarian","task_librarian_d":"Add 5 games","task_explorer":"Explorer","task_explorer_d":"Explore 3 genres",
    "task_social":"Social","task_social_d":"Add 3 to wishlist","task_wheel":"Wheel Master","task_wheel_d":"Spin the wheel",
    "profile_stats_lib":"Library","profile_stats_wish":"Wishlist","profile_stats_dl":"Downloads","profile_stats_ach":"Achievements",
    "level":"Level 1 • New Player","neon_banner":"🌸 Neon Banner",
    "dev_title":"🔒 Developer Login","dev_authorized":"Only those who enter the correct password can enter developer mode.",
    "dev_password_ph":"Password","dev_login":"Sign In","dev_forgot":"","dev_wrong":"Incorrect password.",
    "dev_already":"Already logged in.","dev_welcome":"Welcome","dev_active":"Developer mode active.",
    "dev_setup_title":"","dev_setup_desc":"",
    "dev_locked":"Too many attempts. Wait {} minutes.",
    "reset_title":"🔑 Password Reset","reset_desc":"No email is sent. Enter the local recovery key created for this device.",
    "reset_send":"Recovery key","reset_code_ph":"Recovery key","reset_new_ph":"New password (min 12)",
    "reset_confirm_ph":"Confirm new password","reset_send_first":"Enter the recovery key.","reset_wrong":"Incorrect recovery key.","reset_weak":"Password is weak or the entries do not match.",
    "reset_done":"Password updated!","reset_verify":"✅ Reset Password","reset_expired":"Recovery key is invalid.",
    "reset_sent":"Recovery key verified.",
    "recovery_code_title":"🔐 Your Local Recovery Key","recovery_code_desc":"Save this key somewhere safe. It is shown only now; no email or internet is needed.",
    "recovery_copy":"📋 Copy Key","recovery_saved":"I saved the key","recovery_key_ph":"Recovery key",
    "detail_type":"Type: {}  •  Size: {} MB  •  RAM: {} GB","close":"Close","ok":"OK",
    "add_wish":"⭐ Add to Wishlist","add_lib":"📚 Add to Library",
}

PARTIAL_LANGS = {
    "de":{"tagline":"ULTIMATE v12.2","home":"🏠 Startseite","browse":"🔎 Entdecken","library":"📚 Bibliothek",
          "downloads":"⬇ Downloads","wishlist":"⭐ Wunschliste","tasks":"🎯 Aufgaben","profile":"👤 Profil",
          "settings":"⚙ Einstellungen","installed":"Installierte Spiele","btn_download":"Herunterladen",
          "free":"KOSTENLOS","dev_title":"🔒 Entwickler-Login",
          "dev_authorized":"Nur wer das richtige Passwort eingibt, kann den Entwicklermodus betreten.",
          "hero_title":"105+ Kostenlose Spiele","language":"Sprache","add_wish":"⭐ Zur Wunschliste","add_lib":"📚 Zur Bibliothek"},
    "fr":{"tagline":"ÉDITION v12.2","home":"🏠 Accueil","browse":"🔎 Parcourir","library":"📚 Bibliothèque",
          "downloads":"⬇ Téléchargements","wishlist":"⭐ Souhaits","tasks":"🎯 Tâches","profile":"👤 Profil",
          "settings":"⚙ Paramètres","installed":"Jeux installés","btn_download":"Télécharger",
          "free":"GRATUIT","dev_title":"🔒 Connexion développeur",
          "dev_authorized":"Seuls ceux qui saisissent le bon mot de passe peuvent accéder au mode développeur.",
          "hero_title":"105+ Jeux Gratuits","language":"Langue","add_wish":"⭐ Ajouter aux souhaits","add_lib":"📚 Ajouter à la bibliothèque"},
    "es":{"tagline":"EDICIÓN v12.2","home":"🏠 Inicio","browse":"🔎 Explorar","library":"📚 Biblioteca",
          "downloads":"⬇ Descargas","wishlist":"⭐ Deseos","tasks":"🎯 Tareas","profile":"👤 Perfil",
          "settings":"⚙ Ajustes","installed":"Juegos instalados","btn_download":"Descargar",
          "free":"GRATIS","dev_title":"🔒 Acceso desarrollador",
          "dev_authorized":"Solo quienes ingresen la contraseña correcta pueden acceder al modo desarrollador.",
          "hero_title":"105+ Juegos Gratis","language":"Idioma","add_wish":"⭐ Añadir a deseos","add_lib":"📚 Añadir a biblioteca"},
    "it":{"tagline":"EDIZIONE v12.2","home":"🏠 Home","browse":"🔎 Esplora","library":"📚 Libreria",
          "downloads":"⬇ Download","wishlist":"⭐ Desideri","tasks":"🎯 Attività","profile":"👤 Profilo",
          "settings":"⚙ Impostazioni","installed":"Giochi installati","btn_download":"Scarica",
          "free":"GRATIS","dev_title":"🔒 Accesso sviluppatore",
          "dev_authorized":"Solo chi inserisce la password corretta può accedere alla modalità sviluppatore.",
          "hero_title":"105+ Giochi Gratuiti","language":"Lingua","add_wish":"⭐ Aggiungi ai desideri","add_lib":"📚 Aggiungi alla libreria"},
    "pt":{"tagline":"EDIÇÃO v12.2","home":"🏠 Início","browse":"🔎 Explorar","library":"📚 Biblioteca",
          "downloads":"⬇ Downloads","wishlist":"⭐ Desejos","tasks":"🎯 Tarefas","profile":"👤 Perfil",
          "settings":"⚙ Configurações","installed":"Jogos Instalados","btn_download":"Baixar",
          "free":"GRÁTIS","dev_title":"🔒 Login Desenvolvedor",
          "dev_authorized":"Apenas quem inserir a senha correta pode entrar no modo desenvolvedor.",
          "hero_title":"105+ Jogos Grátis","language":"Idioma","add_wish":"⭐ Adicionar aos Desejos","add_lib":"📚 Adicionar à Biblioteca"},
    "ru":{"tagline":"ULTIMATE v12.2","home":"🏠 Главная","browse":"🔎 Обзор","library":"📚 Библиотека",
          "downloads":"⬇ Загрузки","wishlist":"⭐ Желания","tasks":"🎯 Задания","profile":"👤 Профиль",
          "settings":"⚙ Настройки","installed":"Установленные игры","btn_download":"Скачать",
          "free":"БЕСПЛАТНО","dev_title":"🔒 Вход разработчика",
          "dev_authorized":"Только те, кто введёт правильный пароль, могут войти в режим разработчика.",
          "hero_title":"105+ Бесплатных Игр","language":"Язык","add_wish":"⭐ В желания","add_lib":"📚 В библиотеку"},
    "zh":{"tagline":"终极版 v12.2","home":"🏠 首页","browse":"🔎 浏览","library":"📚 库",
          "downloads":"⬇ 下载","wishlist":"⭐ 愿望单","tasks":"🎯 任务","profile":"👤 个人",
          "settings":"⚙ 设置","installed":"已安装游戏","btn_download":"下载","free":"免费",
          "dev_title":"🔒 开发者登录","dev_authorized":"只有输入正确密码的人才能进入开发者模式。",
          "hero_title":"105+ 款免费游戏","language":"语言","add_wish":"⭐ 加入愿望单","add_lib":"📚 加入库"},
    "ja":{"tagline":"v12.2","home":"🏠 ホーム","browse":"🔎 ブラウズ","library":"📚 ライブラリ",
          "downloads":"⬇ ダウンロード","wishlist":"⭐ ウィッシュ","tasks":"🎯 タスク","profile":"👤 プロフィール",
          "settings":"⚙ 設定","installed":"インストール済み","btn_download":"ダウンロード","free":"無料",
          "dev_title":"🔒 開発者ログイン","dev_authorized":"正しいパスワードを入力した人だけが開発者モードに入れます。",
          "hero_title":"105+ 無料ゲーム","language":"言語","add_wish":"⭐ ウィッシュリストに追加","add_lib":"📚 ライブラリに追加"},
    "ko":{"tagline":"v12.2","home":"🏠 홈","browse":"🔎 찾아보기","library":"📚 라이브러리",
          "downloads":"⬇ 다운로드","wishlist":"⭐ 위시","tasks":"🎯 작업","profile":"👤 프로필",
          "settings":"⚙ 설정","installed":"설치된 게임","btn_download":"다운로드","free":"무료",
          "dev_title":"🔒 개발자 로그인","dev_authorized":"올바른 비밀번호를 입력한 사람만 개발자 모드에 들어갈 수 있습니다.",
          "hero_title":"105+ 무료 게임","language":"언어","add_wish":"⭐ 위시리스트에 추가","add_lib":"📚 라이브러리에 추가"},
    "ar":{"tagline":"v12.2","home":"🏠 الرئيسية","browse":"🔎 تصفح","library":"📚 المكتبة",
          "downloads":"⬇ التنزيلات","wishlist":"⭐ الرغبات","tasks":"🎯 المهام","profile":"👤 الملف",
          "settings":"⚙ الإعدادات","installed":"الألعاب المثبتة","btn_download":"تحميل","free":"مجاني",
          "dev_title":"🔒 دخول المطور","dev_authorized":"فقط من يدخل كلمة المرور الصحيحة يمكنه الدخول إلى وضع المطور.",
          "hero_title":"أكثر من 105 لعبة مجانية","language":"اللغة","add_wish":"⭐ أضف إلى الرغبات","add_lib":"📚 أضف إلى المكتبة"},
}
TRANSLATIONS = {"tr": TR, "en": EN}
for c, p in PARTIAL_LANGS.items():
    m = dict(EN); m.update(p); TRANSLATIONS[c] = m

def detect_language():
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        p = lid & 0x3FF
        m = {0x1F:"tr",0x09:"en",0x07:"de",0x0C:"fr",0x0A:"es",0x10:"it",
             0x16:"pt",0x19:"ru",0x04:"zh",0x11:"ja",0x12:"ko",0x01:"ar"}
        if p in m: return m[p]
    except: pass
    try:
        import locale; l = locale.getdefaultlocale()[0]
        if l and l[:2].lower() in LANGS: return l[:2].lower()
    except: pass
    return "en"

_GH, _ST, _WEB = "github", "steam", "web"
RAW_CATALOG = [
    ("mindustry","Mindustry","1127400",_GH,"Anuken/Mindustry",250,2,"Kule savunma"),
    ("wesnoth","Battle for Wesnoth","599390",_GH,"wesnoth/wesnoth",400,2,"Strateji"),
    ("endless-sky","Endless Sky","404410",_GH,"endless-sky/endless-sky",300,2,"Uzay"),
    ("shattered-pd","Shattered Pixel Dungeon","1769170",_GH,"00-Evan/shattered-pixel-dungeon",80,1,"Roguelike"),
    ("openttd","OpenTTD","1536610",_GH,"OpenTTD/OpenTTD",200,1,"Ulaşım"),
    ("warzone2100","Warzone 2100","1241950",_GH,"Warzone2100/warzone2100",600,2,"RTS"),
    ("cataclysm-dda","Cataclysm: DDA","2330750",_GH,"CleverRaven/Cataclysm-DDA",400,2,"Hayatta"),
    ("tome4","Tales of Maj'Eyal","259680",_GH,"tome4/tome",800,2,"RPG"),
    ("ddnet","DDNet","380840",_GH,"ddnet/ddnet",200,1,"2D"),
    ("cs2","Counter-Strike 2","730",_ST,"",50,8,"FPS"),
    ("dota2","Dota 2","570",_ST,"",50,8,"MOBA"),
    ("pubg","PUBG","578080",_ST,"",50,16,"BR"),
    ("apex","Apex Legends","1172470",_ST,"",80,8,"BR"),
    ("warframe","Warframe","230410",_ST,"",50,6,"Aksiyon"),
    ("tf2","Team Fortress 2","440",_ST,"",30,2,"FPS"),
    ("warthunder","War Thunder","236390",_ST,"",95,16,"Araç"),
    ("destiny2","Destiny 2","1085660",_ST,"",100,8,"FPS RPG"),
    ("halo-infinite","Halo Infinite","1240440",_ST,"",50,8,"FPS"),
    ("sims4","The Sims 4","1222670",_ST,"",30,4,"Yaşam"),
    ("unturned","Unturned","304930",_ST,"",2,4,"Zombi"),
    ("poe","Path of Exile","238960",_ST,"",40,8,"ARPG"),
    ("overwatch2","Overwatch 2","2357570",_ST,"",50,6,"FPS"),
    ("wot","World of Tanks","1407200",_ST,"",70,6,"Tank"),
    ("wows","World of Warships","552990",_ST,"",50,6,"Gemi"),
    ("marvel-rivals","Marvel Rivals","2767030",_ST,"",70,16,"FPS"),
    ("trackmania","Trackmania","2225070",_ST,"",20,4,"Yarış"),
    ("brawlhalla","Brawlhalla","291550",_ST,"",1,2,"Dövüş"),
    ("paladins","Paladins","444090",_ST,"",20,4,"FPS"),
    ("smite","SMITE","386360",_ST,"",30,4,"MOBA"),
    ("lostark","Lost Ark","1599340",_ST,"",90,8,"MMO"),
    ("albion","Albion Online","761890",_ST,"",10,4,"MMO"),
    ("runescape","RuneScape","1343400",_ST,"",20,2,"MMO"),
    ("osrs","Old School RuneScape","1343370",_ST,"",20,2,"MMO"),
    ("yugioh","Yu-Gi-Oh!","1449850",_ST,"",20,4,"Kart"),
    ("marvel-snap","Marvel Snap","1997040",_ST,"",5,4,"Kart"),
    ("efootball","eFootball","1665460",_ST,"",40,8,"Futbol"),
    ("asphalt","Asphalt Legends","1815780",_ST,"",30,4,"Yarış"),
    ("stumble","Stumble Guys","1677740",_ST,"",5,4,"Parti"),
    ("dcs","DCS World","223750",_ST,"",100,16,"Uçuş"),
    ("fallout-shelter","Fallout Shelter","588430",_ST,"",2,2,"Yönetim"),
    ("vrchat","VRChat","438100",_ST,"",20,8,"VR"),
    ("aimlabs","Aimlabs","714010",_ST,"",5,4,"Nişan"),
    ("once-human","Once Human","2139460",_ST,"",50,16,"Hayatta"),
    ("delta-force","Delta Force","2507950",_ST,"",50,16,"FPS"),
    ("naraka","Naraka","1203220",_ST,"",50,8,"Dövüş"),
    ("the-finals","The Finals","2073850",_ST,"",50,12,"FPS"),
    ("enlisted","Enlisted","2051620",_ST,"",40,8,"WW2"),
    ("crossout","Crossout","386180",_ST,"",30,4,"Araç"),
    ("star-conflict","Star Conflict","212070",_ST,"",15,4,"Uzay"),
    ("fishing-planet","Fishing Planet","380600",_ST,"",15,4,"Balık"),
    ("planetside2","PlanetSide 2","218230",_ST,"",50,8,"FPS"),
    ("eve","EVE Online","8500",_ST,"",30,4,"Uzay"),
    ("trove","Trove","304050",_ST,"",10,4,"MMO"),
    ("gw2","Guild Wars 2","1284210",_ST,"",50,8,"MMO"),
    ("swtor","SWTOR","1286830",_ST,"",50,4,"MMO"),
    ("lotro","LOTRO","212500",_ST,"",30,4,"MMO"),
    ("neverwinter","Neverwinter","109600",_ST,"",30,4,"MMO"),
    ("sto","Star Trek Online","9900",_ST,"",20,4,"Uzay"),
    ("dcuo","DCUO","24200",_ST,"",30,4,"MMO"),
    ("maplestory","MapleStory","216150",_ST,"",10,2,"2D"),
    ("bdo","Black Desert","582660",_ST,"",80,8,"MMO"),
    ("throne-liberty","Throne and Liberty","2429640",_ST,"",70,16,"MMO"),
    ("tof","Tower of Fantasy","2064650",_ST,"",50,8,"RPG"),
    ("honkai3","Honkai Impact 3rd","1671200",_ST,"",30,8,"ARPG"),
    ("limbus","Limbus Company","1973530",_ST,"",15,4,"RPG"),
    ("shadowverse","Shadowverse","453480",_ST,"",10,4,"Kart"),
    ("gwent","Gwent","1284410",_ST,"",10,4,"Kart"),
    ("mtga","MTG Arena","2141910",_ST,"",10,4,"Kart"),
    ("eternal","Eternal","531640",_ST,"",10,4,"Kart"),
    ("conqueror-blade","Conqueror's Blade","835570",_ST,"",40,8,"Savaş"),
    ("mwo","MechWarrior Online","342200",_ST,"",20,4,"Mech"),
    ("hawken","Hawken","705040",_ST,"",20,8,"Mech"),
    ("ironsight","Ironsight","783770",_ST,"",20,8,"FPS"),
    ("combat-master","Combat Master","2281730",_ST,"",10,8,"FPS"),
    ("krunker","Krunker","1408720",_ST,"",1,2,"FPS"),
    ("pixel-strike","Pixel Strike 3D","1113120",_ST,"",5,4,"FPS"),
    ("goose-duck","Goose Goose Duck","1568590",_ST,"",2,4,"Sosyal"),
    ("rec-room","Rec Room","471710",_ST,"",5,4,"VR"),
    ("banana","Banana","2923300",_ST,"",1,2,"Klik"),
    ("cats","Cats","2977660",_ST,"",1,2,"Kedi"),
    ("adv-capitalist","AdVenture Capitalist","346900",_ST,"",1,2,"Boşta"),
    ("cells-singularity","Cells to Singularity","977400",_ST,"",1,2,"Evrim"),
    ("rotmg","Realm of the Mad God","200210",_ST,"",1,2,"MMO"),
    ("spiral-knights","Spiral Knights","99900",_ST,"",2,2,"MMO"),
    ("elsword","Elsword","237310",_ST,"",5,4,"MMO"),
    ("grandchase","GrandChase","985810",_ST,"",5,4,"RPG"),
    ("kurtzpel","KurtzPel","844870",_ST,"",15,8,"Aksiyon"),
    ("closers","Closers","215830",_ST,"",10,4,"MMO"),
    ("soulworker","SoulWorker","1377580",_ST,"",15,8,"MMO"),
    ("auto-chess","Auto Chess","1097130",_ST,"",5,4,"Satranç"),
    ("ddlc","DDLC","698780",_ST,"",1,2,"Roman"),
    ("cry-of-fear","Cry of Fear","223710",_ST,"",2,2,"Korku"),
    ("nmrih","No More Room in Hell","224260",_ST,"",5,4,"Zombi"),
    ("asrd","Alien Swarm","563560",_ST,"",5,4,"Shooter"),
    ("sven","Sven Co-op","225840",_ST,"",5,4,"Co-op"),
    ("fof","Fistful of Frags","265630",_ST,"",2,2,"Western"),
    ("cure","Codename CURE","355180",_ST,"",5,4,"Co-op"),
    ("deceit","Deceit","466240",_ST,"",10,4,"Çıkarım"),
    ("deceit2","Deceit 2","2064870",_ST,"",15,8,"Çıkarım"),
    ("muck","Muck","1625450",_ST,"",1,4,"Hayatta"),
    ("crab-game","Crab Game","1782210",_ST,"",1,4,"Parti"),
    ("among-us","Among Us","843380",_ST,"",1,4,"Çıkarım"),
    ("farlight","Farlight 84","1928420",_ST,"",20,8,"BR"),
    ("bloodhunt","Bloodhunt","760160",_ST,"",20,8,"Vampir"),
    ("rogue-company","Rogue Company","872200",_ST,"",15,8,"FPS"),
    ("splitgate","Splitgate","677620",_ST,"",15,8,"Portal"),
    ("quake-champions","Quake Champions","611500",_ST,"",20,8,"Arena"),
    ("tribes3","Tribes 3","2687970",_ST,"",20,8,"Arena"),
    ("stormgate","Stormgate","2012510",_ST,"",20,8,"RTS"),
    ("battle-aces","Battle Aces","2682180",_ST,"",10,8,"RTS"),
    ("zero-k","Zero-K","334920",_ST,"",5,4,"RTS"),
    ("bar","Beyond All Reason","0",_WEB,"",20,8,"RTS"),
    ("rf4","Russian Fishing 4","766570",_ST,"",20,4,"Balık"),
    ("hunter-classic","theHunter Classic","253710",_ST,"",15,4,"Avcılık"),
    ("cotw-angler","CotW Angler","1408610",_ST,"",20,4,"Balık"),
]

class Game:
    __slots__ = ("gid","name","appid","kind","repo","size_mb","ram_gb","desc")
    def __init__(self, t):
        (self.gid, self.name, self.appid, self.kind, self.repo,
         self.size_mb, self.ram_gb, self.desc) = t

GAMES = [Game(t) for t in RAW_CATALOG]
GAME_MAP = {g.gid: g for g in GAMES}

def find_steam_path():
    if winreg is None: return None
    for root, sub in [(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                      (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")]:
        try:
            k = winreg.OpenKey(root, sub)
        except: continue
        try:
            for name in ("SteamPath","InstallPath"):
                try:
                    v, _ = winreg.QueryValueEx(k, name)
                    p = Path(v)
                    if p.exists():
                        winreg.CloseKey(k)
                        return p
                except: pass
        finally:
            try: winreg.CloseKey(k)
            except: pass
    for guess in [Path("C:/Program Files (x86)/Steam"), Path("C:/Program Files/Steam")]:
        if guess.exists(): return guess
    return None

def is_steam_installed(appid):
    sp = find_steam_path()
    if not sp: return False
    return (sp / "steamapps" / f"appmanifest_{appid}.acf").exists()

def launch_steam_install(appid):
    try:
        os.startfile(f"steam://install/{appid}")
        return True, None
    except Exception as e:
        return False, str(e)

_cover_mem = {}
def fetch_cover(game, cb):
    key = game.gid
    if key in _cover_mem:
        try: cb(_cover_mem[key]); return
        except: pass
    cached = COVERS_DIR / f"{game.gid}.jpg"
    if cached.exists() and cached.stat().st_size > 3000:
        try:
            img = Image.open(cached); img.load()
            _cover_mem[key] = img; cb(img); return
        except: pass
    def worker():
        urls = []
        for cdn in STEAM_CDNS:
            urls += [f"{cdn}/steam/apps/{game.appid}/library_600x900.jpg",
                     f"{cdn}/steam/apps/{game.appid}/header.jpg",
                     f"{cdn}/steam/apps/{game.appid}/capsule_616x353.jpg"]
        for u in urls:
            try:
                with requests.get(u, timeout=(4, 8), headers={"User-Agent":"Mozilla/5.0"},
                                  allow_redirects=True) as response:
                    if response.status_code != 200 or len(response.content) <= 3000:
                        continue
                    image_bytes = response.content
                with open(cached, "wb") as f:
                    f.write(image_bytes)
                img = Image.open(cached); img.load()
                _cover_mem[key] = img; cb(img); return
            except Exception:
                continue
        cb(None)
    threading.Thread(target=worker, daemon=True).start()

class DownloadTask:
    def __init__(self, game, dest_dir=None):
        self.game = game
        self.dest_dir = Path(dest_dir) if dest_dir else DOWNLOADS_DIR
        self.filename = None; self.url = None
        self.total = 0; self.downloaded = 0; self.speed = 0
        self.state = "idle"; self.error = None
        self.paused = False; self.cancelled = False
        self.thread = None; self.on_update = None
        self._last_t = 0; self._last_b = 0

    def resolve(self):
        try:
            if not self.game.repo or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.game.repo):
                return False, "Geçersiz GitHub depo adresi"
            response = requests.get(
                f"https://api.github.com/repos/{self.game.repo}/releases/latest",
                timeout=(8, 20),
                headers={"User-Agent":"ArdaLauncher/12.2", "Accept":"application/vnd.github+json"},
            )
            try:
                if response.status_code in (403, 429):
                    reset = response.headers.get("X-RateLimit-Reset", "bilinmiyor")
                    return False, f"GitHub API limiti aşıldı. Sıfırlanma zamanı: {reset}"
                if response.status_code == 404:
                    return False, f"Repo/release bulunamadı: {self.game.repo}"
                if response.status_code != 200:
                    return False, f"GitHub API: HTTP {response.status_code}"
                payload = response.json()
            finally:
                response.close()
            assets = payload.get("assets", []) if isinstance(payload, dict) else []
            if not isinstance(assets, list) or not assets:
                return False, "Bu GitHub deposunda indirilebilir release dosyası yok"
            valid = []
            for asset in assets:
                if not isinstance(asset, dict):
                    continue
                name = str(asset.get("name", ""))
                url = str(asset.get("browser_download_url", ""))
                if not re.search(r"\.(zip|7z|exe)$", name, re.I):
                    continue
                parsed = urlparse(url)
                if parsed.scheme != "https" or parsed.hostname != "github.com":
                    continue
                if re.search(r"(win|windows|x86_64|amd64)", name, re.I):
                    valid.insert(0, asset)
                else:
                    valid.append(asset)
            if not valid:
                return False, "İndirilebilir güvenli Windows release dosyası bulunamadı"
            asset = valid[0]
            filename = str(asset.get("name", ""))
            filename = filename.replace("\\", "/").split("/")[-1]
            if not filename or filename in (".", "..") or ".." in filename:
                return False, "Release dosya adı güvenli değil"
            self.url = str(asset.get("browser_download_url", ""))
            self.filename = filename
            try: self.total = max(0, int(asset.get("size", 0)))
            except (TypeError, ValueError): self.total = 0
            return True, None
        except requests.exceptions.Timeout:
            return False, "GitHub API zaman aşımı"
        except requests.exceptions.RequestException as exc:
            return False, f"Ağ bağlantısı hatası: {exc}"
        except (ValueError, TypeError, KeyError) as exc:
            return False, f"GitHub release verisi okunamadı: {exc}"
        except Exception as exc:
            return False, str(exc)

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True); self.thread.start()

    def _notify(self):
        if self.on_update:
            try: self.on_update(self)
            except Exception as e: log_error(f"notify: {e}")

    def _run(self):
        response = None
        try:
            self.state = "resolving"
            self._notify()
            if not self.url:
                ok, error = self.resolve()
                if not ok:
                    self.state, self.error = "error", error
                    self._notify()
                    log_error(f"resolve {self.game.gid}: {error}")
                    return

            parsed = urlparse(self.url)
            if parsed.scheme != "https" or parsed.hostname != "github.com":
                raise ValueError("Yalnızca HTTPS GitHub release adreslerine izin verilir.")
            if not self.filename or Path(self.filename).name != self.filename:
                raise ValueError("Geçersiz hedef dosya adı.")

            self.dest_dir.mkdir(parents=True, exist_ok=True)
            dest = self.dest_dir / self.filename
            part = self.dest_dir / (self.filename + ".part")
            if dest.exists() and (self.total <= 0 or dest.stat().st_size == self.total):
                self.downloaded = dest.stat().st_size
                self.state = "done"
                self._notify()
                return

            existing = part.stat().st_size if part.exists() else 0
            headers = {"User-Agent":"ArdaLauncher/12.2"}
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"
            self.state = "downloading"
            self._notify()
            response = requests.get(self.url, stream=True, headers=headers,
                                    timeout=(15, 45), allow_redirects=True)

            # A range request can return 416 for a complete or stale partial file.
            if response.status_code == 416:
                match = re.search(r"bytes \*/(\d+)", response.headers.get("Content-Range", ""))
                expected = int(match.group(1)) if match else self.total
                response.close()
                response = None
                if part.exists() and expected > 0 and part.stat().st_size == expected:
                    os.replace(part, dest)
                    self.downloaded = expected
                    self.state = "done"
                    self._notify()
                    return
                try: part.unlink()
                except FileNotFoundError: pass
                existing = 0
                headers.pop("Range", None)
                response = requests.get(self.url, stream=True, headers=headers,
                                        timeout=(15, 45), allow_redirects=True)

            final = urlparse(response.url)
            allowed_hosts = {"github.com", "objects.githubusercontent.com",
                             "release-assets.githubusercontent.com", "github-releases.githubusercontent.com"}
            if final.scheme != "https" or final.hostname not in allowed_hosts:
                raise ValueError("İndirme yönlendirmesi güvenli olmayan bir adrese gidiyor.")
            if response.status_code not in (200, 206):
                raise requests.HTTPError(f"HTTP {response.status_code}")

            append_mode = existing > 0 and response.status_code == 206
            if append_mode:
                content_range = response.headers.get("Content-Range", "")
                range_match = re.match(r"bytes (\d+)-(\d+)/(\d+|\*)", content_range)
                if not range_match or int(range_match.group(1)) != existing:
                    response.close()
                    response = requests.get(self.url, stream=True,
                        headers={"User-Agent":"ArdaLauncher/12.2"},
                        timeout=(15, 45), allow_redirects=True)
                    append_mode = False
                    fallback_url = urlparse(response.url)
                    if fallback_url.scheme != "https" or fallback_url.hostname not in allowed_hosts:
                        raise ValueError("Yeniden başlatılan indirme güvenli olmayan bir adrese yönlendirildi.")
                    if response.status_code != 200:
                        raise requests.HTTPError(f"Resume fallback HTTP {response.status_code}")
            if not append_mode:
                existing = 0
            self.downloaded = existing
            if self.total <= 0:
                try:
                    length = int(response.headers.get("Content-Length", "0"))
                    self.total = existing + max(0, length)
                except (TypeError, ValueError):
                    self.total = 0
            self._last_t = time.time()
            self._last_b = existing
            mode = "ab" if append_mode else "wb"
            with open(part, mode) as output:
                for chunk in response.iter_content(chunk_size=128 * 1024):
                    if self.cancelled:
                        self.state = "cancelled"
                        self._notify()
                        try: part.unlink()
                        except OSError: pass
                        return
                    while self.paused and not self.cancelled:
                        time.sleep(0.15)
                    if self.cancelled:
                        self.state = "cancelled"
                        self._notify()
                        try: part.unlink()
                        except OSError: pass
                        return
                    if not chunk:
                        continue
                    output.write(chunk)
                    self.downloaded += len(chunk)
                    now = time.time()
                    if now - self._last_t >= 0.75:
                        elapsed = max(now - self._last_t, 0.001)
                        self.speed = (self.downloaded - self._last_b) / elapsed
                        self._last_t, self._last_b = now, self.downloaded
                        self._notify()
                output.flush()
                os.fsync(output.fileno())

            if self.total > 0 and self.downloaded != self.total:
                self.state = "error"
                self.error = f"Eksik indirme: {self.downloaded}/{self.total} bayt. Yeniden deneyebilirsiniz."
                self._notify()
                return
            os.replace(part, dest)
            self.speed = 0
            self.state = "done"
            self._notify()
        except requests.exceptions.Timeout:
            self.state, self.error = "error", "İndirme zaman aşımına uğradı. Kısmi dosya korunuyor."
            self._notify()
        except requests.exceptions.RequestException as exc:
            self.state, self.error = "error", f"Ağ/HTTP hatası: {exc}"
            log_error(f"download {self.game.gid}: {exc}")
            self._notify()
        except Exception as exc:
            self.state, self.error = "error", str(exc)
            log_error(f"download {self.game.gid}: {exc}")
            self._notify()
        finally:
            if response is not None:
                try: response.close()
                except Exception: pass

    def pause(self):
        if self.state == "downloading":
            self.paused = True
            self.state = "paused"
            self._notify()

    def resume(self):
        if self.state == "paused":
            self.paused = False
            self.state = "downloading"
            self._notify()

    def cancel(self):
        self.cancelled = True
        self.paused = False
        self._notify()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
C_BG="#0B0E14"; C_PANEL="#131823"; C_PANEL2="#1A2030"
C_NEON="#00C8FF"; C_PURPLE="#7C3AED"; C_GOLD="#FFB800"
C_TEXT="#E6EAF2"; C_MUTED="#8892A6"; C_ERR="#FF4D6D"; C_OK="#22C55E"

class ArdaLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1440x900"); self.minsize(1000, 650)
        self.configure(fg_color=C_BG)
        try:
            if not ICON_FILE.exists():
                sz=256; img=Image.new("RGBA",(sz,sz),(0,0,0,0)); d=ImageDraw.Draw(img)
                d.rounded_rectangle([10,10,sz-10,sz-10], radius=48, fill=(4,7,20,255))
                for r,c,w in [(95,(0,200,255,255),4),(78,(150,60,255,255),3)]:
                    d.ellipse([sz//2-r,sz//2-r,sz//2+r,sz//2+r], outline=c, width=w)
                cx,cy=sz//2,sz//2
                d.polygon([(cx,cy-70),(cx+22,cy-22),(cx+70,cy),(cx+22,cy+22),
                          (cx,cy+70),(cx-22,cy+22),(cx-70,cy),(cx-22,cy-22)], fill=(180,230,255,255))
                img.save(ICON_FILE, format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
            self.iconbitmap(str(ICON_FILE))
        except: pass
        try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Arda.Launcher.12")
        except: pass

        # ⭐ KRİTİK: Toplevel referansları burada tutulur
        self._top_windows = []

        self.settings = load_json(SETTINGS_FILE, {})
        if not isinstance(self.settings, dict):
            self.settings = {}
        defaults = {"username":"Player", "tag":"0001", "credits":10000,
                    "language":detect_language(), "theme":"dark", "card_size":"medium",
                    "volume":70, "notifications":True, "boost":False, "startup":False,
                    "last_wheel":None}
        for key, value in defaults.items():
            self.settings.setdefault(key, value)
        # This build uses a fixed, compiled PBKDF2 verifier; remove legacy password/mail fields.
        for obsolete_key in ("smtp_enc", "cloud_url", "dev_hash", "recovery_hash",
                             "recovery_notice_enc", "recovery_notice_pending"):
            self.settings.pop(obsolete_key, None)
        if self.settings.get("language") not in LANGS:
            self.settings["language"] = "en"
        if self.settings.get("theme") not in ("dark", "light", "system"):
            self.settings["theme"] = "dark"
        ctk.set_appearance_mode(self.settings["theme"])
        if self.settings.get("card_size") not in ("small", "medium", "large"):
            self.settings["card_size"] = "medium"
        try: self.settings["credits"] = min(2_000_000_000, max(0, int(self.settings.get("credits", 0))))
        except (TypeError, ValueError, OverflowError): self.settings["credits"] = 0
        try: self.settings["volume"] = min(100, max(0, int(self.settings.get("volume", 70))))
        except (TypeError, ValueError): self.settings["volume"] = 70
        self.settings["username"] = str(self.settings.get("username") or "Player")[:24]
        self.settings["tag"] = str(self.settings.get("tag") or "0001")[:12]

        self.library = load_json(LIBRARY_FILE, [])
        if not isinstance(self.library, list): self.library = []
        self.library = list(dict.fromkeys(gid for gid in self.library if isinstance(gid, str) and gid in GAME_MAP))
        self.wishlist = load_json(WISHLIST_FILE, [])
        if not isinstance(self.wishlist, list): self.wishlist = []
        self.wishlist = list(dict.fromkeys(gid for gid in self.wishlist if isinstance(gid, str) and gid in GAME_MAP))
        self.dl_log = load_json(DOWNLOAD_LOG_FILE, {})
        if not isinstance(self.dl_log, dict): self.dl_log = {}
        self.dl_log = {gid: (info if isinstance(info, dict) else {})
                       for gid, info in self.dl_log.items() if isinstance(gid, str) and gid in GAME_MAP}
        self.download_tasks = {}
        self.lockout = load_json(SECURITY_LOCKOUT_FILE, {})
        if not isinstance(self.lockout, dict): self.lockout = {}
        for key in ("fails", "recovery_fails"):
            try: self.lockout[key] = min(5, max(0, int(self.lockout.get(key, 0) or 0)))
            except (TypeError, ValueError): self.lockout[key] = 0
        for key in ("until", "recovery_until"):
            try: self.lockout[key] = max(0.0, float(self.lockout.get(key, 0) or 0))
            except (TypeError, ValueError): self.lockout[key] = 0.0
        save_json(SETTINGS_FILE, self.settings)
        # Remove legacy mail credentials from the fallback copy too.
        settings_backup = Path(str(SETTINGS_FILE) + ".bak")
        try:
            if settings_backup.exists():
                with settings_backup.open("r", encoding="utf-8") as backup_file:
                    backup_settings = json.load(backup_file)
                if isinstance(backup_settings, dict):
                    changed = False
                    for obsolete_key in ("smtp_enc", "cloud_url", "dev_hash", "recovery_hash", "recovery_notice_enc", "recovery_notice_pending"):
                        if obsolete_key in backup_settings:
                            backup_settings.pop(obsolete_key, None)
                            changed = True
                    if changed:
                        backup_tmp = Path(str(settings_backup) + ".tmp")
                        with backup_tmp.open("w", encoding="utf-8") as backup_file:
                            json.dump(backup_settings, backup_file, ensure_ascii=False, indent=2)
                            backup_file.flush()
                            os.fsync(backup_file.fileno())
                        os.replace(backup_tmp, settings_backup)
        except Exception as exc:
            log_error(f"legacy settings backup cleanup: {exc}")
        save_json(SECURITY_LOCKOUT_FILE, self.lockout)
        self._ui_events = queue.Queue()
        self._ui_poll_id = None
        self._closing = False
        self.current_page = "home"
        self.nav_history = ["home"]; self.nav_index = 0
        self.search_query = ""
        self._logo_clicks=0; self._logo_t=0
        self._dev_verified=False
        self._github_token_session = ""
        self._github_busy = False
        self._hero_job=None
        self._shortcuts_bound=False
        self._lang = self.settings["language"]
        self.title(f"ARDA LAUNCHER v{APP_VERSION} {self.t('tagline')}")
        self._build_layout()
        self._bind_shortcuts()
        self.show_page("home")
        self._ui_poll_id = self.after(100, self._drain_ui_events)

    def _post_ui(self, callback):
        """Queue UI work so worker threads never call Tk/CustomTkinter directly."""
        try:
            if self._closing:
                return
            self._ui_events.put_nowait(callback)
        except Exception as exc:
            log_error(f"ui queue: {exc}")

    def _drain_ui_events(self):
        try:
            processed = 0
            while processed < 100:
                callback = self._ui_events.get_nowait()
                try: callback()
                except Exception as exc: log_error(f"ui callback: {exc}")
                processed += 1
        except queue.Empty:
            pass
        except Exception as exc:
            log_error(f"ui event pump: {exc}")
        try:
            if self.winfo_exists():
                self._ui_poll_id = self.after(100, self._drain_ui_events)
        except Exception:
            self._ui_poll_id = None

    def _show_window(self, win):
        """Toplevel pencereyi GC'den koru + kapanınca listeden sil."""
        self._top_windows.append(win)
        def _close():
            try: self._top_windows.remove(win)
            except: pass
            try: win.destroy()
            except: pass
        try: win.protocol("WM_DELETE_WINDOW", _close)
        except: pass
        try: win.transient(self)
        except: pass
        return win

    def t(self, key, *args, **kwargs):
        lang = self._lang if self._lang in TRANSLATIONS else "en"
        s = TRANSLATIONS.get(lang, {}).get(key) or TRANSLATIONS["en"].get(key, key)
        if args or kwargs:
            try: s = s.format(*args, **kwargs)
            except: pass
        return s

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=C_PANEL, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew"); self.sidebar.grid_propagate(False)
        self._build_sidebar()
        right = ctk.CTkFrame(self, fg_color=C_BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1); right.grid_columnconfigure(0, weight=1)
        self.topbar = ctk.CTkFrame(right, height=64, fg_color=C_PANEL, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew"); self.topbar.grid_propagate(False)
        self._build_topbar()
        self.content = ctk.CTkFrame(right, fg_color=C_BG, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1); self.content.grid_columnconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(self.content, fg_color=C_BG, corner_radius=0)
        self.scroll.grid(row=0, column=0, sticky="nsew")

    def _build_sidebar(self):
        lf = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        lf.pack(fill="x", padx=16, pady=(20,10))
        self.logo_lbl = ctk.CTkLabel(lf, text="⚡ ARDA\nLAUNCHER",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=C_NEON, justify="left")
        self.logo_lbl.pack(anchor="w")
        self.logo_lbl.bind("<Button-1>", self._on_logo_click)
        ctk.CTkLabel(lf, text=f"v{APP_VERSION} • {self.t('tagline')}",
                     font=ctk.CTkFont(size=9), text_color=C_MUTED).pack(anchor="w")
        navs = [("home",self.t("home")),("browse",self.t("browse")),("library",self.t("library")),
                ("downloads",self.t("downloads")),("wishlist",self.t("wishlist")),
                ("tasks",self.t("tasks")),("profile",self.t("profile")),("settings",self.t("settings"))]
        self.nav_buttons = {}
        nf = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nf.pack(fill="x", padx=8, pady=6)
        for pid, lbl in navs:
            b = ctk.CTkButton(nf, text=lbl, anchor="w", height=36, fg_color="transparent",
                hover_color=C_PANEL2, text_color=C_TEXT, font=ctk.CTkFont(size=13),
                command=lambda p=pid: self.show_page(p))
            b.pack(fill="x", pady=1); self.nav_buttons[pid]=b
        ctk.CTkLabel(self.sidebar, text=self.t("installed"),
            font=ctk.CTkFont(size=11, weight="bold"), text_color=C_MUTED).pack(anchor="w", padx=20, pady=(12,4))
        self.installed_lbl = ctk.CTkLabel(self.sidebar,
            text=self.t("installed_count", len(self.library)),
            font=ctk.CTkFont(size=12), text_color=C_NEON)
        self.installed_lbl.pack(anchor="w", padx=20)
        self.installed_list = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.installed_list.pack(fill="both", expand=True, padx=8, pady=(4,8))
        self._refresh_installed_list()
        pc = ctk.CTkFrame(self.sidebar, fg_color=C_PANEL2, corner_radius=12)
        pc.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(pc, text="🎮", width=40, height=40, fg_color=C_PURPLE,
                     corner_radius=20, font=ctk.CTkFont(size=18)).pack(side="left", padx=8, pady=8)
        info = ctk.CTkFrame(pc, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=4)
        ctk.CTkLabel(info, text=f"{self.settings['username']}#{self.settings['tag']}",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=C_TEXT).pack(anchor="w")
        self.credit_lbl = ctk.CTkLabel(info, text=self.t("credits", self.settings['credits']),
            font=ctk.CTkFont(size=11), text_color=C_GOLD)
        self.credit_lbl.pack(anchor="w")

    def _refresh_installed_list(self):
        if not hasattr(self, "installed_list"): return
        try:
            if not self.installed_list.winfo_exists(): return
        except: return
        for w in self.installed_list.winfo_children(): w.destroy()
        for gid in self.library[:6]:
            g = GAME_MAP.get(gid)
            if not g: continue
            lbl = ctk.CTkLabel(self.installed_list, text=f"• {g.name[:22]}",
                font=ctk.CTkFont(size=11), text_color=C_TEXT, anchor="w", cursor="hand2")
            lbl.pack(fill="x", padx=8, pady=1)
            lbl.bind("<Button-1>", lambda e, gg=g: self._open_game_detail(gg))

    def _build_topbar(self):
        self.topbar.grid_columnconfigure(4, weight=1)
        ctk.CTkButton(self.topbar, text="<", width=36, height=36, fg_color=C_PANEL2,
            hover_color=C_NEON, text_color=C_TEXT, command=self._nav_back).grid(row=0, column=0, padx=(16,4), pady=14)
        ctk.CTkButton(self.topbar, text=">", width=36, height=36, fg_color=C_PANEL2,
            hover_color=C_NEON, text_color=C_TEXT, command=self._nav_forward).grid(row=0, column=1, padx=4, pady=14)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.topbar, textvariable=self.search_var,
            placeholder_text=self.t("search_ph"), width=320, height=36,
            fg_color=C_PANEL2, border_color=C_NEON, text_color=C_TEXT)
        self.search_entry.grid(row=0, column=2, padx=12, pady=14)
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())
        ctk.CTkLabel(self.topbar, text=f"⬇ {len(self.dl_log)}", width=60,
            font=ctk.CTkFont(size=13), text_color=C_NEON).grid(row=0, column=3, padx=6)
        ctk.CTkButton(self.topbar, text=self.t("daily_wheel"), width=140, height=36,
            fg_color=C_PURPLE, hover_color=C_NEON, command=self._daily_wheel
        ).grid(row=0, column=4, padx=6, pady=14, sticky="e")
        ctk.CTkButton(self.topbar, text="⚙", width=36, height=36, fg_color=C_PANEL2,
            hover_color=C_NEON, command=lambda: self.show_page("settings")
        ).grid(row=0, column=5, padx=4)
        ctk.CTkButton(self.topbar, text=self.t("report"), width=190, height=36,
            fg_color=C_GOLD, text_color="#000", hover_color="#FFD34D",
            command=lambda: webbrowser.open(FEEDBACK_URL)
        ).grid(row=0, column=6, padx=(6,16))

    def _bind_shortcuts(self):
        if self._shortcuts_bound: return
        self.bind_all("<Control-k>", lambda e: self.search_entry.focus_set() if hasattr(self,"search_entry") else None)
        self.bind_all("<Control-K>", lambda e: self.search_entry.focus_set() if hasattr(self,"search_entry") else None)
        self.bind_all("<Control-Shift-D>", lambda e: self._open_dev_login())
        self.bind_all("<Control-Shift-d>", lambda e: self._open_dev_login())
        self._shortcuts_bound = True

    def _on_logo_click(self, e=None):
        now=time.time()
        if now - self._logo_t > 2.0: self._logo_clicks=0
        self._logo_clicks += 1; self._logo_t = now
        if self._logo_clicks >= 5:
            self._logo_clicks=0; self._open_dev_login()

    def _nav_back(self):
        if self.nav_index>0:
            self.nav_index -= 1
            self._load_page(self.nav_history[self.nav_index], record=False)

    def _nav_forward(self):
        if self.nav_index < len(self.nav_history)-1:
            self.nav_index += 1
            self._load_page(self.nav_history[self.nav_index], record=False)

    def show_page(self, pid):
        self._load_page(pid, record=(pid != self.current_page))

    def _load_page(self, pid, record=True):
        try:
            self._cancel_hero()
            if record:
                self.nav_history = self.nav_history[:self.nav_index+1]
                self.nav_history.append(pid); self.nav_index = len(self.nav_history)-1
            self.current_page = pid
            for w in self.scroll.winfo_children(): w.destroy()
            for nid, btn in self.nav_buttons.items():
                btn.configure(fg_color=C_PANEL2 if nid==pid else "transparent",
                              text_color=C_NEON if nid==pid else C_TEXT)
            pages = {"home":self._page_home,"browse":self._page_browse,"library":self._page_library,
                     "downloads":self._page_downloads,"wishlist":self._page_wishlist,"tasks":self._page_tasks,
                     "profile":self._page_profile,"settings":self._page_settings}
            try: pages.get(pid, self._page_home)()
            except Exception as e:
                log_error(f"page {pid}: {e}")
                ctk.CTkLabel(self.scroll, text=self.t("page_error", str(e)), text_color=C_ERR).pack(pady=20)
        except Exception as e:
            try: ctk.CTkLabel(self.scroll, text=str(e), text_color=C_ERR).pack(pady=20)
            except: pass

    def _on_search(self):
        try: self.search_query = self.search_var.get().strip().lower()
        except: self.search_query = ""
        if self.current_page == "browse": self._load_page("browse", record=False)

    def _cancel_hero(self):
        if self._hero_job:
            try: self.after_cancel(self._hero_job)
            except: pass
            self._hero_job = None

    def _apply_language(self, code):
        if code not in LANGS or code==self._lang: return
        self._lang = code; self.settings["language"]=code
        save_json(SETTINGS_FILE, self.settings)
        self._cancel_hero()
        self.title(f"ARDA LAUNCHER v{APP_VERSION} {self.t('tagline')}")
        for w in self.winfo_children(): w.destroy()
        self._shortcuts_bound = False
        self.search_query = ""
        self._build_layout()
        self._bind_shortcuts()
        self._load_page(self.current_page, record=False)

    def _page_home(self):
        self._hero_banner(); self._filter_bar()
        self._shelf(self.t("featured"), GAMES[:12])
        self._shelf(self.t("popular"), [g for g in GAMES if g.kind==_ST][:12])
        self._shelf(self.t("opensource"), [g for g in GAMES if g.kind==_GH][:9])
        self._shelf(self.t("newest"), GAMES[-12:])

    def _hero_banner(self):
        f = ctk.CTkFrame(self.scroll, fg_color=C_PANEL2, corner_radius=16, height=240)
        f.pack(fill="x", padx=24, pady=(20,10)); f.pack_propagate(False)
        left = ctk.CTkFrame(f, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=28, pady=24)
        ctk.CTkLabel(left, text=self.t("hero_tag"), font=ctk.CTkFont(size=14), text_color=C_NEON).pack(anchor="w")
        ctk.CTkLabel(left, text=self.t("hero_title"), font=ctk.CTkFont(size=32, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", pady=(4,4))
        ctk.CTkLabel(left, text=self.t("hero_desc"), font=ctk.CTkFont(size=13),
            text_color=C_MUTED).pack(anchor="w")
        row = ctk.CTkFrame(left, fg_color="transparent"); row.pack(anchor="w", pady=(12,0))
        ctk.CTkButton(row, text=self.t("btn_browse"), width=120, height=38, fg_color=C_NEON,
            text_color="#000", hover_color="#5DDFFF", command=lambda: self.show_page("browse")
        ).pack(side="left", padx=(0,8))
        ctk.CTkButton(row, text=self.t("btn_library"), width=140, height=38, fg_color=C_PURPLE,
            hover_color=C_NEON, command=lambda: self.show_page("library")).pack(side="left")
        right = ctk.CTkFrame(f, fg_color="transparent", width=300)
        right.pack(side="right", fill="y", padx=20, pady=16); right.pack_propagate(False)
        self._hero_previews = right; self._hero_idx = 0
        self._hero_cycle()

    def _hero_cycle(self):
        try:
            if not hasattr(self, "_hero_previews"): return
            try:
                if not self._hero_previews.winfo_exists(): return
            except: return
            for w in self._hero_previews.winfo_children(): w.destroy()
            g = GAMES[self._hero_idx % len(GAMES)]; self._hero_idx += 1
            ctk.CTkLabel(self._hero_previews, text=f"🎮\n{g.name}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color=C_TEXT,
                fg_color=C_PANEL, corner_radius=10, width=260, height=140).pack(fill="x", pady=4)
            self._hero_job = self.after(7000, self._hero_cycle)
        except Exception as e:
            log_error(f"hero: {e}")

    def _filter_bar(self):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(4,10))
        for lbl in ("Tümü","FPS","RPG","Strateji","MMO","Kart","Yarış","Co-op","Aksiyon"):
            ctk.CTkButton(f, text=lbl, width=90, height=30, fg_color=C_PANEL2,
                hover_color=C_NEON, text_color=C_TEXT,
                command=lambda q=lbl: (setattr(self,"search_query","" if q=="Tümü" else q.lower()),
                                       self.show_page("browse"))).pack(side="left", padx=4)

    def _shelf(self, title, games):
        w = ctk.CTkFrame(self.scroll, fg_color="transparent")
        w.pack(fill="x", padx=24, pady=10)
        ctk.CTkLabel(w, text=title, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", pady=(0,6))
        row = ctk.CTkFrame(w, fg_color="transparent"); row.pack(fill="x")
        for g in games: self._game_card(row, g)

    def _game_card(self, parent, game, w=None, h=None):
        if w is None or h is None:
            dimensions = {"small": (130, 185), "medium": (150, 210), "large": (180, 250)}
            w, h = dimensions.get(self.settings.get("card_size", "medium"), dimensions["medium"])
        card = ctk.CTkFrame(parent, width=w, height=h, fg_color=C_PANEL, corner_radius=10, cursor="hand2")
        card.pack(side="left", padx=6, pady=4); card.pack_propagate(False)
        img = ctk.CTkLabel(card, text="...", width=w-8, height=int(h*0.62),
            fg_color=C_PANEL2, corner_radius=8, text_color=C_MUTED)
        img.pack(pady=(4,4), padx=4)
        ctk.CTkLabel(card, text=game.name[:22], font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C_TEXT, wraplength=w-8).pack(padx=4)
        is_free = game.kind in (_ST, _WEB)
        ctk.CTkLabel(card, text=self.t("free") if is_free else self.t("mb", game.size_mb),
            font=ctk.CTkFont(size=10), text_color=C_OK if is_free else C_GOLD).pack(pady=(0,2))
        ctk.CTkButton(card, text=self.t("btn_download"), height=26, width=w-16,
            fg_color=C_NEON, text_color="#000", hover_color="#5DDFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._open_game_detail(game)).pack(pady=(0,4))
        card.bind("<Button-1>", lambda e, gg=game: self._open_game_detail(gg))
        img.bind("<Button-1>", lambda e, gg=game: self._open_game_detail(gg))
        def apply(im):
            if im is None:
                return
            def _upd():
                try:
                    if not img.winfo_exists():
                        return
                    fit = ImageOps.fit(im, (w-8, int(h*0.62)), method=Image.LANCZOS)
                    tki = ctk.CTkImage(light_image=fit, dark_image=fit, size=(w-8, int(h*0.62)))
                    img.configure(image=tki, text="")
                    img._arda_image_ref = tki
                except Exception as exc:
                    log_error(f"cover ui {game.gid}: {exc}")
            self._post_ui(_upd)
        if game.gid in _cover_mem: apply(_cover_mem[game.gid])
        else: fetch_cover(game, apply)

    def _page_browse(self):
        ctk.CTkLabel(self.scroll, text=self.t("browse"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        q = self.search_query
        res = [g for g in GAMES if not q or q in g.name.lower() or q in g.desc.lower()]
        ctk.CTkLabel(self.scroll, text=self.t("found", len(res)),
            font=ctk.CTkFont(size=12), text_color=C_MUTED).pack(anchor="w", padx=24)
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=24, pady=10)
        for g in res: self._game_card(grid, g)

    def _page_library(self):
        ctk.CTkLabel(self.scroll, text=self.t("library"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        if not self.library:
            ctk.CTkLabel(self.scroll, text=self.t("empty_lib"), text_color=C_MUTED).pack(pady=20); return
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=24, pady=10)
        for gid in self.library:
            g = GAME_MAP.get(gid)
            if g: self._game_card(grid, g)

    def _page_downloads(self):
        ctk.CTkLabel(self.scroll, text=self.t("downloads"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        ctk.CTkButton(self.scroll, text="📂 İndirme klasörünü aç", width=220,
            fg_color=C_PANEL2, command=lambda: self._open_path(DOWNLOADS_DIR)
        ).pack(anchor="e", padx=24, pady=(0,8))
        if not self.dl_log and not self.download_tasks:
            ctk.CTkLabel(self.scroll, text=self.t("no_dl"), text_color=C_MUTED).pack(pady=20); return
        # Aktif ve başarısız görevler; hata alan indirmeler tekrar denenebilir.
        for gid, task in list(self.download_tasks.items()):
            if task.state in ("done", "cancelled"): continue
            self._render_download_row(task)
        # Geçmiş
        for gid, info in self.dl_log.items():
            if gid in self.download_tasks and self.download_tasks[gid].state not in ("done","cancelled","error"):
                continue
            g = GAME_MAP.get(gid)
            row = ctk.CTkFrame(self.scroll, fg_color=C_PANEL, corner_radius=10)
            row.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(row, text=f"✓ {g.name if g else gid}",
                font=ctk.CTkFont(size=12), text_color=C_OK).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=info.get("time","")[:19], text_color=C_MUTED,
                font=ctk.CTkFont(size=10)).pack(side="right", padx=12)

    def _render_download_row(self, task):
        row = ctk.CTkFrame(self.scroll, fg_color=C_PANEL, corner_radius=10)
        row.pack(fill="x", padx=24, pady=4)
        top = ctk.CTkFrame(row, fg_color="transparent"); top.pack(fill="x", padx=12, pady=(8,4))
        ctk.CTkLabel(top, text=task.game.name, font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C_TEXT).pack(side="left")
        pct = min(100, max(0, int(task.downloaded/task.total*100))) if task.total else 0
        spd = f"{task.speed/1024/1024:.1f} MB/s" if task.speed > 0 else "--"
        st = {"resolving":"Hazırlanıyor","downloading":f"{pct}% • {spd}","paused":"Duraklatıldı",
              "error":f"Hata: {task.error}"}.get(task.state, task.state)
        ctk.CTkLabel(top, text=st, text_color=C_NEON,
            font=ctk.CTkFont(size=11)).pack(side="right")
        bar = ctk.CTkProgressBar(row, progress_color=C_NEON)
        bar.pack(fill="x", padx=12, pady=4)
        bar.set(pct/100 if task.total else 0)
        btns = ctk.CTkFrame(row, fg_color="transparent"); btns.pack(fill="x", padx=12, pady=(0,8))
        def _ref(t=task): self._load_page("downloads", record=False)
        if task.state == "downloading":
            ctk.CTkButton(btns, text=self.t("btn_pause"), width=100, height=26,
                fg_color=C_GOLD, text_color="#000",
                command=lambda t=task: (t.pause(), _ref())).pack(side="left", padx=2)
        elif task.state == "paused":
            ctk.CTkButton(btns, text=self.t("btn_resume"), width=100, height=26,
                fg_color=C_OK, text_color="#000",
                command=lambda t=task: (t.resume(), _ref())).pack(side="left", padx=2)
        if task.state in ("downloading", "paused", "resolving"):
            ctk.CTkButton(btns, text=self.t("btn_cancel"), width=100, height=26,
                fg_color=C_ERR, command=lambda t=task: (t.cancel(), _ref())
            ).pack(side="left", padx=2)
        elif task.state == "error":
            ctk.CTkButton(btns, text="↻ Yeniden Dene", width=140, height=26,
                fg_color=C_PURPLE, command=lambda t=task: self._start_download(t.game)
            ).pack(side="left", padx=2)

    def _page_wishlist(self):
        ctk.CTkLabel(self.scroll, text=self.t("wishlist"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        if not self.wishlist:
            ctk.CTkLabel(self.scroll, text=self.t("empty_wish"), text_color=C_MUTED).pack(pady=20); return
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=24, pady=10)
        for gid in self.wishlist:
            g = GAME_MAP.get(gid)
            if g: self._game_card(grid, g)

    def _page_tasks(self):
        ctk.CTkLabel(self.scroll, text=self.t("tasks"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        tasks = [(self.t("task_login"),self.t("task_login_d"),100,True),
                 (self.t("task_download"),self.t("task_download_d"),250,bool(self.dl_log)),
                 (self.t("task_librarian"),self.t("task_librarian_d"),500,len(self.library)>=5),
                 (self.t("task_explorer"),self.t("task_explorer_d"),300,False),
                 (self.t("task_social"),self.t("task_social_d"),200,len(self.wishlist)>=3),
                 (self.t("task_wheel"),self.t("task_wheel_d"),150,self.settings.get("last_wheel")==datetime.now().date().isoformat())]
        for title,desc,rw,done in tasks:
            r = ctk.CTkFrame(self.scroll, fg_color=C_PANEL, corner_radius=10)
            r.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(r, text=("✅ " if done else "⬜ ")+title,
                font=ctk.CTkFont(size=13, weight="bold"), text_color=C_TEXT).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(r, text=desc, text_color=C_MUTED, font=ctk.CTkFont(size=11)).pack(side="left", padx=12)
            ctk.CTkLabel(r, text=f"+{rw} 💎", font=ctk.CTkFont(size=12, weight="bold"),
                text_color=C_GOLD).pack(side="right", padx=12)

    def _page_profile(self):
        ctk.CTkLabel(self.scroll, text=self.t("profile"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,6))
        card = ctk.CTkFrame(self.scroll, fg_color=C_PANEL, corner_radius=16)
        card.pack(fill="x", padx=24, pady=10)
        top = ctk.CTkFrame(card, fg_color=C_PURPLE, height=100, corner_radius=16)
        top.pack(fill="x", padx=8, pady=8); top.pack_propagate(False)
        ctk.CTkLabel(top, text=self.t("neon_banner"), font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#fff").pack(pady=30)
        info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(info, text="🎮", width=70, height=70, fg_color=C_NEON, corner_radius=35,
            font=ctk.CTkFont(size=28)).pack(side="left", padx=12)
        meta = ctk.CTkFrame(info, fg_color="transparent"); meta.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(meta, text=f"{self.settings['username']}#{self.settings['tag']}",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=C_TEXT).pack(anchor="w")
        ctk.CTkLabel(meta, text=self.t("level"), text_color=C_MUTED).pack(anchor="w")
        ctk.CTkLabel(meta, text=self.t("credits", self.settings['credits']),
            font=ctk.CTkFont(size=13, weight="bold"), text_color=C_GOLD).pack(anchor="w")
        stats = ctk.CTkFrame(card, fg_color="transparent"); stats.pack(fill="x", padx=16, pady=(8,16))
        for icon,lbl,val in [("📚",self.t("profile_stats_lib"),len(self.library)),
                              ("⭐",self.t("profile_stats_wish"),len(self.wishlist)),
                              ("⬇",self.t("profile_stats_dl"),len(self.dl_log)),
                              ("🏆",self.t("profile_stats_ach"),0)]:
            s = ctk.CTkFrame(stats, fg_color=C_PANEL2, corner_radius=10)
            s.pack(side="left", expand=True, fill="x", padx=4)
            ctk.CTkLabel(s, text=icon, font=ctk.CTkFont(size=22)).pack(pady=(6,0))
            ctk.CTkLabel(s, text=str(val), font=ctk.CTkFont(size=16, weight="bold"),
                text_color=C_TEXT).pack()
            ctk.CTkLabel(s, text=lbl, text_color=C_MUTED, font=ctk.CTkFont(size=10)).pack(pady=(0,6))
        ctk.CTkLabel(self.scroll, text=self.t("shop"), font=ctk.CTkFont(size=18, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(16,6))
        shop = ctk.CTkFrame(self.scroll, fg_color="transparent"); shop.pack(fill="x", padx=24)
        for name, price, color in [("Neon Blue Frame",2000,C_NEON),("Purple Galaxy",2500,C_PURPLE),
                                    ("Gold Knight",3500,C_GOLD),("Fire Red",1800,C_ERR),
                                    ("Ice White",1500,"#E6EAF2"),("Emerald Green",2200,C_OK)]:
            ctk.CTkButton(shop, text=f"{name}\n💎 {price}", width=160, height=70,
                fg_color=C_PANEL2, hover_color=color,
                command=lambda n=name,p=price: self._buy(n,p)).pack(side="left", padx=4, pady=4)

    def _buy(self, name, price):
        if self.settings["credits"] >= price:
            self.settings["credits"] -= price
            save_json(SETTINGS_FILE, self.settings)
            try: self.credit_lbl.configure(text=self.t("credits", self.settings["credits"]))
            except: pass
            messagebox.showinfo(self.t("purchased"), self.t("purchased_msg", name, price))
        else:
            messagebox.showwarning(self.t("insufficient"), self.t("insufficient_msg", price))

    def _page_settings(self):
        ctk.CTkLabel(self.scroll, text=self.t("settings"), font=ctk.CTkFont(size=24, weight="bold"),
            text_color=C_TEXT).pack(anchor="w", padx=24, pady=(20,10))
        tabs = ctk.CTkTabview(self.scroll, fg_color=C_PANEL, segmented_button_fg_color=C_PANEL2,
            segmented_button_selected_color=C_NEON, segmented_button_selected_hover_color="#5DDFFF")
        tabs.pack(fill="both", expand=True, padx=24, pady=10)
        tnames = (self.t("tab_storage"), self.t("tab_network"), self.t("tab_perf"),
                  self.t("tab_appear"), self.t("tab_sound"), self.t("tab_maint"))
        if self._dev_verified:
            tnames += (self.t("dev_mode_tab"),)
        for tn in tnames: tabs.add(tn)
        f = tabs.tab(tnames[0])
        self._kv(f, self.t("data_dir"), str(DATA_DIR))
        ctk.CTkButton(f, text=self.t("open_folder"), width=180,
            command=lambda: self._open_path(DATA_DIR)).pack(anchor="w", padx=16, pady=8)
        ctk.CTkButton(f, text=self.t("clear_cache"), width=180, fg_color=C_ERR,
            command=self._clear_cache).pack(anchor="w", padx=16, pady=4)
        f = tabs.tab(tnames[1])
        self._kv(f, self.t("github_repo"), GITHUB_REPO)
        ctk.CTkLabel(f, text=self.t("network_info"), text_color=C_MUTED,
            wraplength=560, justify="left").pack(anchor="w", padx=16, pady=(16,10))
        ctk.CTkButton(f, text="GitHub deposunu aç", width=200,
            command=lambda: webbrowser.open(f"https://github.com/{GITHUB_REPO}")).pack(anchor="w", padx=16, pady=6)
        f = tabs.tab(tnames[2])
        boost = ctk.CTkSwitch(f, text=self.t("game_booster"))
        boost.pack(anchor="w", padx=16, pady=10)
        if self.settings.get("boost"): boost.select()
        def boost_cmd():
            enabled = bool(boost.get())
            self.settings["boost"] = enabled
            save_json(SETTINGS_FILE, self.settings)
            if enabled:
                self._safe_booster()
        boost.configure(command=boost_cmd)
        start = ctk.CTkSwitch(f, text=self.t("startup"))
        start.pack(anchor="w", padx=16, pady=10)
        if self.settings.get("startup"): start.select()
        def startup_cmd():
            desired = bool(start.get())
            if self._set_startup(desired):
                self.settings["startup"] = desired
                save_json(SETTINGS_FILE, self.settings)
            else:
                start.deselect() if desired else start.select()
                messagebox.showerror(self.t("error"), "Windows başlangıç ayarı değiştirilemedi.")
        start.configure(command=startup_cmd)
        f = tabs.tab(tnames[3])
        ctk.CTkLabel(f, text=self.t("language")+":", text_color=C_TEXT).pack(anchor="w", padx=16)
        lang_var = ctk.StringVar(value=LANGS[self._lang])
        def lang_change(display):
            for c,n in LANGS.items():
                if n==display: self._apply_language(c); return
        ctk.CTkOptionMenu(f, values=list(LANGS.values()), variable=lang_var,
            command=lang_change).pack(anchor="w", padx=16, pady=6)
        ctk.CTkLabel(f, text=self.t("theme"), text_color=C_TEXT).pack(anchor="w", padx=16, pady=(12,4))
        theme_var = ctk.StringVar(value=self.settings.get("theme","dark"))
        ctk.CTkOptionMenu(f, values=["dark","light","system"], variable=theme_var,
            command=lambda v: (ctk.set_appearance_mode(v),
                                self.settings.update({"theme":v}),
                                save_json(SETTINGS_FILE, self.settings))).pack(anchor="w", padx=16)
        ctk.CTkLabel(f, text=self.t("card_size"), text_color=C_TEXT).pack(anchor="w", padx=16, pady=(12,4))
        size_var = ctk.StringVar(value=self.settings.get("card_size","medium"))
        ctk.CTkOptionMenu(f, values=["small","medium","large"], variable=size_var,
            command=lambda v: (self.settings.update({"card_size":v}),
                                save_json(SETTINGS_FILE, self.settings))).pack(anchor="w", padx=16)
        f = tabs.tab(tnames[4])
        vol_var = ctk.IntVar(value=self.settings.get("volume",70))
        vol_lbl = ctk.CTkLabel(f, text=self.t("volume", vol_var.get()), text_color=C_TEXT)
        vol_lbl.pack(anchor="w", padx=16)
        def vol_change(v):
            self.settings["volume"] = int(float(v)); save_json(SETTINGS_FILE, self.settings)
            vol_lbl.configure(text=self.t("volume", int(float(v))))
        ctk.CTkSlider(f, from_=0, to=100, variable=vol_var, command=vol_change).pack(fill="x", padx=16, pady=8)
        notif = ctk.CTkSwitch(f, text=self.t("notifications"),
            command=lambda: (self.settings.update({"notifications": bool(notif.get())}),
                              save_json(SETTINGS_FILE, self.settings)))
        notif.pack(anchor="w", padx=16, pady=10)
        if self.settings.get("notifications", True): notif.select()
        f = tabs.tab(tnames[5])
        ctk.CTkButton(f, text=self.t("check_update"), width=240, command=self._check_update).pack(anchor="w", padx=16, pady=6)
        ctk.CTkButton(f, text=self.t("create_shortcut"), width=240, command=self._create_shortcut).pack(anchor="w", padx=16, pady=6)
        ctk.CTkButton(f, text=self.t("export_installer"), width=240, command=self._export_installer).pack(anchor="w", padx=16, pady=6)
        ctk.CTkButton(f, text=self.t("backup_json"), width=240, command=self._backup).pack(anchor="w", padx=16, pady=6)
        ctk.CTkButton(f, text=self.t("uninstall"), width=240, fg_color=C_ERR, command=self._uninstall).pack(anchor="w", padx=16, pady=6)
        if self._dev_verified:
            self._build_developer_tab(tabs.tab(tnames[-1]))

    def _build_developer_tab(self, parent):
        """Developer-only GitHub file manager. It is not constructed for normal users."""
        panel = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        panel.pack(fill="both", expand=True, padx=8, pady=8)
        ctk.CTkLabel(panel, text="GitHub Dosya Yöneticisi",
            font=ctk.CTkFont(size=19, weight="bold"), text_color=C_NEON).pack(anchor="w", padx=10, pady=(8,4))
        ctk.CTkLabel(panel, text=f"Depo: {GITHUB_REPO}  •  Gmail veya SMTP kullanılmaz. GitHub yazma izni gerekir.",
            text_color=C_MUTED, wraplength=720, justify="left").pack(anchor="w", padx=10, pady=(0,10))

        ctk.CTkLabel(panel, text="GitHub Fine-grained Token (Contents: Read and write)",
            text_color=C_TEXT).pack(anchor="w", padx=10, pady=(6,3))
        self._github_token_var = ctk.StringVar(value="")
        token_row = ctk.CTkFrame(panel, fg_color="transparent")
        token_row.pack(fill="x", padx=10, pady=3)
        self._github_token_entry = ctk.CTkEntry(token_row, textvariable=self._github_token_var,
            show="•", placeholder_text="Token girin; kayıtlı token varsa boş bırakın", height=36)
        self._github_token_entry.pack(side="left", fill="x", expand=True, padx=(0,6))
        ctk.CTkButton(token_row, text="Tokeni güvenli kaydet", width=160,
            command=self._github_store_token).pack(side="left", padx=3)
        ctk.CTkButton(token_row, text="Kayıtlı tokeni sil", width=135, fg_color=C_ERR,
            command=self._github_clear_token).pack(side="left", padx=3)

        branch_row = ctk.CTkFrame(panel, fg_color="transparent")
        branch_row.pack(fill="x", padx=10, pady=(12,4))
        ctk.CTkLabel(branch_row, text="Branch:", width=90, anchor="w", text_color=C_TEXT).pack(side="left")
        self._github_branch_var = ctk.StringVar(value="")
        ctk.CTkEntry(branch_row, textvariable=self._github_branch_var,
            placeholder_text="Boş bırakılırsa deponun varsayılan branch'i", height=34).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(branch_row, text="Bağlantıyı test et", width=150,
            command=self._github_test_connection).pack(side="left", padx=(8,0))

        ctk.CTkLabel(panel, text="GitHub hedef dosya yolu:", text_color=C_TEXT).pack(anchor="w", padx=10, pady=(12,3))
        self._github_path_var = ctk.StringVar(value="")
        ctk.CTkEntry(panel, textvariable=self._github_path_var,
            placeholder_text="ör. launcher.py veya assets/config.json", height=34).pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(panel, text="Bilgisayardaki dosya:", text_color=C_TEXT).pack(anchor="w", padx=10, pady=(10,3))
        local_row = ctk.CTkFrame(panel, fg_color="transparent")
        local_row.pack(fill="x", padx=10, pady=3)
        self._github_local_var = ctk.StringVar(value="")
        ctk.CTkEntry(local_row, textvariable=self._github_local_var,
            placeholder_text="Güncellenecek yerel dosyayı seçin", height=34).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(local_row, text="Dosya seç", width=110,
            command=self._github_choose_local).pack(side="left", padx=(6,0))

        ctk.CTkLabel(panel, text="Tüm depoyu eşitlemek için proje klasörü:",
            text_color=C_TEXT).pack(anchor="w", padx=10, pady=(12,3))
        folder_row = ctk.CTkFrame(panel, fg_color="transparent")
        folder_row.pack(fill="x", padx=10, pady=3)
        self._github_folder_var = ctk.StringVar(value="")
        ctk.CTkEntry(folder_row, textvariable=self._github_folder_var,
            placeholder_text="ArdaLauncher.pyw, version.json ve diğer proje dosyalarının bulunduğu klasör",
            height=34).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(folder_row, text="Klasör seç", width=110,
            command=self._github_choose_folder).pack(side="left", padx=(6,0))

        ctk.CTkLabel(panel,
            text="Klasör eşitleme: Yeni dosyalar eklenir, değişenler güncellenir, aynı olanlar atlanır. GitHub'daki fazladan dosyalar silinmez.",
            text_color=C_MUTED, wraplength=720, justify="left").pack(anchor="w", padx=10, pady=(2,6))

        ctk.CTkLabel(panel, text="Commit mesajı:", text_color=C_TEXT).pack(anchor="w", padx=10, pady=(10,3))
        self._github_commit_var = ctk.StringVar(value="Launcher dosyası güncellendi")
        ctk.CTkEntry(panel, textvariable=self._github_commit_var, height=34).pack(fill="x", padx=10, pady=3)

        action_row = ctk.CTkFrame(panel, fg_color="transparent")
        action_row.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(action_row, text="Depodaki dosyaları listele", width=210,
            fg_color=C_PURPLE, command=self._github_list_files).pack(side="left", padx=(0,6))
        ctk.CTkButton(action_row, text="GitHub'a yükle / güncelle", width=230,
            fg_color=C_NEON, text_color="#000", hover_color="#5DDFFF",
            command=self._github_upload_selected).pack(side="left", padx=6)
        ctk.CTkButton(action_row, text="Geliştirici modundan çık", width=190,
            fg_color=C_PANEL2, command=self._dev_logout).pack(side="right", padx=(6,0))

        sync_row = ctk.CTkFrame(panel, fg_color="transparent")
        sync_row.pack(fill="x", padx=10, pady=(0,8))
        ctk.CTkButton(sync_row, text="TÜM KLASÖRÜ GITHUB'A EŞİTLE", width=280, height=38,
            fg_color=C_OK, text_color="#06110B", hover_color="#4ADE80",
            command=self._github_sync_folder).pack(side="left", padx=6)

        self._github_status_label = ctk.CTkLabel(panel,
            text=("Kayıtlı şifreli token bulundu. Alanı boş bırakabilirsiniz." if self.settings.get("github_token_enc") else "Token henüz kaydedilmedi."),
            text_color=C_MUTED, wraplength=720, justify="left")
        self._github_status_label.pack(anchor="w", padx=10, pady=(0,8))
        ctk.CTkLabel(panel,
            text="Not: Fine-grained token yalnızca bu depoya erişmeli ve Contents izni Write olmalı. .github/workflows/ altındaki dosyalar için Workflows izni de gerekir. Dosya sınırı: 20 MB.",
            text_color=C_MUTED, wraplength=720, justify="left").pack(anchor="w", padx=10, pady=(0,8))
        self._github_files_frame = ctk.CTkScrollableFrame(panel, fg_color=C_PANEL2, height=210)
        self._github_files_frame.pack(fill="x", padx=10, pady=(4,12))
        ctk.CTkLabel(self._github_files_frame, text="Dosya listesini görmek için yukarıdaki düğmeye basın.",
            text_color=C_MUTED).pack(anchor="w", padx=8, pady=8)

    def _github_set_status(self, message, color=C_MUTED):
        try:
            if hasattr(self, "_github_status_label") and self._github_status_label.winfo_exists():
                self._github_status_label.configure(text=message, text_color=color)
        except Exception as exc:
            log_error(f"GitHub status UI: {exc}")

    def _github_current_token(self):
        entered = ""
        try:
            entered = self._github_token_var.get().strip()
        except Exception:
            pass
        if entered:
            return entered
        if self._github_token_session:
            return self._github_token_session
        encrypted = str(self.settings.get("github_token_enc") or "")
        token = decrypt_secret(encrypted) if encrypted else ""
        if token:
            return token
        raise RuntimeError("GitHub token bulunamadı. Fine-grained token girin.")

    def _github_store_token(self):
        token = self._github_token_var.get().strip()
        if not token:
            messagebox.showwarning("GitHub", "Önce token alanına token girin.")
            return
        self._github_token_session = token
        encrypted = encrypt_secret(token)
        if not encrypted:
            self.settings.pop("github_token_enc", None)
            save_json(SETTINGS_FILE, self.settings)
            self._github_set_status("Token yalnızca bu oturumda tutuluyor; Windows DPAPI kullanılamadığı için diske kaydedilmedi.", C_GOLD)
            return
        self.settings["github_token_enc"] = encrypted
        if not save_json(SETTINGS_FILE, self.settings):
            self.settings.pop("github_token_enc", None)
            self._github_set_status("Token şifrelendi ancak ayar dosyasına kaydedilemedi.", C_ERR)
            return
        self._github_token_var.set("")
        self._github_set_status("Token Windows DPAPI ile şifrelenerek kaydedildi. Alanı boş bırakıp kullanabilirsiniz.", C_OK)

    def _github_clear_token(self):
        self.settings.pop("github_token_enc", None)
        self._github_token_session = ""
        try: self._github_token_var.set("")
        except Exception: pass
        if save_json(SETTINGS_FILE, self.settings):
            self._github_set_status("Kayıtlı GitHub tokeni silindi.", C_OK)
        else:
            self._github_set_status("Token silindi ancak ayar dosyası kaydedilemedi.", C_ERR)

    @staticmethod
    def _github_validate_path(path_value):
        raw = str(path_value or "").strip().replace(chr(92), "/")
        path = PurePosixPath(raw)
        windows_path = PureWindowsPath(raw)
        if (not raw or raw.startswith("/") or path.is_absolute()
                or windows_path.is_absolute() or bool(windows_path.drive)
                or any(part in ("", ".", "..") for part in raw.split("/"))
                or any(ord(ch) < 32 for ch in raw)):
            raise ValueError("GitHub hedef yolu geçersiz. Örnek: src/launcher.py")
        if any(part == ".git" for part in path.parts):
            raise ValueError(".git klasöründeki dosyalar güncellenemez.")
        return "/".join(path.parts)

    @staticmethod
    def _github_api_request(method, endpoint, token, params=None, payload=None, allow_404=False):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ArdaLauncher/12.2",
        }
        try:
            response = requests.request(method, "https://api.github.com" + endpoint,
                headers=headers, params=params, json=payload, timeout=(12, 45))
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("GitHub bağlantısı zaman aşımına uğradı.") from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"GitHub ağ bağlantısı kurulamadı: {exc}") from exc
        if response.status_code == 404 and allow_404:
            response.close()
            return None
        if response.status_code >= 400:
            try:
                detail = response.json().get("message", "")
            except Exception:
                detail = ""
            status = response.status_code
            response.close()
            if status == 401:
                raise RuntimeError("GitHub token geçersiz veya süresi dolmuş. Tokeni yenileyin.")
            if status == 403:
                raise RuntimeError("GitHub erişimi reddetti. Token izinlerini ve API limitini kontrol edin (Contents: write gerekli).")
            if status == 404:
                raise RuntimeError("Depo, branch veya dosya bulunamadı. Tokenin bu depoya eriştiğini kontrol edin.")
            if status == 409:
                raise RuntimeError("GitHub çakışma bildirdi. Depo değişmiş olabilir; dosya listesini yenileyip tekrar deneyin.")
            if status == 422:
                raise RuntimeError("GitHub dosyayı kabul etmedi. Dosya yolu, commit mesajı ve gerekli izinleri kontrol edin.")
            raise RuntimeError(f"GitHub API HTTP {status}: {detail or 'İstek başarısız.'}")
        try:
            return response.json() if response.content else {}
        except ValueError as exc:
            raise RuntimeError("GitHub beklenmeyen bir yanıt döndürdü.") from exc
        finally:
            response.close()

    def _github_repo_and_branch(self, token, branch_override=""):
        parts = GITHUB_REPO.split("/", 1)
        if len(parts) != 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts):
            raise RuntimeError("Uygulamanın GitHub depo ayarı geçersiz.")
        endpoint = f"/repos/{quote(parts[0], safe='')}/{quote(parts[1], safe='')}"
        repo_data = self._github_api_request("GET", endpoint, token)
        if not isinstance(repo_data, dict):
            raise RuntimeError("GitHub depo bilgisi beklenen biçimde değil.")
        default_branch = str(repo_data.get("default_branch") or "main")
        branch = str(branch_override or "").strip() or default_branch
        if len(branch) > 250 or any(ord(ch) < 32 for ch in branch):
            raise ValueError("Branch adı geçersiz.")
        return endpoint, branch

    def _github_get_tree_sha(self, repo_endpoint, branch, token):
        ref = self._github_api_request("GET",
            f"{repo_endpoint}/git/ref/heads/{quote(branch, safe='/')}", token)
        obj = ref.get("object", {}) if isinstance(ref, dict) else {}
        commit_sha = obj.get("sha") if isinstance(obj, dict) else None
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", commit_sha):
            raise RuntimeError("GitHub branch referansı geçerli bir commit SHA döndürmedi.")
        commit = self._github_api_request("GET",
            f"{repo_endpoint}/git/commits/{quote(commit_sha, safe='')}", token)
        tree = commit.get("tree", {}) if isinstance(commit, dict) else {}
        tree_sha = tree.get("sha") if isinstance(tree, dict) else None
        if not isinstance(tree_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40,64}", tree_sha):
            raise RuntimeError("GitHub commit kaydında geçerli bir tree SHA bulunamadı.")
        return tree_sha

    def _github_test_connection(self):
        if self._github_busy:
            return
        try: token = self._github_current_token()
        except Exception as exc:
            messagebox.showwarning("GitHub", str(exc)); return
        self._github_busy = True
        self._github_set_status("GitHub bağlantısı ve depo erişimi kontrol ediliyor...", C_GOLD)
        branch_value = self._github_branch_var.get().strip()
        def worker():
            try:
                _, branch = self._github_repo_and_branch(token, branch_value)
                self._post_ui(lambda b=branch: self._github_set_status(
                    f"Bağlantı başarılı. Depo: {GITHUB_REPO}  •  Branch: {b}", C_OK))
                if not branch_value:
                    self._post_ui(lambda b=branch: self._github_branch_var.set(b))
            except Exception as exc:
                message = str(exc)
                self._post_ui(lambda m=message: self._github_set_status(m, C_ERR))
            finally:
                self._github_busy = False
        threading.Thread(target=worker, daemon=True).start()

    def _github_list_files(self):
        if self._github_busy:
            return
        try: token = self._github_current_token()
        except Exception as exc:
            messagebox.showwarning("GitHub", str(exc)); return
        self._github_busy = True
        self._github_set_status("GitHub dosya ağacı alınıyor...", C_GOLD)
        branch_value = self._github_branch_var.get().strip()
        def worker():
            try:
                repo_endpoint, branch = self._github_repo_and_branch(token, branch_value)
                tree_sha = self._github_get_tree_sha(repo_endpoint, branch, token)
                tree = self._github_api_request("GET",
                    f"{repo_endpoint}/git/trees/{quote(tree_sha, safe='')}", token,
                    params={"recursive": "1"})
                files = sorted(item.get("path", "") for item in tree.get("tree", [])
                    if isinstance(item, dict) and item.get("type") == "blob" and item.get("path"))
                truncated = bool(tree.get("truncated"))
                self._post_ui(lambda b=branch: self._github_branch_var.set(b))
                self._post_ui(lambda items=files[:400], tr=truncated, total=len(files):
                    self._github_render_files(items, tr, total))
            except Exception as exc:
                message = str(exc)
                self._post_ui(lambda m=message: self._github_set_status(m, C_ERR))
            finally:
                self._github_busy = False
        threading.Thread(target=worker, daemon=True).start()

    def _github_render_files(self, files, truncated, total):
        try:
            for child in self._github_files_frame.winfo_children():
                child.destroy()
            if not files:
                ctk.CTkLabel(self._github_files_frame, text="Depoda dosya bulunamadı.",
                    text_color=C_MUTED).pack(anchor="w", padx=8, pady=8)
            for remote_path in files:
                row = ctk.CTkFrame(self._github_files_frame, fg_color="transparent")
                row.pack(fill="x", padx=4, pady=2)
                ctk.CTkLabel(row, text=remote_path, anchor="w", text_color=C_TEXT,
                    font=ctk.CTkFont(size=11)).pack(side="left", fill="x", expand=True, padx=6)
                ctk.CTkButton(row, text="Hedef olarak seç", width=115, height=26,
                    command=lambda value=remote_path: self._github_path_var.set(value)).pack(side="right", padx=4)
            suffix = " (GitHub tam ağacı kırptı)" if truncated else ""
            self._github_set_status(f"{min(total, len(files))}/{total} dosya listelendi • Branch: {self._github_branch_var.get()}{suffix}", C_OK)
        except Exception as exc:
            log_error(f"GitHub file list render: {exc}")
            self._github_set_status(f"Dosya listesi ekrana çizilemedi: {exc}", C_ERR)

    def _github_choose_local(self):
        selected = filedialog.askopenfilename(title="GitHub'a yüklenecek dosyayı seçin")
        if selected:
            self._github_local_var.set(selected)
            if not self._github_path_var.get().strip():
                self._github_path_var.set(Path(selected).name)

    @staticmethod
    def _github_should_skip_local_file(relative_path):
        """Keep secrets, caches and machine-specific data out of repository sync."""
        rel = PurePosixPath(str(relative_path).replace("\\", "/"))
        parts = [part.lower() for part in rel.parts]
        name = rel.name.lower()
        ignored_dirs = {
            ".git", "__pycache__", ".venv", "venv", "env", "virtualenv",
            "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache",
            ".ruff_cache", ".tox", ".idea", ".vs", "$recycle.bin"
        }
        if any(part in ignored_dirs for part in parts[:-1]):
            return True
        if name in {
            ".env", "settings.json", "lockout.json", "errors.log",
            "credentials.json", "secrets.json", "token.json", "id_rsa",
            "id_ed25519", "known_hosts", "desktop.ini", "thumbs.db"
        }:
            return True
        if name.startswith(".env.") or name.endswith((
            ".pyc", ".pyo", ".pyd", ".log", ".tmp", ".bak", ".part",
            ".download", ".secret", ".token", ".pem", ".key", ".p12", ".pfx"
        )):
            return True
        if name in {"settings.json.bak", "library.json", "wishlist.json", "download_log.json"}:
            return True
        return False

    @staticmethod
    def _github_git_blob_sha(content):
        """Return the SHA-1 Git uses for a blob (same format as GitHub tree entries)."""
        header = f"blob {len(content)}\0".encode("ascii")
        return hashlib.sha1(header + content).hexdigest()

    @classmethod
    def _github_collect_folder_files(cls, folder):
        root = Path(folder).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError("Önce geçerli bir proje klasörü seçin.")
        ignored_dirs = {
            ".git", "__pycache__", ".venv", "venv", "env", "virtualenv",
            "node_modules", "dist", "build", ".pytest_cache", ".mypy_cache",
            ".ruff_cache", ".tox", ".idea", ".vs", "$recycle.bin"
        }
        files = []
        skipped = 0
        too_large = []
        max_bytes = 20 * 1024 * 1024
        for current_dir, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current_dir)
            # Prune generated/secret-heavy folders before descending into them.
            kept_dirs = []
            for dirname in sorted(dirnames):
                dir_path = current_path / dirname
                if dirname.lower() in ignored_dirs or dir_path.is_symlink():
                    continue
                kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in sorted(filenames):
                candidate = current_path / filename
                try:
                    if candidate.is_symlink() or not candidate.is_file():
                        continue
                    relative = candidate.relative_to(root).as_posix()
                    if cls._github_should_skip_local_file(relative):
                        skipped += 1
                        continue
                    remote_path = cls._github_validate_path(relative)
                    size = candidate.stat().st_size
                    if size > max_bytes:
                        too_large.append((remote_path, size))
                        continue
                    files.append((candidate, remote_path, size))
                except (OSError, ValueError) as exc:
                    raise RuntimeError(f"Yerel dosya taranamadı: {candidate.name}: {exc}") from exc
        files.sort(key=lambda item: item[1].casefold())
        if not files:
            if too_large:
                raise ValueError("Klasörde 20 MB sınırının altında yüklenebilir dosya bulunamadı.")
            raise ValueError("Seçilen klasörde eşitlenecek dosya bulunamadı.")
        if len(files) > 1000:
            raise ValueError("Güvenlik sınırı: tek seferde en fazla 1000 dosya eşitlenebilir.")
        return root, files, skipped, too_large

    def _github_choose_folder(self):
        selected = filedialog.askdirectory(title="GitHub ile eşitlenecek proje klasörünü seçin")
        if selected:
            self._github_folder_var.set(selected)

    def _github_sync_folder(self):
        """Add/update every eligible local project file on the selected GitHub branch."""
        if self._github_busy:
            return
        try:
            token = self._github_current_token()
            root, local_files, skipped_count, too_large = self._github_collect_folder_files(
                self._github_folder_var.get().strip())
            commit_prefix = self._github_commit_var.get().strip()
            if not commit_prefix:
                raise ValueError("Commit mesajı boş olamaz.")
            if len(commit_prefix) > 200 or any(ord(ch) < 32 for ch in commit_prefix):
                raise ValueError("Commit mesajı 200 karakteri aşmamalı ve kontrol karakteri içermemeli.")
            branch_value = self._github_branch_var.get().strip()
            total_bytes = sum(item[2] for item in local_files)
        except Exception as exc:
            messagebox.showwarning("GitHub klasör eşitleme", str(exc))
            return

        preview = [f"Klasör: {root}", f"Depo: {GITHUB_REPO}",
                   f"Dosya sayısı: {len(local_files)}",
                   f"Toplam boyut: {total_bytes / (1024 * 1024):.2f} MB",
                   f"Branch: {branch_value or 'varsayılan'}",
                   f"Atlanacak hassas/önbellek dosyası: {skipped_count}",
                   f"20 MB sınırını aşan dosya: {len(too_large)}",
                   "\nYeni dosyalar eklenecek, farklı olanlar güncellenecek, aynı olanlar atlanacak.",
                   "GitHub'da bu klasörde bulunmayan dosyalar SİLİNMEYECEK."]
        if not messagebox.askyesno("Tüm klasörü GitHub'a eşitle", "\n".join(preview)):
            return

        self._github_busy = True
        self._github_set_status("GitHub deposu karşılaştırılıyor...", C_GOLD)

        def worker():
            created = updated = unchanged = 0
            failed_path = ""
            commit_urls = []
            try:
                repo_endpoint, branch = self._github_repo_and_branch(token, branch_value)
                tree_sha = self._github_get_tree_sha(repo_endpoint, branch, token)
                tree = self._github_api_request("GET",
                    f"{repo_endpoint}/git/trees/{quote(tree_sha, safe='')}", token,
                    params={"recursive": "1"})
                if not isinstance(tree, dict) or not isinstance(tree.get("tree"), list):
                    raise RuntimeError("GitHub deposunun dosya ağacı okunamadı.")
                if tree.get("truncated"):
                    raise RuntimeError("GitHub dosya ağacı 100.000 kayıt sınırında kırpıldı. Güvenli eşitleme için işlem durduruldu.")
                remote_sha = {
                    item.get("path"): item.get("sha")
                    for item in tree["tree"]
                    if isinstance(item, dict) and item.get("type") == "blob"
                    and isinstance(item.get("path"), str) and isinstance(item.get("sha"), str)
                }
                for index, (local_path, remote_path, original_size) in enumerate(local_files, 1):
                    failed_path = remote_path
                    data = local_path.read_bytes()
                    if len(data) > 20 * 1024 * 1024:
                        raise RuntimeError(f"Dosya tarama sonrasında 20 MB sınırını aştı: {remote_path}")
                    blob_sha = self._github_git_blob_sha(data)
                    previous_sha = remote_sha.get(remote_path)
                    if previous_sha == blob_sha:
                        unchanged += 1
                    else:
                        encoded_path = quote(remote_path, safe="/")
                        endpoint = f"{repo_endpoint}/contents/{encoded_path}"
                        payload = {
                            "message": (f"{commit_prefix}: {remote_path}")[:200],
                            "content": base64.b64encode(data).decode("ascii"),
                            "branch": branch,
                        }
                        if previous_sha:
                            payload["sha"] = previous_sha
                        result = self._github_api_request("PUT", endpoint, token, payload=payload)
                        commit = result.get("commit", {}) if isinstance(result, dict) else {}
                        commit_url = commit.get("html_url", "") if isinstance(commit, dict) else ""
                        if commit_url and len(commit_urls) < 3:
                            commit_urls.append(commit_url)
                        if previous_sha:
                            updated += 1
                        else:
                            created += 1
                    current = index
                    self._post_ui(lambda i=current, n=len(local_files), p=remote_path,
                                         c=created, u=updated, s=unchanged:
                        self._github_set_status(
                            f"Eşitleniyor: {i}/{n} • {p}\nEklendi: {c} • Güncellendi: {u} • Değişmedi: {s}",
                            C_GOLD))

                result_text = (
                    "GitHub klasör eşitlemesi tamamlandı.\n"
                    f"Branch: {branch}\n"
                    f"Yeni eklenen: {created}\n"
                    f"Güncellenen: {updated}\n"
                    f"Değişmediği için atlanan: {unchanged}\n"
                    f"Hassas/önbellek dosyaları: {skipped_count}\n"
                    f"20 MB üstü dosyalar: {len(too_large)}\n"
                    "GitHub'da fazladan bulunan dosyalar korunmuştur."
                )
                if too_large:
                    result_text += "\nAtlanan büyük dosyalar: " + ", ".join(p for p, _ in too_large[:8])
                if commit_urls:
                    result_text += "\nÖrnek commit: " + commit_urls[-1]
                self._post_ui(lambda msg=result_text: self._github_set_status(msg, C_OK))
                if too_large:
                    log_error("GitHub folder sync skipped oversized files: " + ", ".join(p for p, _ in too_large))
            except Exception as exc:
                message = f"Klasör eşitlemesi tamamlanamadı.\n"
                message += f"Tamamlanan: eklendi {created}, güncellendi {updated}, atlandı {unchanged}.\n"
                if failed_path:
                    message += f"Hata alınan dosya: {failed_path}\n"
                message += str(exc)
                if failed_path.startswith(".github/workflows/"):
                    message += " .github/workflows dosyaları için Workflows: write izni gerekebilir."
                self._post_ui(lambda msg=message: self._github_set_status(msg, C_ERR))
                log_error(f"GitHub folder sync failed at {failed_path}: {message}")
            finally:
                self._github_busy = False

        threading.Thread(target=worker, daemon=True).start()

    def _github_upload_selected(self):
        if self._github_busy:
            return
        try:
            token = self._github_current_token()
            local_path = Path(self._github_local_var.get().strip()).expanduser()
            if not local_path.is_file():
                raise ValueError("Önce bilgisayarınızdan yüklenecek dosyayı seçin.")
            file_size = local_path.stat().st_size
            if file_size > 20 * 1024 * 1024:
                raise ValueError("Bu araç tek dosyada en fazla 20 MB yüklemeyi destekler.")
            remote_path = self._github_validate_path(self._github_path_var.get())
            commit_message = self._github_commit_var.get().strip()
            if not commit_message:
                raise ValueError("Commit mesajı boş olamaz.")
            if len(commit_message) > 200 or any(ord(ch) < 32 for ch in commit_message):
                raise ValueError("Commit mesajı 200 karakteri aşmamalı ve kontrol karakteri içermemeli.")
            branch_value = self._github_branch_var.get().strip()
        except Exception as exc:
            messagebox.showwarning("GitHub", str(exc)); return

        action = f"'{local_path.name}' dosyası '{GITHUB_REPO}/{remote_path}' konumuna\n"
        action += "eklensin veya güncellensin mi?\n\n"
        action += f"Branch: {branch_value or 'varsayılan'}\nBoyut: {file_size / 1024:.1f} KB"
        if not messagebox.askyesno("GitHub dosya güncelleme", action):
            return

        self._github_busy = True
        self._github_set_status("Dosya GitHub'a yükleniyor...", C_GOLD)
        def worker():
            try:
                repo_endpoint, branch = self._github_repo_and_branch(token, branch_value)
                encoded_path = quote(remote_path, safe="/")
                content_endpoint = f"{repo_endpoint}/contents/{encoded_path}"
                existing = self._github_api_request("GET", content_endpoint, token,
                    params={"ref": branch}, allow_404=True)
                file_bytes = local_path.read_bytes()
                if len(file_bytes) > 20 * 1024 * 1024:
                    raise RuntimeError("Dosya yükleme başlamadan önce 20 MB sınırını aştı; işlem iptal edildi.")
                payload = {
                    "message": commit_message,
                    "content": base64.b64encode(file_bytes).decode("ascii"),
                    "branch": branch,
                }
                if existing is not None:
                    if not isinstance(existing, dict) or existing.get("type") != "file" or not existing.get("sha"):
                        raise RuntimeError("GitHub hedefi normal bir dosya değil; güncelleme iptal edildi.")
                    payload["sha"] = existing["sha"]
                result = self._github_api_request("PUT", content_endpoint, token, payload=payload)
                commit = result.get("commit", {}) if isinstance(result, dict) else {}
                html_url = commit.get("html_url", "") if isinstance(commit, dict) else ""
                message = ("Dosya GitHub'a eklendi." if existing is None else "Dosya GitHub'da güncellendi.")
                if html_url:
                    message += f"\nCommit: {html_url}"
                self._post_ui(lambda m=message: self._github_set_status(m, C_OK))
            except Exception as exc:
                message = str(exc)
                if remote_path.startswith(".github/workflows/"):
                    message += " .github/workflows dosyaları için Workflows: write izni de gerekebilir."
                self._post_ui(lambda m=message: self._github_set_status(m, C_ERR))
                log_error(f"GitHub upload failed for {remote_path}: {message}")
            finally:
                self._github_busy = False
        threading.Thread(target=worker, daemon=True).start()

    def _dev_logout(self):
        if self._github_busy:
            messagebox.showwarning("Geliştirici Modu", "GitHub işlemi sürerken çıkış yapılamaz. İşlem tamamlanınca tekrar deneyin.")
            return
        self._dev_verified = False
        self._github_token_session = ""
        try: self._github_token_var.set("")
        except Exception: pass
        self._load_page("settings", record=False)
        messagebox.showinfo("Geliştirici Modu", "Geliştirici modundan çıkış yapıldı.")

    def _kv(self, parent, k, v):
        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(r, text=f"{k}:", text_color=C_MUTED, font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkLabel(r, text=v, text_color=C_TEXT, font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

    def _clear_cache(self):
        try:
            for f in COVERS_DIR.glob("*.jpg"): f.unlink()
            _cover_mem.clear()
            messagebox.showinfo(self.t("ok"), self.t("cache_cleared"))
        except Exception as e: messagebox.showerror(self.t("error"), str(e))

    def _safe_booster(self):
        if psutil is None:
            messagebox.showwarning("Game Booster", "psutil kurulu değil."); return
        critical = {"explorer.exe","dwm.exe","winlogon.exe","csrss.exe","smss.exe",
                    "services.exe","lsass.exe","svchost.exe","system","system idle process",
                    "registry","wininit.exe","fontdrvhost.exe","taskmgr.exe"}
        candidates = []
        try:
            for p in psutil.process_iter(["pid","name"]):
                try:
                    n = (p.info.get("name") or "").lower()
                    if n in critical or not n: continue
                    if n in {"searchapp.exe","cortana.exe","yourphone.exe","skypeapp.exe"}:
                        candidates.append(p.info)
                except: continue
        except: pass
        if not candidates:
            messagebox.showinfo("Game Booster", "Kapatılacak süreç yok."); return
        names = "\n".join(f"• {c['name']} (PID {c['pid']})" for c in candidates)
        if not messagebox.askyesno("Game Booster", f"Kapatılacak:\n\n{names}\n\nOnaylıyor musunuz?"): return
        killed = 0
        for c in candidates:
            try:
                psutil.Process(c["pid"]).terminate(); killed += 1
            except: pass
        messagebox.showinfo("Game Booster", f"{killed} süreç kapatıldı.")

    def _open_path(self, path):
        try:
            path = str(Path(path).resolve())
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as exc:
            messagebox.showerror(self.t("error"), str(exc))

    def _set_startup(self, enable):
        if winreg is None:
            return False
        key = None
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if enable:
                if getattr(sys, "frozen", False):
                    command = f'"{Path(sys.executable).resolve()}"'
                else:
                    script = Path(sys.argv[0]).resolve()
                    interpreter = Path(sys.executable)
                    pythonw = interpreter.with_name("pythonw.exe")
                    if pythonw.exists(): interpreter = pythonw
                    command = f'"{interpreter}" "{script}"'
                winreg.SetValueEx(key, "ArdaLauncher", 0, winreg.REG_SZ, command)
            else:
                try: winreg.DeleteValue(key, "ArdaLauncher")
                except FileNotFoundError: pass
            return True
        except Exception as exc:
            log_error(f"startup registry: {exc}")
            return False
        finally:
            if key is not None:
                try: winreg.CloseKey(key)
                except Exception: pass

    def _check_update(self):
        def worker():
            try:
                with requests.get(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.json",
                                  timeout=10, headers={"User-Agent":"ArdaLauncher/12.2"}) as response:
                    response.raise_for_status()
                    payload = response.json()
                latest = str(payload.get("version", "?")) if isinstance(payload, dict) else "?"
                self._post_ui(lambda: messagebox.showinfo(self.t("check_update"),
                    f"Yüklü: {APP_VERSION}\nSunucu: {latest}"))
            except Exception as exc:
                error_text = str(exc)
                self._post_ui(lambda message=error_text: messagebox.showerror(self.t("error"), message))
        threading.Thread(target=worker, daemon=True).start()

    def _create_shortcut(self):
        try:
            desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
            desktop.mkdir(parents=True, exist_ok=True)
            link_path = desktop / "ARDA LAUNCHER.lnk"
            if getattr(sys, "frozen", False):
                target = Path(sys.executable).resolve()
                arguments = ""
            else:
                script = Path(sys.argv[0]).resolve()
                interpreter = Path(sys.executable)
                pythonw = interpreter.with_name("pythonw.exe")
                if pythonw.exists(): interpreter = pythonw
                target = interpreter.resolve()
                arguments = f'"{script}"'
            def ps_quote(value):
                return "'" + str(value).replace("'", "''") + "'"
            script_ps = (
                "$ws = New-Object -ComObject WScript.Shell; "
                f"$s = $ws.CreateShortcut({ps_quote(link_path)}); "
                f"$s.TargetPath = {ps_quote(target)}; "
                f"$s.Arguments = {ps_quote(arguments)}; "
                f"$s.IconLocation = {ps_quote(ICON_FILE)}; $s.Save()"
            )
            encoded = base64.b64encode(script_ps.encode("utf-16le")).decode("ascii")
            result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive",
                                     "-EncodedCommand", encoded], capture_output=True,
                                     text=True, timeout=20)
            if result.returncode != 0 or not link_path.exists():
                raise RuntimeError((result.stderr or result.stdout or "Kısayol oluşturulamadı.").strip())
            messagebox.showinfo(self.t("ok"), f"Kısayol oluşturuldu: {link_path}")
        except Exception as exc:
            log_error(f"shortcut: {exc}")
            messagebox.showerror(self.t("error"), str(exc))

    def _export_installer(self):
        try:
            p = filedialog.asksaveasfilename(
                defaultextension=".bat", initialfile="ArdaLauncherInstaller.bat")
            if not p:
                return
            Path(p).write_text(INSTALLER_BAT_TEMPLATE, encoding="utf-8")
            messagebox.showinfo(self.t("saved"), p)
        except Exception as e:
            messagebox.showerror(self.t("error"), str(e))

    def _backup(self):
        try:
            p = filedialog.asksaveasfilename(defaultextension=".json", initialfile="arda_backup.json")
            if not p: return
            private_keys = {"dev_hash", "recovery_hash", "recovery_notice_enc", "recovery_notice_pending", "github_token_enc"}
            data = {"settings": {k:v for k,v in self.settings.items() if k not in private_keys},
                    "library": self.library, "wishlist": self.wishlist, "downloads": self.dl_log}
            Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            messagebox.showinfo(self.t("ok"), f"Yedek: {p}")
        except Exception as e: messagebox.showerror(self.t("error"), str(e))

    def _uninstall(self):
        if not messagebox.askyesno(self.t("uninstall"), "Tüm veriler silinsin mi?"): return
        try:
            shutil.rmtree(DATA_DIR, ignore_errors=True)
            messagebox.showinfo(self.t("uninstall"), "Veriler silindi.")
            self.after(1000, self.destroy)
        except Exception as e: messagebox.showerror(self.t("error"), str(e))

    # ============ OYUN DETAY (PENCERE KAPANMA FIX) ============
    def _open_game_detail(self, game):
        try:
            win = ctk.CTkToplevel(self)
            self._show_window(win)  # ⭐ KRİTİK: referans tut
            win.title(game.name); win.geometry("560x680"); win.configure(fg_color=C_BG)
            try: win.iconbitmap(str(ICON_FILE))
            except: pass
            ctk.CTkLabel(win, text=game.name, font=ctk.CTkFont(size=22, weight="bold"),
                text_color=C_TEXT).pack(pady=(16,6))
            ctk.CTkLabel(win, text=game.desc, text_color=C_MUTED, font=ctk.CTkFont(size=12),
                wraplength=500).pack(pady=6, padx=20)
            ctk.CTkLabel(win, text=self.t("detail_type", game.kind.upper(), game.size_mb, game.ram_gb),
                text_color=C_GOLD).pack(pady=8)
            if game.kind == _GH:
                ctk.CTkButton(win, text=self.t("btn_install"), height=44, width=280, fg_color=C_NEON,
                    text_color="#000", hover_color="#5DDFFF",
                    command=lambda: (self._start_download(game), win.destroy())).pack(pady=8)
            elif game.kind == _WEB:
                ctk.CTkLabel(win, text="Resmî web sitesinden ücretsiz indirilebilir.",
                    text_color=C_OK, font=ctk.CTkFont(size=12), wraplength=420).pack(pady=6)
                ctk.CTkButton(win, text="Resmî siteden indir", height=44, width=280,
                    fg_color=C_NEON, text_color="#000", hover_color="#5DDFFF",
                    command=lambda: webbrowser.open("https://www.beyondallreason.info/download")).pack(pady=8)
            else:
                steam_found = find_steam_path() is not None
                installed = is_steam_installed(game.appid) if steam_found else False
                if installed:
                    ctk.CTkLabel(win, text="✓ "+self.t("steam_already"),
                        text_color=C_OK, font=ctk.CTkFont(size=12)).pack(pady=4)
                elif steam_found:
                    ctk.CTkButton(win, text=self.t("btn_install")+" (Steam)", height=44, width=280,
                        fg_color=C_NEON, text_color="#000", hover_color="#5DDFFF",
                        command=lambda: (self._start_steam(game), win.destroy())).pack(pady=8)
                else:
                    ctk.CTkLabel(win, text=self.t("steam_not_found"),
                        text_color=C_ERR, font=ctk.CTkFont(size=12), wraplength=400).pack(pady=4)
                    ctk.CTkButton(win, text=self.t("steam_install_btn"), height=40, width=280,
                        fg_color=C_PURPLE,
                        command=lambda: webbrowser.open("https://store.steampowered.com/about/")
                    ).pack(pady=4)
            ctk.CTkButton(win, text=self.t("add_wish"), height=36, width=280,
                fg_color=C_PURPLE, command=lambda: self._toggle_wishlist(game)).pack(pady=4)
            ctk.CTkButton(win, text=self.t("add_lib"), height=36, width=280,
                fg_color=C_PANEL2, command=lambda: self._add_library(game)).pack(pady=4)
            ctk.CTkButton(win, text=self.t("close"), height=32, width=280, fg_color=C_PANEL2,
                command=win.destroy).pack(pady=6)
        except Exception as e:
            log_error(f"detail: {e}")
            messagebox.showerror(self.t("error"), str(e))

    def _start_steam(self, game):
        ok, err = launch_steam_install(game.appid)
        if ok:
            messagebox.showinfo(self.t("steam_start"), self.t("steam_started"))
        else:
            messagebox.showerror(self.t("steam_error"), err)

    def _start_download(self, game):
        if game.gid in self.download_tasks:
            t = self.download_tasks[game.gid]
            if t.state in ("downloading","paused","resolving"):
                messagebox.showinfo("İndirme", "Bu oyun zaten indiriliyor."); return
        task = DownloadTask(game)
        task.on_update = lambda updated: self._post_ui(lambda item=updated: self._on_task_update(item))
        self.download_tasks[game.gid] = task
        task.start()
        self.show_page("downloads")

    def _on_task_update(self, task):
        try:
            if task.state == "done":
                self.dl_log[task.game.gid] = {"time": datetime.now().isoformat(), "file": task.filename}
                save_json(DOWNLOAD_LOG_FILE, self.dl_log)
                self._add_library(task.game)
            if self.current_page == "downloads":
                try:
                    if self.scroll.winfo_exists():
                        self._load_page("downloads", record=False)
                except: pass
        except Exception as e: log_error(f"task_update: {e}")

    def _toggle_wishlist(self, game):
        if game.gid in self.wishlist:
            self.wishlist.remove(game.gid); messagebox.showinfo(self.t("wishlist"), self.t("wishlist_removed"))
        else:
            self.wishlist.append(game.gid); messagebox.showinfo(self.t("wishlist"), self.t("wishlist_added"))
        save_json(WISHLIST_FILE, self.wishlist)

    def _add_library(self, game):
        if game.gid not in self.library:
            self.library.append(game.gid); save_json(LIBRARY_FILE, self.library)
            try:
                if self.installed_lbl.winfo_exists():
                    self.installed_lbl.configure(text=self.t("installed_count", len(self.library)))
            except: pass
            self._refresh_installed_list()

    def _daily_wheel(self):
        today = datetime.now().date().isoformat()
        if self.settings.get("last_wheel") == today:
            messagebox.showinfo(self.t("wheel_title"), self.t("wheel_daily")); return
        reward = random.choice([50,100,150,200,250,500])
        self.settings["credits"] += reward
        self.settings["last_wheel"] = today
        save_json(SETTINGS_FILE, self.settings)
        try: self.credit_lbl.configure(text=self.t("credits", self.settings["credits"]))
        except: pass
        win = ctk.CTkToplevel(self)
        self._show_window(win)
        win.title(self.t("wheel_title")); win.geometry("360x260"); win.configure(fg_color=C_BG)
        ctk.CTkLabel(win, text="🎡", font=ctk.CTkFont(size=80)).pack(pady=20)
        ctk.CTkLabel(win, text=self.t("wheel_win", reward), font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C_GOLD).pack(pady=8)
        ctk.CTkButton(win, text=self.t("ok"), command=win.destroy).pack(pady=10)

    # ============ DEV LOGIN ============
    def _open_dev_login(self):
        if self._dev_verified:
            messagebox.showinfo(self.t("dev_welcome"), self.t("dev_already")); return
        now = time.time()
        try: locked_until = max(0.0, float(self.lockout.get("until", 0) or 0))
        except (TypeError, ValueError): locked_until = 0.0
        if locked_until > now:
            mins = int((locked_until-now)/60)+1
            messagebox.showwarning(self.t("dev_title"), self.t("dev_locked", mins)); return
        if self.lockout.get("until"):
            self.lockout.pop("until", None)
            save_json(SECURITY_LOCKOUT_FILE, self.lockout)
        win = ctk.CTkToplevel(self)
        self._show_window(win)
        win.title(self.t("dev_title")); win.geometry("460x420"); win.configure(fg_color=C_BG)
        try: win.iconbitmap(str(ICON_FILE))
        except: pass
        win.grab_set()
        ctk.CTkLabel(win, text=self.t("dev_title"), font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C_NEON).pack(pady=(20,8))
        ctk.CTkLabel(win, text=self.t("dev_authorized"), text_color=C_MUTED,
            font=ctk.CTkFont(size=11), wraplength=400).pack()
        pwd_var = ctk.StringVar()
        e = ctk.CTkEntry(win, textvariable=pwd_var, show="•", width=300, height=40,
            placeholder_text=self.t("dev_password_ph"))
        e.pack(pady=16)
        show = {"on":False}
        def eye():
            show["on"] = not show["on"]; e.configure(show="" if show["on"] else "•")
        ctk.CTkButton(win, text="👁️", width=40, height=40, fg_color=C_PANEL2, command=eye).pack()
        msg = ctk.CTkLabel(win, text="", text_color=C_ERR); msg.pack()
        def attempt():
            if verify_password(pwd_var.get(), DEV_LOGIN_HASH):
                self._dev_verified = True
                self.lockout = {}; save_json(SECURITY_LOCKOUT_FILE, self.lockout)
                win.destroy()
                messagebox.showinfo(self.t("dev_welcome"), self.t("dev_active"))
                self.show_page("settings")
            else:
                try: self.lockout["fails"] = max(0, int(self.lockout.get("fails", 0) or 0)) + 1
                except (TypeError, ValueError): self.lockout["fails"] = 1
                if self.lockout["fails"] >= 5:
                    self.lockout["until"] = time.time() + 300
                    self.lockout["fails"] = 0
                    save_json(SECURITY_LOCKOUT_FILE, self.lockout)
                    msg.configure(text=self.t("dev_locked", 5))
                else:
                    msg.configure(text=self.t("dev_wrong") + f" ({self.lockout['fails']}/5)")
                    save_json(SECURITY_LOCKOUT_FILE, self.lockout)
        ctk.CTkButton(win, text=self.t("dev_login"), width=300, height=40, fg_color=C_NEON,
            text_color="#000", command=attempt).pack(pady=8)

    def destroy(self):
        """Kapatmadan önce thread'leri ve pencereleri temizle."""
        self._closing = True
        self._github_token_session = ""
        try:
            if hasattr(self, "_github_token_var"):
                self._github_token_var.set("")
        except Exception:
            pass
        try:
            if self._ui_poll_id is not None:
                self.after_cancel(self._ui_poll_id)
                self._ui_poll_id = None
        except: pass
        try:
            for t in self.download_tasks.values():
                try: t.cancel()
                except: pass
        except: pass
        try:
            for w in list(self._top_windows):
                try: w.destroy()
                except: pass
            self._top_windows.clear()
        except: pass
        try: super().destroy()
        except: pass


if __name__ == "__main__":
    try:
        app = ArdaLauncher()
        app.mainloop()
    except Exception:
        import traceback
        _show_fatal("Başlatma Hatası", traceback.format_exc())