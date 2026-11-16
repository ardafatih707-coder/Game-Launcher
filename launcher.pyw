"""
ARDA LAUNCHER v9.1 ULTIMATE EDITION
Fix: pack() layout for CTkScrollableFrame + in-app modal celebration
New: Daily Wheel, Quests, Sys Requirements, Reviews, Sort Bar
"""

import os, sys, io, json, time, math, hashlib, zipfile, shutil, subprocess, threading, ctypes, tempfile, random, re, base64, webbrowser, traceback
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import customtkinter as ctk
from tkinter import filedialog, messagebox

try: import psutil; PSUTIL_OK = True
except ImportError: PSUTIL_OK = False
try: import winreg; WINREG_OK = True
except ImportError: WINREG_OK = False
try: import py7zr; PY7ZR_OK = True
except ImportError: PY7ZR_OK = False

# ======================================================================
# SABİTLER
# ======================================================================
APP_VERSION = "9.1"
UPDATE_VERSION_URL = "https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/version.json"
UPDATE_CODE_URL = "https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/launcher.pyw"
CATALOG_URL = "https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/catalog.json"
DEFAULT_GH_OWNER = "ardafatih707-coder"
DEFAULT_GH_REPO = "Game-Launcher"
DEFAULT_GH_BRANCH = "main"
DEV_PIN_DEFAULT = "1453"
WELCOME_CREDITS = 10000

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".arda_launcher_config.json")

def _get_base_dir():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f); custom = d.get("base_dir")
                if custom:
                    p = Path(custom); p.mkdir(parents=True, exist_ok=True); return p
    except Exception: pass
    if sys.platform == "win32":
        return Path(os.path.join(os.path.expanduser("~"), "AppData", "Local", "ArdaLauncher"))
    return Path(os.path.expanduser("~")) / ".local" / "share" / "ArdaLauncher"

BASE_DIR = _get_base_dir()
CACHE_COVERS = BASE_DIR / "cache_covers"
PROFILE_CACHE = BASE_DIR / "arda_profile_cache"
MODS_DIR = BASE_DIR / "mods"
DATA_DOSYASI = BASE_DIR / "arda_launcher_data.json"
ICON_DOSYASI = BASE_DIR / "arda_icon.ico"

for _d in (BASE_DIR, CACHE_COVERS, PROFILE_CACHE, MODS_DIR):
    try: _d.mkdir(parents=True, exist_ok=True)
    except Exception: pass

def _get_script_path():
    try:
        if "__file__" in globals():
            p = os.path.abspath(__file__)
            if os.path.exists(p): return p
    except Exception: pass
    try:
        if sys.argv and sys.argv[0] and os.path.exists(sys.argv[0]): return os.path.abspath(sys.argv[0])
    except Exception: pass
    return None

def _temizle_bozuk_onbellek():
    n = 0
    try:
        for f in list(CACHE_COVERS.glob("*.png")):
            try:
                if f.stat().st_size < 5000: f.unlink(); n += 1; continue
                try: Image.open(f).verify()
                except Exception:
                    try: f.unlink(); n += 1
                    except Exception: pass
            except Exception: pass
    except Exception: pass
    if n: print(f"[CACHE] {n} bozuk dosya silindi.")
_temizle_bozuk_onbellek()

def _varsayilan_oyun_dizini():
    p = Path(os.path.join(os.path.expanduser("~"), "ArdaLauncherGames"))
    try: p.mkdir(parents=True, exist_ok=True)
    except Exception: pass
    return p

def _varsayilan_yedek_dizini():
    p = Path(os.path.join(os.path.expanduser("~"), "ArdaLauncherBackups"))
    try: p.mkdir(parents=True, exist_ok=True)
    except Exception: pass
    return p

# ======================================================================
# TEMA
# ======================================================================
TEMALAR = {
    "mavi":    {"ad": "Elektrik Mavisi", "renk": "#3B82F6", "hover": "#2563EB"},
    "yesil":   {"ad": "Zümrüt Yeşili",   "renk": "#10B981", "hover": "#059669"},
    "mor":     {"ad": "Siber Mor",       "renk": "#8B5CF6", "hover": "#7C3AED"},
    "turuncu": {"ad": "Alev Turuncusu",  "renk": "#F97316", "hover": "#EA580C"},
    "kirmizi": {"ad": "Yakut Kırmızısı", "renk": "#EF4444", "hover": "#DC2626"},
    "altin":   {"ad": "Altın Sarısı",    "renk": "#F59E0B", "hover": "#D97706"},
    "galaksi": {"ad": "Galaksi Moru",    "renk": "#9D00FF", "hover": "#7B00CC"},
}
CERCEVELER = {
    "mavi":   {"ad": "Elektrik Mavisi", "renk": "#3B82F6"},
    "altin":  {"ad": "Altın Şampiyon",  "renk": "#F59E0B"},
    "zumrut": {"ad": "Zümrüt Siber",    "renk": "#10B981"},
    "kizil":  {"ad": "Kızıl Ateş",      "renk": "#EF4444"},
    "mor":    {"ad": "Mor Galaksi",     "renk": "#8B5CF6"},
    "beyaz":  {"ad": "Beyaz Işık",      "renk": "#F8FAFC"},
    "turkuaz":{"ad": "Turkuaz Dalga",   "renk": "#06B6D4"},
    "pembe":  {"ad": "Pembe Neon",      "renk": "#EC4899"},
}
BANNER_TEMALARI = [
    {"ad": "Neon Cyber",  "r1": (0,210,255),   "r2": (157,0,255)},
    {"ad": "Sunset",      "r1": (249,115,22),  "r2": (239,68,68)},
    {"ad": "Emerald",     "r1": (16,185,129),  "r2": (59,130,246)},
    {"ad": "Cosmic",      "r1": (30,27,75),    "r2": (157,0,255)},
    {"ad": "Firestorm",   "r1": (127,29,29),   "r2": (249,115,22)},
    {"ad": "Cyberpunk",   "r1": (255,0,128),   "r2": (0,200,255)},
    {"ad": "Aurora",      "r1": (16,185,129),  "r2": (139,92,246)},
    {"ad": "Midnight",    "r1": (12,20,45),    "r2": (75,85,255)},
]
PRESET_AVATARS = [
    {"ad": "Cyber Ninja",     "emoji": "忍", "bg": (30,10,40),  "fg": (157,0,255)},
    {"ad": "Kozmik Astronot", "emoji": "★", "bg": (10,25,60),  "fg": (0,210,255)},
    {"ad": "Neon Kurt",       "emoji": "狼", "bg": (20,30,50),  "fg": (59,130,246)},
    {"ad": "Siber Samuray",   "emoji": "侍", "bg": (50,10,20),  "fg": (239,68,68)},
    {"ad": "Ejderha",         "emoji": "龍", "bg": (60,20,10),  "fg": (249,115,22)},
    {"ad": "Robot",           "emoji": "機", "bg": (30,40,50),  "fg": (148,163,184)},
    {"ad": "Piksel Şövalye",  "emoji": "盾", "bg": (10,40,30),  "fg": (16,185,129)},
    {"ad": "Galaksi Yıldızı", "emoji": "✦", "bg": (25,20,60),  "fg": (139,92,246)},
]
UNVANLAR = ["Yeni Oyuncu", "Gece Kuşu", "Strateji Ustası", "Koleksiyoncu",
            "Speedrunner", "Kaşif", "Arşivci", "Modcu", "Şampiyon", "Galaktik Kaptan"]
CARD_SIZES = {"compact": {"img": (150, 200)}, "standard": {"img": (200, 280)}, "wide": {"img": (260, 340)}}
RENKLER = {
    "arka": "#0B0E14", "yan": "#131822", "kart": "#1A1F2E", "kart_hover": "#232A3D",
    "vurgu": TEMALAR["mavi"]["renk"], "vurgu_hover": TEMALAR["mavi"]["hover"],
    "metin": "#E2E8F0", "soluk": "#94A3B8",
    "yesil": "#22C55E", "kirmizi": "#EF4444", "sari": "#F59E0B", "cizgi": "#1E293B",
    "galaksi": "#9D00FF", "neon_mavi": "#00D2FF", "altin": "#FFD700",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
QUESTS = {
    "daily_scan":    {"ad": "Klasör Tara",       "hedef": 1,  "kredi": 400, "aciklama": "1 klasör taraması yap",      "tip": "daily"},
    "daily_play":    {"ad": "Oyun Oyna",         "hedef": 15, "kredi": 600, "aciklama": "15 dakika oyun oyna",        "tip": "daily"},
    "daily_fav":     {"ad": "Favorilere Ekle",   "hedef": 1,  "kredi": 200, "aciklama": "Bir oyunu favorilere ekle",  "tip": "daily"},
    "daily_explore": {"ad": "Oyun İncele",       "hedef": 2,  "kredi": 300, "aciklama": "2 farklı oyunu incele",       "tip": "daily"},
    "weekly_buy":    {"ad": "Alışveriş",         "hedef": 1,  "kredi": 800, "aciklama": "1 kredili oyun satın al",    "tip": "weekly"},
    "weekly_review": {"ad": "İnceleme Yap",      "hedef": 1,  "kredi": 500, "aciklama": "Bir oyuna yıldız ver",       "tip": "weekly"},
}
WHEEL_REWARDS = [250, 500, 1000, 2500, 5000, 500, 1000, 250, 2500, 500]

# ======================================================================
# YARDIMCILAR
# ======================================================================
def load_json(path, default=None):
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: pass
    return default if default is not None else {}

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e: print(f"[JSON] {e}")

def fmt_bayt(b):
    if b < 1024: return f"{b:.0f} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/1024**2:.2f} MB"
    return f"{b/1024**3:.2f} GB"

def sistem_ram():
    if PSUTIL_OK:
        try: return psutil.virtual_memory().percent
        except Exception: pass
    return 0.0

def toplam_ram_gb():
    if PSUTIL_OK:
        try: return psutil.virtual_memory().total / (1024**3)
        except Exception: pass
    return 8.0

def sistem_cpu_cores():
    if PSUTIL_OK:
        try: return psutil.cpu_count(logical=True) or 4
        except Exception: pass
    return 4

def disk_usage_gb(path):
    try:
        anchor = os.path.splitdrive(str(Path(path).resolve()))[0] + "\\"
        u = shutil.disk_usage(anchor)
        return u.total / (1024**3), u.used / (1024**3), u.free / (1024**3)
    except Exception: return 0.0, 0.0, 0.0

def yuksek_oncelik(exe, cwd):
    proc = subprocess.Popen([exe], cwd=cwd)
    if sys.platform == "win32":
        try:
            h = ctypes.windll.kernel32.OpenProcess(0x0200 | 0x0400, False, proc.pid)
            if h:
                ctypes.windll.kernel32.SetPriorityClass(h, 0x80)
                ctypes.windll.kernel32.CloseHandle(h)
        except Exception: pass
    return proc

def win_desktop_path():
    if sys.platform != "win32": return Path(os.path.expanduser("~")) / "Desktop"
    candidates = []
    try:
        if WINREG_OK:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "Desktop"); winreg.CloseKey(key)
            candidates.append(Path(os.path.expandvars(val)))
    except Exception: pass
    up = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    candidates.append(Path(up) / "Desktop")
    od = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    if od: candidates.append(Path(od) / "Desktop")
    candidates.append(Path(up) / "Masaüstü")
    for c in candidates:
        try:
            if c.exists(): return c
        except Exception: continue
    try:
        candidates[0].mkdir(parents=True, exist_ok=True); return candidates[0]
    except Exception: return Path(os.path.expanduser("~")) / "Desktop"

def _steam_install_path():
    if sys.platform != "win32": return None
    candidates = []
    try:
        if WINREG_OK:
            for hive, kp in [(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
                              (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
                              (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")]:
                try:
                    k = winreg.OpenKey(hive, kp, 0, winreg.KEY_READ)
                    v, _ = winreg.QueryValueEx(k, "InstallPath"); winreg.CloseKey(k)
                    candidates.append(Path(v))
                except Exception: pass
    except Exception: pass
    candidates.append(Path("C:/Program Files (x86)/Steam"))
    candidates.append(Path("C:/Program Files/Steam"))
    for c in candidates:
        try:
            if c.exists(): return c
        except Exception: continue
    return None

def _steam_game_installed(appid):
    steam = _steam_install_path()
    if not steam: return False
    try:
        if (steam / "steamapps" / f"appmanifest_{appid}.acf").exists(): return True
    except Exception: pass
    try:
        vdf = steam / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            text = vdf.read_text(encoding="utf-8", errors="ignore")
            for p in re.findall(r'"path"\s+"([^"]+)"', text):
                try:
                    if (Path(p.replace("\\\\", "\\")) / "steamapps" / f"appmanifest_{appid}.acf").exists():
                        return True
                except Exception: continue
    except Exception: pass
    return False

def _steam_launch(appid):
    try: os.startfile(f"steam://rungameid/{appid}"); return True
    except Exception:
        try: subprocess.Popen(["cmd", "/c", "start", "", f"steam://rungameid/{appid}"], shell=False); return True
        except Exception: return False

def _steam_install(appid):
    try: os.startfile(f"steam://install/{appid}"); return True
    except Exception:
        try: subprocess.Popen(["cmd", "/c", "start", "", f"steam://install/{appid}"], shell=False); return True
        except Exception: return False

# ======================================================================
# KATALOG
# ======================================================================
def _mk(appid, isim, tur, fiyat=0, repo="", exe="", url="", desc="", min_ram=2):
    entry = {
        "isim": isim, "tur": tur, "fiyat": fiyat, "min_ram": min_ram,
        "aciklama": desc or f"{isim} - popüler PC oyunu.",
        "sistem": f"Windows 7+, {min_ram} GB RAM",
        "kapak_urls": [
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900.jpg",
            f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_600x900.jpg",
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
        ],
        "banner_urls": [
            f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
        ],
    }
    if appid: entry["steam_appid"] = appid
    if repo: entry["repo"] = repo
    if exe: entry["exe_adi"] = exe
    if url: entry["url"] = url
    return entry

OYUN_KATALOGU = {
    "cs2":        _mk(730,     "Counter-Strike 2",       "Aksiyon",    0, desc="Valve FPS."),
    "dota2":      _mk(570,     "Dota 2",                 "Strateji",   0, desc="Valve MOBA."),
    "tf2":        _mk(440,     "Team Fortress 2",        "Aksiyon",    0, desc="Takım FPS."),
    "unturned":   _mk(304930,  "Unturned",               "Aksiyon",    0, desc="Voxel hayatta kalma."),
    "brawlhalla": _mk(291550,  "Brawlhalla",             "Aksiyon",    0, desc="Platform dövüş."),
    "paladins":   _mk(444090,  "Paladins",               "Aksiyon",    0, desc="Kahraman FPS."),
    "falloutshelter": _mk(588430, "Fallout Shelter",     "Simülasyon", 0, desc="Vault simülasyonu."),
    "vrchat":     _mk(438100,  "VRChat",                 "Simülasyon", 0, desc="Sosyal VR."),
    "aimlabs":    _mk(714010,  "Aimlabs",                "Araçlar",    0, desc="FPS antrenörü."),
    "stumbleguys":_mk(1677740, "Stumble Guys",           "Yarış",      0, desc="Engel parkuru."),
    "asphaltlegends": _mk(1815780, "Asphalt Legends Unite","Yarış",    0, desc="Yarış oyunu."),
    "mindustry":  _mk(1127400, "Mindustry",              "Strateji",   0, repo="Anuken/Mindustry", exe="Mindustry.exe"),
    "wesnoth":    _mk(599390,  "Battle for Wesnoth",     "Strateji",   0, repo="wesnoth/wesnoth", exe="wesnoth.exe"),
    "endlesssky": _mk(404410,  "Endless Sky",            "RPG",        0, repo="endless-sky/endless-sky", exe="EndlessSky.exe"),
    "shatteredpd":_mk(1769170, "Shattered Pixel Dungeon","Roguelike",  0, repo="00-Evan/shattered-pixel-dungeon", exe="ShatteredPD.exe"),
    "openttd":    _mk(1536610, "OpenTTD",                "Simülasyon", 0, repo="OpenTTD/OpenTTD", exe="openttd.exe"),
    "warzone2100":_mk(1241950, "Warzone 2100",           "Strateji",   0, repo="Warzone2100/warzone2100", exe="warzone2100.exe"),
    "cataclysm":  _mk(2330750, "Cataclysm: DDA",         "RPG",        0, repo="CleverRaven/Cataclysm-DDA", exe="cataclysm-tiles.exe"),
    "tome4":      _mk(259680,  "Tales of Maj'Eyal",      "Roguelike",  0, repo="tome4/tome", exe="t-engine.exe"),
    "ddnet":      _mk(380840,  "DDNet (Teeworlds)",      "Aksiyon",    0, repo="ddnet/ddnet", exe="DDNet.exe"),
    "rocketleague":_mk(252950, "Rocket League",          "Aksiyon",    0, desc="Arabalarla futbol."),
    "warface":    _mk(291480,  "Warface",                "Aksiyon",    0, desc="Taktiksel FPS."),
    "pubg":       _mk(578080,  "PUBG: BATTLEGROUNDS",    "Aksiyon",    8500),
    "apex":       _mk(1172470, "Apex Legends",           "Aksiyon",    9000),
    "warframe":   _mk(230410,  "Warframe",               "RPG",        6500),
    "warthunder": _mk(236390,  "War Thunder",            "Simülasyon", 7000),
    "destiny2":   _mk(1085660, "Destiny 2",              "Aksiyon",    10500),
    "haloinfinite":_mk(1240440,"Halo Infinite",          "Aksiyon",    12000),
    "sims4":      _mk(1222670, "The Sims 4",             "Simülasyon", 8500),
    "pathofexile":_mk(238960,  "Path of Exile",          "RPG",        7500),
    "overwatch2": _mk(2357570, "Overwatch 2",            "Aksiyon",    9500),
    "worldoftanks":_mk(1407200,"World of Tanks",         "Strateji",   6000),
    "worldofwarships":_mk(552990,"World of Warships",    "Strateji",   6000),
    "marvelrivals":_mk(2767030,"Marvel Rivals",          "Aksiyon",    13500),
    "trackmania":  _mk(2225070,"Trackmania",             "Yarış",      5000),
    "smite":       _mk(386360, "SMITE",                  "Strateji",   4500),
    "lostark":     _mk(1599340,"Lost Ark",               "RPG",        9000),
    "albiononline":_mk(761890, "Albion Online",          "RPG",        5500),
    "runescape":   _mk(1343400,"RuneScape",              "RPG",        5000),
    "osrs":        _mk(1343370,"Old School RuneScape",   "RPG",        4500),
    "yugiohmd":    _mk(1449850,"Yu-Gi-Oh! Master Duel",  "Strateji",   5500),
    "marvelsnap":  _mk(1997040,"Marvel Snap",            "Strateji",   5000),
    "efootball":   _mk(1665460,"eFootball",              "Simülasyon", 7000),
    "dcsworld":    _mk(223750, "DCS World",              "Simülasyon", 15000),
    "oncehuman":   _mk(2139460,"Once Human",             "Aksiyon",    11500),
    "deltaforce":  _mk(2507950,"Delta Force",            "Aksiyon",    12500),
    "naraka":      _mk(1203220,"Naraka: Bladepoint",     "Aksiyon",    10000),
    "thefinals":   _mk(2073850,"The Finals",             "Aksiyon",    11000),
    "enlisted":    _mk(2051620,"Enlisted",               "Aksiyon",    8000),
    "crossout":    _mk(386180, "Crossout",               "Aksiyon",    5500),
    "starconflict":_mk(212070, "Star Conflict",          "Aksiyon",    4500),
    "fishingplanet":_mk(380600,"Fishing Planet",         "Simülasyon", 4000),
    "planetside2": _mk(218230, "PlanetSide 2",           "Aksiyon",    6500),
    "eveonline":   _mk(8500,   "EVE Online",             "RPG",        8500),
    "trove":       _mk(304050, "Trove",                  "RPG",        4000),
    "guildwars2":  _mk(1284210,"Guild Wars 2",           "RPG",        9500),
}

BASARIMLAR = {
    "first_step":   {"ad": "İlk Adım",       "ikon": "🎯", "aciklama": "İlk oyunu kur",       "kredi": 500},
    "marathon":     {"ad": "Maratoncu",      "ikon": "⏱️", "aciklama": "1 saat oyun oyna",     "kredi": 500},
    "archivist":    {"ad": "Arşivci",        "ikon": "📚", "aciklama": "5 oyun ekle",          "kredi": 500},
    "safe_player":  {"ad": "Güvenli Oyuncu", "ikon": "🛡️", "aciklama": "İlk yedeğini al",      "kredi": 500},
    "collector":    {"ad": "Koleksiyoncu",   "ikon": "💎", "aciklama": "10 oyun ekle",         "kredi": 500},
    "customizer":   {"ad": "Kişiselleştir",  "ikon": "🎨", "aciklama": "Profilini düzenle",    "kredi": 500},
    "downloader":   {"ad": "İndirici",       "ikon": "⬇️", "aciklama": "3 indirme tamamla",    "kredi": 500},
    "explorer":     {"ad": "Kaşif",          "ikon": "🔍", "aciklama": "Klasör tara",          "kredi": 500},
    "booster":      {"ad": "Hız Tutkunu",    "ikon": "🚀", "aciklama": "Yüksek öncelikle başlat","kredi": 500},
    "theme_master": {"ad": "Tema Ustası",    "ikon": "🌈", "aciklama": "Tema değiştir",        "kredi": 500},
    "first_purchase":{"ad":"Alışverişçi",    "ikon": "🛒", "aciklama": "İlk kredili oyunu al", "kredi": 1000},
    "wishlister":   {"ad": "Hayalperest",    "ikon": "⭐", "aciklama": "İlk istek listesi",    "kredi": 300},
    "reviewer":     {"ad": "Eleştirmen",     "ikon": "📝", "aciklama": "İlk inceleme",         "kredi": 400},
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ======================================================================
# İKON
# ======================================================================
def _draw_star(d, cx, cy, size, fill):
    p = [(cx, cy - size), (cx + size*0.18, cy - size*0.18), (cx + size, cy),
         (cx + size*0.18, cy + size*0.18), (cx, cy + size), (cx - size*0.18, cy + size*0.18),
         (cx - size, cy), (cx - size*0.18, cy - size*0.18)]
    d.polygon(p, fill=fill)

def icon_olustur():
    if ICON_DOSYASI.exists():
        try: Image.open(ICON_DOSYASI).verify(); return
        except Exception:
            try: ICON_DOSYASI.unlink()
            except Exception: pass
    sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
    try:
        S = 256
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, S-1, S-1), radius=52, fill=255)
        bg = Image.new("RGBA", (S, S), (4, 7, 20, 255))
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0)); img.paste(bg, (0, 0), mask)
        d = ImageDraw.Draw(img); random.seed(42)
        for _ in range(70):
            x, y = random.randint(8, S-8), random.randint(8, S-8)
            if mask.getpixel((x, y)) > 100:
                r = random.choice([0.5, 0.8, 1.2]); b = random.randint(160, 255)
                d.ellipse((x-r, y-r, x+r, y+r), fill=(b, b, min(255, b+15), 220))
        grad = Image.new("RGB", (S, S)); gd = ImageDraw.Draw(grad)
        for x in range(S):
            t = x / S
            gd.line([(x, 0), (x, S)], fill=(int(157*t), int(210*(1-t)), 255))
        fm = Image.new("L", (S, S), 0)
        ImageDraw.Draw(fm).rounded_rectangle((10, 10, S-11, S-11), radius=44, outline=255, width=6)
        frame = Image.new("RGBA", (S, S), (0, 0, 0, 0)); frame.paste(grad, (0, 0), fm)
        img = Image.alpha_composite(img, frame); d = ImageDraw.Draw(img)
        cx, cy = S // 2, S // 2
        _draw_star(d, cx, cy, 72, (255, 255, 255, 255))
        _draw_star(d, cx, cy, 47, (200, 230, 255, 255))
        _draw_star(d, cx, cy, 25, (0, 210, 255, 255))
        img.save(ICON_DOSYASI, format="ICO", sizes=sizes)
    except Exception as e: print(f"[ICON] {e}")
icon_olustur()

# ======================================================================
# GÖRSEL
# ======================================================================
PALETLER = {
    "Strateji": [(20,25,60),(60,30,90),(120,60,40)],
    "RPG": [(30,10,50),(100,40,80),(220,100,60)],
    "Roguelike": [(10,10,20),(60,20,60),(200,50,80)],
    "Yarış": [(10,30,60),(60,100,150),(240,180,60)],
    "Simülasyon": [(20,40,30),(60,120,100),(180,200,100)],
    "Aksiyon": [(40,10,10),(150,40,40),(240,120,40)],
    "Araçlar": [(20,20,40),(60,60,100),(150,100,200)],
}

def sinematik_kapak_uret(isim, tur, boyut):
    w, h = boyut; renkler = PALETLER.get(tur, PALETLER["Araçlar"])
    img = Image.new("RGB", (w, h)); d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        if t < 0.5:
            t2 = t * 2
            c = tuple(int(renkler[0][i] * (1 - t2) + renkler[1][i] * t2) for i in range(3))
        else:
            t2 = (t - 0.5) * 2
            c = tuple(int(renkler[1][i] * (1 - t2) + renkler[2][i] * t2) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    try:
        font_size = int(h * 0.08); font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        try: font = ImageFont.truetype("arial.ttf", font_size)
        except Exception: font = ImageFont.load_default()
    bb = d.textbbox((0, 0), isim[:18], font=font)
    tw = bb[2] - bb[0]
    d.text(((w - tw) / 2 + 2, h * 0.75 + 2), isim[:18], font=font, fill=(0, 0, 0))
    d.text(((w - tw) / 2, h * 0.75), isim[:18], font=font, fill=(255, 255, 255))
    return img

def akilli_kirp(img, boyut):
    try:
        try: resample = Image.Resampling.LANCZOS
        except AttributeError: resample = Image.LANCZOS
        return ImageOps.fit(img, boyut, method=resample)
    except Exception:
        w, h = img.size; o = w / h; hedef_o = boyut[0] / boyut[1]
        if o > hedef_o:
            yw = int(h * hedef_o); s = (w - yw) // 2; img = img.crop((s, 0, s + yw, h))
        else:
            yh = int(w / hedef_o); u = (h - yh) // 2; img = img.crop((0, u, w, u + yh))
        try: return img.resize(boyut, Image.Resampling.LANCZOS)
        except AttributeError: return img.resize(boyut, Image.LANCZOS)

def banner_overlay(img):
    w, h = img.size; ov = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(h):
        o = y / h
        a = int(180 * max(0, o - 0.30) / 0.70) if o > 0.30 else 0
        d.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

def yuvarlak_maske(img, boyut):
    img = akilli_kirp(img, (boyut, boyut))
    m = Image.new("L", (boyut, boyut), 0)
    ImageDraw.Draw(m).ellipse((0, 0, boyut, boyut), fill=255)
    out = Image.new("RGBA", (boyut, boyut), (0, 0, 0, 0))
    out.paste(img, (0, 0), m); return out

def cerceve_ekle(img, renk, kalinlik=4):
    w, h = img.size
    out = Image.new("RGBA", (w + kalinlik*2, h + kalinlik*2), (0, 0, 0, 0))
    d = ImageDraw.Draw(out); d.ellipse((0, 0, w + kalinlik*2, h + kalinlik*2), fill=renk)
    out.paste(img, (kalinlik, kalinlik), img if img.mode == "RGBA" else None); return out

def _diskten_resim_bul(urls):
    if not urls: return None
    for url in urls:
        cp = CACHE_COVERS / f"{hashlib.md5(url.encode()).hexdigest()}.png"
        try:
            if cp.exists() and cp.stat().st_size >= 5000:
                Image.open(cp).verify()
                return Image.open(cp).convert("RGB")
        except Exception: continue
    return None

def _resim_indir_dogrula(urls, cache_dir=None):
    if not urls: return None
    for url in urls:
        cache_path = None
        if cache_dir is not None:
            cache_path = cache_dir / f"{hashlib.md5(url.encode()).hexdigest()}.png"
            if cache_path.exists():
                try:
                    if cache_path.stat().st_size >= 5000:
                        Image.open(cache_path).verify()
                        return Image.open(cache_path).convert("RGB")
                except Exception:
                    try: cache_path.unlink()
                    except Exception: pass
        try:
            r = requests.get(url, timeout=20, headers=HEADERS, allow_redirects=True)
            if r.status_code != 200 or len(r.content) < 5000: continue
            Image.open(io.BytesIO(r.content)).verify()
            raw = Image.open(io.BytesIO(r.content))
            if raw.mode in ("RGBA", "LA", "P"):
                raw = raw.convert("RGBA")
                bg = Image.new("RGB", raw.size, (26, 31, 46))
                try: bg.paste(raw, mask=raw.split()[-1]); img = bg
                except Exception: img = raw.convert("RGB")
            else: img = raw.convert("RGB")
            if cache_path is not None:
                try: img.save(cache_path, "PNG")
                except Exception: pass
            return img
        except Exception: continue
    return None

def preset_avatar_olustur(emoji, bg, fg, boyut=110):
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / (S - 1)
        c = tuple(int(bg[i] * (1 - t) + fg[i] * t * 0.6) for i in range(3))
        d.line([(0, y), (S, y)], fill=c + (255,))
    d.ellipse((30, 30, S-30, S-30), outline=fg + (200,), width=6)
    try:
        try: font = ImageFont.truetype("arialbd.ttf", 110)
        except Exception: font = ImageFont.truetype("arial.ttf", 110)
    except Exception: font = ImageFont.load_default()
    bb = d.textbbox((0, 0), emoji, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((S - tw) / 2 - bb[0], (S - th) / 2 - bb[1] - 8), emoji, font=font, fill=(255, 255, 255))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, S, S), fill=255)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out.resize((boyut, boyut), Image.LANCZOS)

# ======================================================================
# AUTO-UPDATER + PUBLISHER + SYNC + STORE
# ======================================================================
class AutoUpdater:
    @staticmethod
    def is_placeholder(url):
        if not url: return True
        return url.strip().lower() in ("https://githubusercontent.com", "https://raw.githubusercontent.com",
                                        "https://github.com", "https://github.com/")
    @staticmethod
    def parse_version(v):
        try:
            parts = []
            for x in str(v).replace("v","").replace("V","").split("."):
                digits = "".join(c for c in x if c.isdigit())
                if digits: parts.append(int(digits))
            return parts if parts else [0]
        except Exception: return [0]
    @staticmethod
    def check(url, current, timeout=5):
        if AutoUpdater.is_placeholder(url): return None
        try:
            r = requests.get(url, timeout=timeout, headers={**HEADERS, "Accept": "application/json"})
            if r.status_code != 200: return None
            try: data = r.json()
            except Exception: return None
            if not isinstance(data, dict): return None
            remote = str(data.get("version", "")).strip()
            if remote and AutoUpdater.parse_version(remote) > AutoUpdater.parse_version(current):
                return data
            return None
        except Exception: return None

class GitHubPublisher:
    def __init__(self, token, owner, repo, branch="main"):
        self.token = token.strip(); self.owner = owner.strip()
        self.repo = repo.strip(); self.branch = (branch or "main").strip()
        self.api = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        self.headers = {"Authorization": f"token {self.token}",
                        "Accept": "application/vnd.github+json",
                        "User-Agent": "ArdaLauncher-Publisher/9.1"}
    def _get_sha(self, path):
        try:
            r = requests.get(f"{self.api}/{path}?ref={self.branch}", headers=self.headers, timeout=12)
            if r.status_code == 200: return r.json().get("sha")
            return None
        except Exception: return None
    def _put_file(self, path, content_bytes, message):
        sha = self._get_sha(path)
        payload = {"message": message, "content": base64.b64encode(content_bytes).decode("ascii"),
                   "branch": self.branch}
        if sha: payload["sha"] = sha
        r = requests.put(f"{self.api}/{path}", headers=self.headers, json=payload, timeout=45)
        if r.status_code in (200, 201): return {"ok": True}
        try: err = r.json().get("message", r.text[:200])
        except Exception: err = r.text[:200]
        return {"ok": False, "status": r.status_code, "error": err}
    def publish_all(self, script_path, new_version, notes, catalog_data=None, progress_cb=None):
        if progress_cb: progress_cb("Hazırlanıyor...", 10)
        try:
            with open(script_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            content = re.sub(r'^APP_VERSION\s*=\s*"[^"]*"', f'APP_VERSION = "{new_version}"', content, flags=re.MULTILINE)
            ver_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/version.json"
            code_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/launcher.pyw"
            content = re.sub(r'^UPDATE_VERSION_URL\s*=\s*"[^"]*"', f'UPDATE_VERSION_URL = "{ver_url}"', content, flags=re.MULTILINE)
            content = re.sub(r'^UPDATE_CODE_URL\s*=\s*"[^"]*"', f'UPDATE_CODE_URL = "{code_url}"', content, flags=re.MULTILINE)
        except Exception as e:
            return {"ok": False, "step": "read", "error": str(e)}
        if progress_cb: progress_cb("launcher.pyw...", 30)
        r1 = self._put_file("launcher.pyw", content.encode("utf-8"), f"ARDA LAUNCHER v{new_version}")
        if not r1.get("ok"): return {"ok": False, "step": "launcher.pyw", **r1}
        ver_data = {"version": new_version, "notes": notes or f"v{new_version}",
                    "url": code_url, "released": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        if progress_cb: progress_cb("version.json...", 55)
        r2 = self._put_file("version.json", json.dumps(ver_data, indent=2, ensure_ascii=False).encode("utf-8"),
                            f"v{new_version} version")
        if not r2.get("ok"): return {"ok": False, "step": "version.json", **r2}
        if progress_cb: progress_cb("installer.bat...", 75)
        try:
            bat = generate_installer_bat(self.owner, self.repo, self.branch).encode("utf-8")
            r3 = self._put_file("ArdaLauncher_Installer.bat", bat, f"v{new_version} installer")
            if not r3.get("ok"): return {"ok": False, "step": "installer", **r3}
        except Exception as e: return {"ok": False, "step": "installer", "error": str(e)}
        if catalog_data is not None:
            if progress_cb: progress_cb("catalog.json...", 90)
            try:
                cat_bytes = json.dumps(catalog_data, indent=2, ensure_ascii=False).encode("utf-8")
                r4 = self._put_file("catalog.json", cat_bytes, f"v{new_version} catalog")
                if not r4.get("ok"): return {"ok": False, "step": "catalog", **r4}
            except Exception as e: return {"ok": False, "step": "catalog", "error": str(e)}
        if progress_cb: progress_cb("Tümü yüklendi ✓", 100)
        return {"ok": True, "version": new_version}

def generate_installer_bat(owner=DEFAULT_GH_OWNER, repo=DEFAULT_GH_REPO, branch=DEFAULT_GH_BRANCH):
    owner = (owner or DEFAULT_GH_OWNER).strip(); repo = (repo or DEFAULT_GH_REPO).strip()
    branch = (branch or DEFAULT_GH_BRANCH).strip()
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/launcher.pyw"
    return (
        "@echo off\nsetlocal EnableDelayedExpansion\ntitle ARDA LAUNCHER Installer\ncolor 0B\n"
        "echo [1/5] Python check...\npython --version >nul 2>&1\nif %errorlevel% equ 0 goto :STEP2\n"
        "winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements\n"
        ":STEP2\necho [2/5] Libraries...\npython -m pip install --upgrade pip >nul 2>&1\n"
        "python -m pip install --upgrade customtkinter requests pillow psutil py7zr\n"
        ":STEP3\necho [3/5] Download...\n"
        "set \"INSTALL_DIR=%LOCALAPPDATA%\\ArdaLauncher\"\nif not exist \"%INSTALL_DIR%\" mkdir \"%INSTALL_DIR%\"\n"
        f"set \"LAUNCHER_URL={raw_url}\"\n"
        "powershell -NoProfile -Command \"try {{ Invoke-WebRequest -Uri '%LAUNCHER_URL%' -OutFile '%INSTALL_DIR%\\launcher.pyw' -UseBasicParsing; exit 0 }} catch {{ exit 1 }}\"\n"
        ":STEP4\necho [4/5] Launching...\n"
        "where pythonw >nul 2>&1\nif %errorlevel% equ 0 (start \"\" pythonw \"%INSTALL_DIR%\\launcher.pyw\") else (start \"\" python \"%INSTALL_DIR%\\launcher.pyw\")\n"
        ":STEP5\necho SUCCESS!\npause\n"
    )

class CatalogSync:
    @staticmethod
    def fetch(url, timeout=8):
        if not url or "githubusercontent.com" == url.strip().lower(): return None
        try:
            r = requests.get(url, timeout=timeout, headers={**HEADERS, "Accept": "application/json"})
            if r.status_code != 200: return None
            try: data = r.json()
            except Exception: return None
            if not isinstance(data, dict): return None
            extra = data.get("extra_games", {})
            return extra if isinstance(extra, dict) else None
        except Exception: return None

class SteamStore:
    @staticmethod
    def search(query, timeout=8):
        try:
            from urllib.parse import quote
            q = quote(query)
            url = f"https://store.steampowered.com/api/storesearch/?term={q}&l=turkish&cc=TR"
            r = requests.get(url, timeout=timeout, headers=HEADERS)
            if r.status_code != 200: return []
            items = r.json().get("items", [])
            return [{"appid": int(i.get("id",0)), "name": i.get("name","?")} for i in items[:12]]
        except Exception: return []

# ======================================================================
# İNDİRME MOTORU
# ======================================================================
class DownloadEngine:
    def __init__(self, app):
        self.app = app; self.aktif = {}; self.lock = threading.Lock()
    def baslat(self, oid, oyun):
        with self.lock:
            if oid in self.aktif: return
            self.aktif[oid] = {"durum": "hazirlaniyor", "iptal": False, "duraklat": False,
                               "indirilen": 0, "toplam": 0, "hiz": 0, "eta": 0}
        threading.Thread(target=self._indir, args=(oid, oyun), daemon=True).start()
    def duraklat(self, oid):
        with self.lock:
            if oid in self.aktif: self.aktif[oid]["duraklat"] = True; self.aktif[oid]["durum"] = "duraklatildi"
    def devam(self, oid, oyun):
        with self.lock:
            if oid in self.aktif and self.aktif[oid]["durum"] == "duraklatildi":
                self.aktif[oid]["duraklat"] = False; self.aktif[oid]["durum"] = "indiriliyor"
                threading.Thread(target=self._indir, args=(oid, oyun), daemon=True).start()
    def iptal(self, oid):
        with self.lock:
            if oid in self.aktif: self.aktif[oid]["iptal"] = True; self.aktif[oid]["duraklat"] = False
    def _indir(self, oid, oyun):
        hedef = self.app.oyunlar_dizini / oid; hedef.mkdir(parents=True, exist_ok=True)
        part = hedef / f"{oid}.part"
        speed_limit = float(self.app.veri.get("settings", {}).get("download_speed_limit", 0))
        auto_extract = bool(self.app.veri.get("settings", {}).get("auto_extract", True))
        try:
            self.app.after(0, lambda: self.app.detay_durum_metni(oid, "Paket aranıyor..."))
            asset = None
            if oyun.get("url"):
                asset = {"name": oyun["url"].split("/")[-1], "url": oyun["url"], "size": 0}
            elif oyun.get("repo"):
                asset = self._github_asset(oyun["repo"])
            if not asset:
                if oyun.get("steam_appid"):
                    self.app.after(0, lambda a=oyun["steam_appid"]: self.app._steam_install_action(a))
                    with self.lock:
                        if oid in self.aktif: del self.aktif[oid]
                    return
                raise RuntimeError("Paket bulunamadı.")
            with self.lock:
                if oid in self.aktif: self.aktif[oid]["durum"] = "indiriliyor"
            mevcut = part.stat().st_size if part.exists() else 0
            h = dict(HEADERS)
            if mevcut > 0: h["Range"] = f"bytes={mevcut}-"
            r = requests.get(asset["url"], stream=True, timeout=60, headers=h, allow_redirects=True)
            r.raise_for_status()
            toplam = int(r.headers.get("content-length", 0)) + mevcut or asset.get("size", 0)
            with open(part, "ab" if mevcut else "wb") as f:
                indirilen, son_t, son_i = mevcut, time.time(), mevcut
                for chunk in r.iter_content(chunk_size=16384):
                    if not chunk: continue
                    with self.lock:
                        if oid not in self.aktif or self.aktif[oid]["iptal"]: return
                        while self.aktif[oid]["duraklat"] and not self.aktif[oid]["iptal"]: time.sleep(0.15)
                        if self.aktif[oid]["iptal"]: return
                    f.write(chunk); indirilen += len(chunk); simdi = time.time()
                    if simdi - son_t >= 0.5:
                        hiz = (indirilen - son_i) / (simdi - son_t) / (1024**2)
                        yuzde = indirilen / toplam if toplam else 0
                        eta = ((toplam - indirilen) / (hiz * 1024**2)) if hiz > 0 else 0
                        with self.lock:
                            if oid in self.aktif:
                                self.aktif[oid].update({"indirilen": indirilen, "toplam": toplam, "hiz": hiz, "eta": eta})
                        self.app.after(0, lambda y=yuzde, hz=hiz, i=indirilen, t=toplam, e=eta:
                                       self.app.detay_ilerleme(oid, y, hz, i, t, e))
                        son_t, son_i = simdi, indirilen
            if auto_extract:
                ok = self._arsiv_cikar(part, hedef)
                if ok:
                    try: part.unlink()
                    except Exception: pass
                elif not zipfile.is_zipfile(part) and part.suffix.lower() not in (".7z", ".zip"):
                    hedef_exe = hedef / oyun.get("exe_adi", "game.exe")
                    try:
                        if hedef_exe.exists(): hedef_exe.unlink()
                        shutil.move(str(part), str(hedef_exe))
                    except Exception: pass
            exe_yolu = None; aranan = oyun.get("exe_adi", "")
            if aranan:
                for p in [hedef / aranan] + list(hedef.rglob(aranan)):
                    if p.exists(): exe_yolu = p; break
            if not exe_yolu:
                exes = list(hedef.rglob("*.exe"))
                if exes:
                    exes.sort(key=lambda x: x.stat().st_size, reverse=True); exe_yolu = exes[0]
            if not exe_yolu: raise FileNotFoundError(".exe bulunamadı.")
            with self.lock:
                if oid in self.aktif: del self.aktif[oid]
            self.app.after(0, lambda ep=exe_yolu: self.app.indirme_basarili(oid, ep, asset["name"]))
        except Exception as e:
            with self.lock:
                if oid in self.aktif: self.aktif[oid]["durum"] = "hata"
            err = str(e)
            self.app.after(0, lambda err=err: self.app.indirme_hatali(oid, err))
    @staticmethod
    def _github_asset(repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/releases/latest",
                             timeout=15, headers={**HEADERS, "Accept": "application/vnd.github+json"})
            if r.status_code == 200:
                data = r.json()
                for a in data.get("assets", []):
                    n = a["name"].lower()
                    if (n.endswith(".zip") or n.endswith(".7z") or n.endswith(".exe")) and ("win" in n or "x64" in n):
                        return {"name": a["name"], "url": a["browser_download_url"], "size": a.get("size", 0)}
                for a in data.get("assets", []):
                    if a["name"].lower().endswith((".zip", ".7z")):
                        return {"name": a["name"], "url": a["browser_download_url"], "size": a.get("size", 0)}
        except Exception: pass
        return None
    @staticmethod
    def _arsiv_cikar(arc, dst):
        dst.mkdir(parents=True, exist_ok=True)
        if zipfile.is_zipfile(arc):
            try:
                with zipfile.ZipFile(arc, "r") as z: z.extractall(dst); return True
            except Exception: pass
        if arc.suffix.lower() == ".7z" and PY7ZR_OK:
            try:
                with py7zr.SevenZipFile(arc, mode="r") as z: z.extractall(dst); return True
            except Exception: pass
        return False

# ======================================================================
# OYUN KARTI
# ======================================================================
class OyunKarti(ctk.CTkFrame):
    def __init__(self, master, oid, oyun, app, favori=False):
        super().__init__(master, corner_radius=12, fg_color=RENKLER["kart"], cursor="hand2")
        self.oid, self.oyun, self.app = oid, oyun, app
        size_key = app.veri.get("settings", {}).get("card_size", "standard")
        dims = CARD_SIZES.get(size_key, CARD_SIZES["standard"]); w, h = dims["img"]
        self.kapak = ctk.CTkLabel(self, text="", width=w, height=h)
        self.kapak.pack(padx=10, pady=(10, 5))
        self.kapak.bind("<Button-1>", lambda e: self.app.oyun_detay_goster(oid))
        self.app.gorsel_yukle_guvenli(self.kapak, oid, "kapak", oyun.get("kapak_urls", []), (w, h),
                                       oyun["isim"], oyun["tur"], overlay=False)
        ctk.CTkLabel(self, text=oyun["isim"], font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"], wraplength=w+10).pack(padx=8, anchor="w")
        fiyat = oyun.get("fiyat", 0)
        if fiyat == 0:
            price_text = "🆓 BEDAVA"; price_color = RENKLER["yesil"]
        else:
            price_text = f"💎 {fiyat:,} Kredi"; price_color = RENKLER["altin"]
        ctk.CTkLabel(self, text=price_text, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=price_color).pack(padx=8, pady=(0, 10), anchor="w")
        self.fav_btn = ctk.CTkButton(self, text="❤️" if favori else "🤍", width=30, height=30,
            fg_color=RENKLER["yan"], hover_color=RENKLER["kart_hover"], font=ctk.CTkFont(size=14),
            command=self._fav)
        self.fav_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")
        self.bind("<Enter>", lambda e: self.configure(fg_color=RENKLER["kart_hover"]))
        self.bind("<Leave>", lambda e: self.configure(fg_color=RENKLER["kart"]))
    def _fav(self): self.app.favori_degistir(self.oid)

# ======================================================================
# ANA UYGULAMA
# ======================================================================
class ArdaLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"ARDA LAUNCHER v{APP_VERSION} ULTIMATE")
        self.geometry("1500x950"); self.minsize(1280, 820)
        self.configure(fg_color=RENKLER["arka"])
        self.image_refs = {}
        self._scroll_positions = {}
        self._hero_paused = False
        self._hero_index = 0
        self.hero_ids = []
        self.hero_banner = None
        self.hero_title_lbl = None
        self.hero_desc_lbl = None
        self.hero_incele_btn = None
        self.hero_dots = None
        self.hero_thumbs_frame = None
        self._nav_history = []
        self._nav_index = -1
        self._animations_enabled = True
        self._update_info = None
        self._dev_pin = DEV_PIN_DEFAULT
        self._gozat_sort = "popular"
        self._celebration_overlay = None
        self._wheel_overlay = None
        self._pencere_ikonu_uygula()

        self.veri = load_json(DATA_DOSYASI, {})
        self.veri.setdefault("profil", {
            "ad": "Arda", "etiket": "1453", "unvan": "Yeni Oyuncu", "biyografi": "ARDA Launcher kullanıcısı.",
            "durum": "Çevrimiçi", "avatar_yolu": "", "banner_yolu": "", "banner_tema": 0,
            "cerceve": "mavi", "avatar_preset": 0, "renk": "#3B82F6",
            "xp": 0, "seviye": 1, "rozetler": [], "vitrin_oyun": "", "sabit_rozetler": [],
            "kredi": WELCOME_CREDITS, "ilk_giris_odulu_alindi": False,
            "son_gunluk_odul": "",
        })
        self.veri.setdefault("oyunlar", {})
        self.veri.setdefault("eklenen_oyunlar", {})
        self.veri.setdefault("satın_alınan", [])
        self.veri.setdefault("istek_listesi", [])
        self.veri.setdefault("incelemeler", {})
        self.veri.setdefault("tema", "galaksi")
        self.veri.setdefault("son_aktiviteler", [])
        self.veri.setdefault("indirme_sayaci", 0)
        self.veri.setdefault("desktop_shortcut_created", False)
        self.veri.setdefault("gunluk_oynama", {})
        self.veri.setdefault("koleksiyonlar", {})
        self.veri.setdefault("cark_son", 0)
        self.veri.setdefault("cark_toplam_kazanc", 0)
        self.veri.setdefault("gorevler", {"gunluk_tarih": "", "ilerleme": {}, "alinan": []})
        self.veri.setdefault("dev", {"owner": DEFAULT_GH_OWNER, "repo": DEFAULT_GH_REPO,
                                     "token": "", "branch": DEFAULT_GH_BRANCH,
                                     "next_version": "", "notes": "", "pin": DEV_PIN_DEFAULT})
        self.veri.setdefault("settings", {
            "download_speed_limit": 0, "auto_extract": True, "download_sound": True,
            "startup_enabled": False, "game_booster": True, "minimize_on_play": False,
            "restore_after_game": True, "monitor_refresh": 2000, "card_size": "standard",
            "animations_enabled": True, "hide_adult": False, "opacity": 1.0,
            "ui_sounds": True, "desktop_notifications": True, "daily_reminder": True,
            "auto_backup_freq": "off",
        })
        self.veri.setdefault("indirme_dizini", str(_varsayilan_oyun_dizini()))
        self.veri.setdefault("yedek_dizini", str(_varsayilan_yedek_dizini()))

        self._dev_pin = self.veri["dev"].get("pin", DEV_PIN_DEFAULT)
        self._animations_enabled = self.veri["settings"].get("animations_enabled", True)

        self.kutuphane = self.veri
        self.oyunlar_dizini = Path(self.veri["indirme_dizini"])
        self.yedek_dizini = Path(self.veri["yedek_dizini"])
        try:
            self.oyunlar_dizini.mkdir(parents=True, exist_ok=True)
            self.yedek_dizini.mkdir(parents=True, exist_ok=True)
        except Exception: pass

        self.oyunlar = dict(OYUN_KATALOGU)
        for oid, o in self.veri["eklenen_oyunlar"].items(): self.oyunlar[oid] = o

        self.secili_oyun = None
        self.aktif_sayfa = "anasayfa"
        self.arama = ""
        self.download_engine = DownloadEngine(self)
        self._monitor_job = None
        self._tema_uygula(self.veri["tema"])

        # GRID WEIGHTS (v9.1 fix)
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=60)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0, minsize=26)

        self._build_top_bar()
        self._build_sidebar()
        self._build_main()
        self._bind_shortcuts()
        self.sayfa_degistir("anasayfa")
        self._sistem_monitor()
        self._auto_slider()
        save_json(DATA_DOSYASI, self.veri)
        self.after(1500, self._ilk_kisayol_olustur)
        self.after(3000, lambda: threading.Thread(target=self._auto_update_check, daemon=True).start())
        self.after(3500, lambda: threading.Thread(target=self._sync_catalog, daemon=True).start())
        self.after(800, self._first_login_check)

    def _bind_shortcuts(self):
        try:
            self.bind_all("<Control-k>", lambda e: self.arama_entry.focus_set())
            self.bind_all("<Control-K>", lambda e: self.arama_entry.focus_set())
            self.bind_all("<Control-Shift-D>", lambda e: self._open_pin_dialog())
            self.bind_all("<Control-Shift-d>", lambda e: self._open_pin_dialog())
        except Exception: pass

    def _first_login_check(self):
        p = self.veri["profil"]
        if not p.get("ilk_giris_odulu_alindi", False):
            p["kredi"] = p.get("kredi", 0) + WELCOME_CREDITS
            p["ilk_giris_odulu_alindi"] = True
            save_json(DATA_DOSYASI, self.veri)
            self._kredi_guncelle()
            self._show_celebration_overlay()
        else:
            bugun = datetime.now().strftime("%Y-%m-%d")
            if p.get("son_gunluk_odul", "") != bugun:
                p["kredi"] = p.get("kredi", 0) + 250
                p["son_gunluk_odul"] = bugun
                save_json(DATA_DOSYASI, self.veri)
                self._kredi_guncelle()
                self.durum("🎁 Günlük +250 Kredi kazandınız!")
        self._quest_reset_if_needed()

    # ============ IN-APP OVERLAY CELEBRATION ============
    def _show_celebration_overlay(self):
        try:
            if self._celebration_overlay is not None:
                try: self._celebration_overlay.destroy()
                except Exception: pass
            overlay_bg = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
            overlay_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
            card = ctk.CTkFrame(overlay_bg, corner_radius=24, border_width=4, border_color="#FFD700",
                                 fg_color="#131822", width=620, height=400)
            card.place(relx=0.5, rely=0.5, anchor="center")
            card.pack_propagate(False)
            ctk.CTkLabel(card, text="🎉", font=ctk.CTkFont(size=72)).pack(pady=(30, 10))
            ctk.CTkLabel(card, text="TEBRİKLER 10000 KREDİ KAZANDINIZ İYİ OYUNLAR!",
                         font=ctk.CTkFont(size=20, weight="bold"),
                         text_color="#FFD700", wraplength=560, justify="center").pack(padx=30, pady=10)
            ctk.CTkLabel(card, text="Başlangıç hediyen olan 10.000 Kredi hesabına eklendi.\n"
                                     "Mağazadaki oyunları hemen keşfetmeye başlayabilirsin!",
                         font=ctk.CTkFont(size=13), text_color=RENKLER["soluk"],
                         wraplength=560, justify="center").pack(padx=30, pady=(10, 20))
            def kapat_ve_git():
                try: overlay_bg.destroy()
                except Exception: pass
                self._celebration_overlay = None
                self.sayfa_degistir("gozat")
            ctk.CTkButton(card, text="🛒 Mağazaya Git", height=48, width=220,
                          fg_color="#FFD700", hover_color="#D4AF37",
                          text_color="#0B0E14",
                          font=ctk.CTkFont(size=15, weight="bold"),
                          command=kapat_ve_git).pack(pady=(10, 25))
            self._celebration_overlay = overlay_bg
        except Exception as e:
            traceback.print_exc()

    # ============ NAV ============
    def _nav_push(self, sayfa):
        if self._nav_index < len(self._nav_history) - 1:
            self._nav_history = self._nav_history[:self._nav_index + 1]
        self._nav_history.append(sayfa)
        self._nav_index = len(self._nav_history) - 1
    def _nav_back(self):
        if self._nav_index > 0:
            self._nav_index -= 1
            self.sayfa_degistir(self._nav_history[self._nav_index], push_history=False)
    def _nav_forward(self):
        if self._nav_index < len(self._nav_history) - 1:
            self._nav_index += 1
            self.sayfa_degistir(self._nav_history[self._nav_index], push_history=False)

    # ============ TOPBAR ============
    def _build_top_bar(self):
        self.topbar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#0F1320")
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(2, weight=1)

        nav_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        nav_frame.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        ctk.CTkButton(nav_frame, text="◀", width=36, height=36, fg_color="#1A1F2E",
                      hover_color="#232A3D", command=self._nav_back).pack(side="left", padx=2)
        ctk.CTkButton(nav_frame, text="▶", width=36, height=36, fg_color="#1A1F2E",
                      hover_color="#232A3D", command=self._nav_forward).pack(side="left", padx=2)

        self.arama_entry = ctk.CTkEntry(
            self.topbar, placeholder_text="🔎  Oyun ara veya Steam'de keşfet... (Ctrl+K)",
            height=42, fg_color="#1A1F2E", border_color="#2a3042",
            text_color=RENKLER["metin"], placeholder_text_color=RENKLER["soluk"])
        self.arama_entry.grid(row=0, column=2, padx=20, pady=10, sticky="ew")
        self.arama_entry.bind("<Return>", self._arama_enter)

        icon_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        icon_frame.grid(row=0, column=3, padx=(10, 20), pady=10, sticky="e")
        ctk.CTkButton(icon_frame, text="🎁 Çark", width=90, height=40, fg_color="#8B5CF6",
                      hover_color="#7C3AED", font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._open_wheel).pack(side="left", padx=3)
        ctk.CTkButton(icon_frame, text="📥", width=40, height=40, fg_color="#1A1F2E",
                      hover_color="#232A3D",
                      command=lambda: self.sayfa_degistir("indirmeler")).pack(side="left", padx=3)
        ctk.CTkButton(icon_frame, text="⚙️", width=40, height=40, fg_color="#1A1F2E",
                      hover_color="#232A3D",
                      command=lambda: self.sayfa_degistir("ayarlar")).pack(side="left", padx=3)

    def _arama_enter(self, _=None):
        q = self.arama_entry.get().strip()
        if q and len(q) > 2:
            if not any(q.lower() in o["isim"].lower() for o in self.oyunlar.values()):
                threading.Thread(target=self._steam_search_thread, args=(q,), daemon=True).start()
            else:
                self.sayfa_degistir("gozat")

    def _steam_search_thread(self, query):
        self.durum(f"Steam'de '{query}' aranıyor...")
        results = SteamStore.search(query)
        self.after(0, lambda: self._show_steam_results(query, results))

    def _show_steam_results(self, query, results):
        if not results:
            self.durum(f"'{query}' için Steam'de sonuç yok."); return
        win = ctk.CTkToplevel(self)
        win.title(f"Steam Arama: {query}")
        win.geometry("700x600")
        win.configure(fg_color=RENKLER["arka"]); win.transient(self); win.grab_set()
        ctk.CTkLabel(win, text=f"Steam'de '{query}' için {len(results)} sonuç",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=RENKLER["metin"]).pack(pady=15)
        sc = ctk.CTkScrollableFrame(win, fg_color=RENKLER["kart"])
        sc.pack(fill="both", expand=True, padx=20, pady=10)
        for r in results:
            row = ctk.CTkFrame(sc, fg_color="#131822", corner_radius=8)
            row.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(row, text=r["name"], font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=RENKLER["metin"], anchor="w").pack(side="left", padx=12, pady=10)
            ctk.CTkButton(row, text="🌐 Steam", width=110, height=32,
                          fg_color=RENKLER["vurgu"],
                          command=lambda a=r["appid"]: webbrowser.open(
                              f"https://store.steampowered.com/app/{a}")).pack(side="right", padx=6)
            ctk.CTkButton(row, text="➕ Ekle", width=110, height=32,
                          fg_color=RENKLER["yesil"],
                          command=lambda rr=r: self._add_steam_to_catalog(rr, win)).pack(side="right", padx=6)
        self.durum(f"Steam: {len(results)} sonuç")

    def _add_steam_to_catalog(self, r, win):
        appid = r["appid"]; oid = f"steam_{appid}"
        if oid in self.oyunlar:
            messagebox.showinfo("Bilgi", "Zaten katalogda."); return
        entry = _mk(appid, r["name"], "Aksiyon", 0)
        self.oyunlar[oid] = entry
        self.veri["eklenen_oyunlar"][oid] = entry
        save_json(DATA_DOSYASI, self.veri)
        self.durum(f"'{r['name']}' eklendi.")
        self.sayfa_degistir("gozat")
        try: win.destroy()
        except Exception: pass

    # ============ SIDEBAR ============
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=RENKLER["yan"])
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.grid(row=0, column=0, padx=15, pady=(18, 12), sticky="ew")
        try:
            li = Image.open(ICON_DOSYASI).convert("RGBA").resize((36, 36), Image.LANCZOS)
            self._logo_ref = ctk.CTkImage(light_image=li, dark_image=li, size=(36, 36))
            ctk.CTkLabel(logo, text="", image=self._logo_ref).pack(side="left", padx=(3, 8))
        except Exception: pass
        ctk.CTkLabel(logo, text="ARDA\nLAUNCHER", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=RENKLER["vurgu"], justify="left").pack(side="left")

        self.nav_btn = {}
        nav = [("anasayfa","🏠 Ana Sayfa"), ("gozat","🧭 Gözat"), ("kutuphane","📚 Kütüphane"),
               ("indirmeler","📥 İndirmeler"), ("istek","⭐ İstek Listesi"), ("profil","👤 Profilim")]
        row = 1
        for key, text in nav:
            if key == "indirmeler":
                holder = ctk.CTkFrame(self.sidebar, fg_color="transparent")
                holder.grid(row=row, column=0, padx=8, pady=2, sticky="ew")
                holder.grid_columnconfigure(0, weight=1)
                b = ctk.CTkButton(holder, text=text, anchor="w", height=40, corner_radius=8,
                                   fg_color="transparent", hover_color=RENKLER["kart_hover"],
                                   text_color=RENKLER["metin"], font=ctk.CTkFont(size=13),
                                   command=lambda k=key: self.sayfa_degistir(k))
                b.grid(row=0, column=0, sticky="ew")
                self.indirme_rozet = ctk.CTkLabel(holder, text="", width=22, height=22,
                                                   corner_radius=11, fg_color=RENKLER["kirmizi"],
                                                   text_color="white", font=ctk.CTkFont(size=10, weight="bold"))
                self.indirme_rozet.grid(row=0, column=1, padx=(5, 5))
                self.indirme_rozet.grid_remove()
                self.nav_btn[key] = b
            else:
                b = ctk.CTkButton(self.sidebar, text=text, anchor="w", height=40, corner_radius=8,
                                   fg_color="transparent", hover_color=RENKLER["kart_hover"],
                                   text_color=RENKLER["metin"], font=ctk.CTkFont(size=13),
                                   command=lambda k=key: self.sayfa_degistir(k))
                b.grid(row=row, column=0, padx=8, pady=2, sticky="ew")
                self.nav_btn[key] = b
            row += 1

        row += 1
        self.quick_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.quick_frame.grid(row=row, column=0, padx=10, pady=(10, 10), sticky="ew")
        self._render_quick_access()

        self.sidebar.grid_rowconfigure(row + 1, weight=1)
        row += 2

        self.profil_kart = ctk.CTkFrame(self.sidebar, fg_color=RENKLER["kart"], corner_radius=12, cursor="hand2")
        self.profil_kart.grid(row=row, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.profil_kart.bind("<Button-1>", lambda e: self.sayfa_degistir("profil"))
        self.sidebar_avatar = ctk.CTkLabel(self.profil_kart, text="", width=52, height=52)
        self.sidebar_avatar.pack(pady=(10, 4))
        self.sidebar_ad = ctk.CTkLabel(self.profil_kart, text="", font=ctk.CTkFont(size=13, weight="bold"),
                                        text_color=RENKLER["metin"])
        self.sidebar_ad.pack()
        self.sidebar_seviye = ctk.CTkLabel(self.profil_kart, text="", font=ctk.CTkFont(size=10),
                                            text_color=RENKLER["soluk"])
        self.sidebar_seviye.pack(pady=(2, 0))
        self.sidebar_kredi = ctk.CTkLabel(self.profil_kart, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                           text_color=RENKLER["altin"])
        self.sidebar_kredi.pack(pady=(0, 8))
        self._profil_side_guncelle()

    def _render_quick_access(self):
        for w in self.quick_frame.winfo_children(): w.destroy()
        kurulu = [(oid, o) for oid, o in self.oyunlar.items() if self._kurulu_mu(oid, o)][:6]
        ctk.CTkLabel(self.quick_frame, text=f"⚡ Yüklü ({len(kurulu)})",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(0, 5))
        if not kurulu:
            ctk.CTkLabel(self.quick_frame, text="Henüz yüklü oyun yok.",
                         font=ctk.CTkFont(size=10), text_color=RENKLER["soluk"]).pack(anchor="w")
            return
        for oid, o in kurulu:
            r = ctk.CTkFrame(self.quick_frame, fg_color="transparent", cursor="hand2")
            r.pack(fill="x", pady=1)
            r.bind("<Button-1>", lambda e, x=oid: self.oyun_detay_goster(x))
            ctk.CTkLabel(r, text="🎮", font=ctk.CTkFont(size=14), width=22).pack(side="left")
            ctk.CTkLabel(r, text=o["isim"][:18], font=ctk.CTkFont(size=11),
                         text_color=RENKLER["metin"], anchor="w").pack(side="left", fill="x", expand=True)

    def _sidebar_avatar_yukle(self):
        p = self.veri["profil"]
        img = None
        if p.get("avatar_yolu") and Path(p["avatar_yolu"]).exists():
            try: img = Image.open(p["avatar_yolu"]).convert("RGB")
            except Exception: img = None
        if img is None:
            preset = PRESET_AVATARS[p.get("avatar_preset", 0) % len(PRESET_AVATARS)]
            img = preset_avatar_olustur(preset["emoji"], preset["bg"], preset["fg"], 52).convert("RGB")
        img = yuvarlak_maske(img, 52)
        renk = CERCEVELER.get(p.get("cerceve", "mavi"), CERCEVELER["mavi"])["renk"]
        img = cerceve_ekle(img, renk, 3)
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self._sidebar_av_ref = ci
            self.sidebar_avatar.configure(image=ci, text="")
        except Exception: pass

    def _profil_side_guncelle(self):
        p = self.veri["profil"]
        try:
            self.sidebar_ad.configure(text=f"{p.get('ad', 'Arda')}#{p.get('etiket', '1453')}")
            self.sidebar_seviye.configure(text=f"Lv.{p.get('seviye', 1)} • {p.get('unvan', 'Yeni')}")
            self.sidebar_kredi.configure(text=f"💎 {p.get('kredi', 0):,} Kredi")
            self._sidebar_avatar_yukle()
        except Exception: pass

    # ============ MAIN (v9.1 PACK FIX) ============
    def _build_main(self):
        self.ana = ctk.CTkFrame(self, corner_radius=0, fg_color=RENKLER["arka"])
        self.ana.grid(row=1, column=1, sticky="nsew")
        self.ana.grid_propagate(False)
        self.ana.grid_rowconfigure(0, weight=1)
        self.ana.grid_columnconfigure(0, weight=1)

        self.icerik = ctk.CTkScrollableFrame(self.ana, fg_color="transparent")
        self.icerik.grid(row=0, column=0, sticky="nsew", padx=25, pady=(10, 10))

        self.status = ctk.CTkLabel(self, text=f"ARDA LAUNCHER v{APP_VERSION} • Hazır", height=26,
                                    anchor="w", fg_color=RENKLER["yan"],
                                    text_color=RENKLER["soluk"], font=ctk.CTkFont(size=10))
        self.status.grid(row=2, column=0, columnspan=2, sticky="ew")

    def durum(self, mesaj):
        try: self.status.configure(text=f"  {mesaj}")
        except Exception: pass

    def _sistem_monitor(self):
        try:
            if self._monitor_job: self.after_cancel(self._monitor_job)
        except Exception: pass
        refresh = int(self.veri.get("settings", {}).get("monitor_refresh", 2000))
        if refresh > 0:
            self._monitor_job = self.after(refresh, self._sistem_monitor)

    def _auto_slider(self):
        try:
            if (self.aktif_sayfa in ("anasayfa", "gozat") and not self.arama
                    and not self._hero_paused and self.hero_ids):
                self._hero_index += 1
                self._hero_guncelle()
        except Exception: pass
        self.after(7000, self._auto_slider)

    def _hero_prev(self):
        if self.hero_ids: self._hero_index -= 1; self._hero_guncelle()
    def _hero_next(self):
        if self.hero_ids: self._hero_index += 1; self._hero_guncelle()
    def _hero_pause(self, event=None): self._hero_paused = True
    def _hero_resume(self, event=None): self._hero_paused = False

    def _hero_guncelle(self):
        try:
            if not self.hero_ids: return
            self._hero_index %= len(self.hero_ids)
            aktif_id = self.hero_ids[self._hero_index]
            onerilen = self.oyunlar.get(aktif_id)
            if not onerilen: return
            if self.hero_banner is not None:
                self.gorsel_yukle_guvenli(self.hero_banner, aktif_id, "banner",
                    onerilen.get("banner_urls", onerilen.get("kapak_urls", [])),
                    (1080, 260), onerilen["isim"], onerilen["tur"], overlay=True)
            if self.hero_title_lbl is not None:
                self.hero_title_lbl.configure(text=onerilen["isim"])
            if self.hero_desc_lbl is not None:
                self.hero_desc_lbl.configure(text=onerilen["aciklama"][:100] + "...")
            if self.hero_incele_btn is not None:
                self.hero_incele_btn.configure(command=lambda oid=aktif_id: self.oyun_detay_goster(oid))
            if self.hero_dots is not None:
                for w in self.hero_dots.winfo_children():
                    try: w.destroy()
                    except Exception: pass
                for i in range(len(self.hero_ids)):
                    c = RENKLER["vurgu"] if i == self._hero_index else RENKLER["soluk"]
                    ctk.CTkLabel(self.hero_dots, text="●", font=ctk.CTkFont(size=11),
                                 text_color=c).pack(side="left", padx=2)
            if self.hero_thumbs_frame is not None:
                self._render_hero_thumbs()
        except Exception: traceback.print_exc()

    def _render_hero_thumbs(self):
        try:
            for w in self.hero_thumbs_frame.winfo_children():
                try: w.destroy()
                except Exception: pass
            n = len(self.hero_ids)
            for offset in range(1, min(5, n)):
                idx = (self._hero_index + offset) % n
                oid = self.hero_ids[idx]
                o = self.oyunlar.get(oid)
                if not o: continue
                th = ctk.CTkFrame(self.hero_thumbs_frame, width=90, height=60,
                                   corner_radius=6, fg_color="#1A1F2E", cursor="hand2")
                th.pack(side="left", padx=3)
                th.pack_propagate(False)
                th.bind("<Button-1>", lambda e, i=idx: self._hero_set(i))
                lbl = ctk.CTkLabel(th, text="", width=90, height=60)
                lbl.pack(fill="both", expand=True)
                lbl.bind("<Button-1>", lambda e, i=idx: self._hero_set(i))
                self.gorsel_yukle_guvenli(lbl, oid, f"thumb_{offset}", o.get("kapak_urls", []),
                                           (90, 60), o["isim"], o["tur"], overlay=False)
        except Exception: pass

    def _hero_set(self, idx):
        self._hero_index = idx
        self._hero_guncelle()

    def gorsel_yukle_guvenli(self, label, oid, tur_adi, urls, boyut, isim, tur, overlay=False):
        key = f"{oid}_{tur_adi}_{boyut[0]}x{boyut[1]}"
        if key in self.image_refs:
            try:
                label._arda_ref = self.image_refs[key]
                label.configure(image=self.image_refs[key], text="")
                return
            except Exception: pass
        try:
            palet = PALETLER.get(tur, PALETLER["Araçlar"])
            bg_c = tuple(max(28, min(70, c)) for c in palet[0])
            placeholder = Image.new("RGB", boyut, bg_c)
            ph_ctk = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=boyut)
            label._arda_ref = ph_ctk
            label.configure(image=ph_ctk, text="")
        except Exception: pass
        disk_img = _diskten_resim_bul(urls or [])
        if disk_img is not None:
            try:
                final = akilli_kirp(disk_img, boyut)
                if overlay: final = banner_overlay(final)
                ci = ctk.CTkImage(light_image=final, dark_image=final, size=boyut)
                self.image_refs[key] = ci
                label._arda_ref = ci
                label.configure(image=ci, text="")
                return
            except Exception: pass
        def _worker():
            img = _resim_indir_dogrula(urls or [], CACHE_COVERS)
            if img is None: img = sinematik_kapak_uret(isim, tur, boyut)
            else: img = akilli_kirp(img, boyut)
            if overlay: img = banner_overlay(img)
            try: ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=boyut)
            except Exception: return
            def _update():
                try:
                    label._arda_ref = ctk_img
                    self.image_refs[key] = ctk_img
                    label.configure(image=ctk_img, text="")
                except Exception: pass
            try: self.after(0, _update)
            except Exception: pass
        threading.Thread(target=_worker, daemon=True).start()

    def _pencere_ikonu_uygula(self):
        try:
            if ICON_DOSYASI.exists():
                if sys.platform == "win32":
                    try: self.iconbitmap(str(ICON_DOSYASI))
                    except Exception: pass
        except Exception: pass

    def _tema_uygula(self, anahtar):
        t = TEMALAR.get(anahtar, TEMALAR["mavi"])
        RENKLER["vurgu"] = t["renk"]; RENKLER["vurgu_hover"] = t["hover"]

    def tema_degistir(self, anahtar):
        self.veri["tema"] = anahtar
        self._tema_uygula(anahtar)
        self._xp_ver(15, "tema")
        self._rozet_ver("theme_master")
        save_json(DATA_DOSYASI, self.veri)
        for w in self.winfo_children(): w.destroy()
        self._build_top_bar(); self._build_sidebar(); self._build_main()
        self._bind_shortcuts()
        self.sayfa_degistir(self.aktif_sayfa)

    def _shimmer(self, widget):
        if not self._animations_enabled: return
        try: original = widget.cget("fg_color")
        except Exception: return
        colors = ["#FFFFFF", "#00D2FF", "#9D00FF", "#FFD700", original]
        def step(i):
            if i >= len(colors):
                try: widget.configure(fg_color=original)
                except Exception: pass
                return
            try: widget.configure(fg_color=colors[i])
            except Exception: pass
            self.after(80, lambda: step(i + 1))
        step(0)

    def _xp_ver(self, miktar, kaynak=""):
        p = self.veri["profil"]
        p["xp"] = p.get("xp", 0) + miktar
        yeni = 1 + p["xp"] // 500
        if yeni > p.get("seviye", 1): p["seviye"] = yeni
        save_json(DATA_DOSYASI, self.veri); self._profil_side_guncelle()

    def _rozet_ver(self, anahtar):
        if anahtar not in self.veri["profil"]["rozetler"]:
            self.veri["profil"]["rozetler"].append(anahtar)
            try:
                kredi = BASARIMLAR[anahtar]["kredi"]
                self.veri["profil"]["kredi"] = self.veri["profil"].get("kredi", 0) + kredi
                self.durum(f"🏆 {BASARIMLAR[anahtar]['ad']} rozeti! (+{kredi} Kredi)")
                self._kredi_guncelle()
            except Exception: pass
            save_json(DATA_DOSYASI, self.veri)

    def _kredi_guncelle(self):
        try:
            self.sidebar_kredi.configure(text=f"💎 {self.veri['profil'].get('kredi', 0):,} Kredi")
        except Exception: pass

    def _kredi_ver(self, miktar, sebep=""):
        self.veri["profil"]["kredi"] = self.veri["profil"].get("kredi", 0) + miktar
        save_json(DATA_DOSYASI, self.veri)
        self._kredi_guncelle()
        if sebep: self.durum(f"+{miktar} Kredi ({sebep})")

    def _kredi_harca(self, miktar):
        k = self.veri["profil"].get("kredi", 0)
        if k < miktar: return False
        self.veri["profil"]["kredi"] = k - miktar
        save_json(DATA_DOSYASI, self.veri)
        self._kredi_guncelle()
        return True

    def _aktivite_ekle(self, metin):
        self.veri["son_aktiviteler"].insert(0, {"metin": metin, "zaman": time.time()})
        self.veri["son_aktiviteler"] = self.veri["son_aktiviteler"][:30]
        save_json(DATA_DOSYASI, self.veri)

    # ============ QUESTS ============
    def _quest_reset_if_needed(self):
        g = self.veri.get("gorevler", {})
        bugun = datetime.now().strftime("%Y-%m-%d")
        if g.get("gunluk_tarih", "") != bugun:
            self.veri["gorevler"] = {"gunluk_tarih": bugun, "ilerleme": {}, "alinan": []}
            save_json(DATA_DOSYASI, self.veri)

    def _quest_progress(self, key, delta=1):
        try:
            g = self.veri.setdefault("gorevler", {"gunluk_tarih": "", "ilerleme": {}, "alinan": []})
            bugun = datetime.now().strftime("%Y-%m-%d")
            if g.get("gunluk_tarih", "") != bugun:
                g = {"gunluk_tarih": bugun, "ilerleme": {}, "alinan": []}
                self.veri["gorevler"] = g
            ilerleme = g.setdefault("ilerleme", {})
            ilerleme[key] = ilerleme.get(key, 0) + delta
            save_json(DATA_DOSYASI, self.veri)
        except Exception: pass

    def _quest_claim(self, key):
        try:
            q = QUESTS[key]
            g = self.veri["gorevler"]
            ilerleme = g.get("ilerleme", {}).get(key, 0)
            if ilerleme < q["hedef"]: return
            if key in g.get("alinan", []): return
            g.setdefault("alinan", []).append(key)
            self._kredi_ver(q["kredi"], "görev")
            save_json(DATA_DOSYASI, self.veri)
            self.durum(f"✅ Görev tamamlandı: {q['ad']} (+{q['kredi']} Kredi)")
            self.sayfa_degistir(self.aktif_sayfa)
        except Exception: traceback.print_exc()

    # ============ DAILY WHEEL ============
    def _open_wheel(self):
        try:
            now = time.time()
            son = self.veri.get("cark_son", 0)
            kalan = 86400 - (now - son)
            if kalan > 0:
                self.durum(f"⏳ Günlük çark için {int(kalan//3600)}s {int((kalan%3600)//60)}dk kaldı.")
                messagebox.showinfo("Günlük Çark",
                    f"Çarkı yarın tekrar çevirebilirsin.\nKalan: {int(kalan//3600)} saat {int((kalan%3600)//60)} dakika")
                return
            if self._wheel_overlay is not None:
                try: self._wheel_overlay.destroy()
                except Exception: pass
            overlay_bg = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
            overlay_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
            card = ctk.CTkFrame(overlay_bg, corner_radius=24, border_width=4, border_color="#9D00FF",
                                 fg_color="#131822", width=560, height=480)
            card.place(relx=0.5, rely=0.5, anchor="center")
            card.pack_propagate(False)
            ctk.CTkLabel(card, text="🎁 Günlük Şans Çarkı", font=ctk.CTkFont(size=22, weight="bold"),
                         text_color="#9D00FF").pack(pady=(25, 10))
            ctk.CTkLabel(card, text="Her 24 saatte bir ücretsiz çevir!",
                         font=ctk.CTkFont(size=12), text_color=RENKLER["soluk"]).pack()
            result_lbl = ctk.CTkLabel(card, text="🎯", font=ctk.CTkFont(size=72))
            result_lbl.pack(pady=20)
            spin_btn = ctk.CTkButton(card, text="🎰 ÇEVİR", height=52, width=240,
                                      fg_color="#FFD700", hover_color="#D4AF37",
                                      text_color="#0B0E14", font=ctk.CTkFont(size=16, weight="bold"))
            spin_btn.pack(pady=10)
            info_lbl = ctk.CTkLabel(card, text="Ödüller: 250, 500, 1K, 2.5K, 5K Kredi",
                                     font=ctk.CTkFont(size=11), text_color=RENKLER["soluk"])
            info_lbl.pack(pady=(5, 15))
            def spin():
                spin_btn.configure(state="disabled")
                def do_spin():
                    try:
                        for i in range(15):
                            result_lbl.configure(text=f"💎 {random.choice(WHEEL_REWARDS):,}")
                            time.sleep(0.1)
                        odul = random.choice(WHEEL_REWARDS)
                        self.veri["cark_son"] = time.time()
                        self.veri["cark_toplam_kazanc"] = self.veri.get("cark_toplam_kazanc", 0) + odul
                        self.veri["profil"]["kredi"] = self.veri["profil"].get("kredi", 0) + odul
                        save_json(DATA_DOSYASI, self.veri)
                        self.after(0, lambda: result_lbl.configure(text=f"🎉 {odul:,} KREDİ!"))
                        self.after(0, self._kredi_guncelle)
                        self.after(0, lambda: spin_btn.configure(text="✅ Alındı!", state="disabled"))
                        self.after(0, lambda: self.durum(f"🎁 Çark ödülü: +{odul:,} Kredi"))
                        self.after(2000, lambda: (overlay_bg.destroy(), setattr(self, "_wheel_overlay", None)))
                    except Exception: traceback.print_exc()
                threading.Thread(target=do_spin, daemon=True).start()
            spin_btn.configure(command=spin)
            ctk.CTkButton(card, text="Kapat", height=34, width=100,
                          fg_color=RENKLER["yan"],
                          command=lambda: (overlay_bg.destroy(), setattr(self, "_wheel_overlay", None))).pack(pady=(0, 15))
            self._wheel_overlay = overlay_bg
        except Exception: traceback.print_exc()

    # ============ PAGE ROUTER ============
    def sayfa_degistir(self, s, push_history=True):
        self.hero_banner = None; self.hero_title_lbl = None; self.hero_desc_lbl = None
        self.hero_incele_btn = None; self.hero_dots = None; self.hero_thumbs_frame = None
        self.hero_ids = []
        try:
            if self.aktif_sayfa: self._scroll_kaydet(self.aktif_sayfa)
        except Exception: pass
        self.aktif_sayfa = s
        if push_history: self._nav_push(s)
        for k, b in self.nav_btn.items():
            try:
                b.configure(fg_color=RENKLER["vurgu"] if k == s else "transparent",
                            text_color="white" if k == s else RENKLER["metin"])
            except Exception: pass
        for w in self.icerik.winfo_children():
            try: w.destroy()
            except Exception: pass
        try:
            page_func = {"anasayfa": self._page_anasayfa, "gozat": self._page_gozat,
                          "kutuphane": self._page_kutuphane, "indirmeler": self._page_indirmeler,
                          "istek": self._page_istek, "profil": self._page_profil,
                          "ayarlar": self._page_ayarlar}.get(s, self._page_anasayfa)
            page_func()
        except Exception as e:
            traceback.print_exc()
            try:
                err_frame = ctk.CTkFrame(self.icerik, corner_radius=10, fg_color="#2a1010")
                err_frame.pack(fill="x", pady=20)
                ctk.CTkLabel(err_frame, text=f"⚠️ Sayfa hatası: {e}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color="#EF4444").pack(padx=15, pady=15)
            except Exception: pass
        saved = self._scroll_positions.get(s, 0.0)
        if saved and saved > 0.001:
            self.after(50, lambda p=saved: self._scroll_geri_yukle(p))

    def _scroll_kaydet(self, sayfa):
        try:
            pos = self.icerik._parent_canvas.yview()[0]
            self._scroll_positions[sayfa] = float(pos)
        except Exception: pass

    def _scroll_geri_yukle(self, pos):
        try:
            if pos and pos > 0.001:
                self.icerik._parent_canvas.yview_moveto(pos)
        except Exception: pass

    def _kurulu_mu(self, oid, o):
        if o.get("steam_appid"):
            return _steam_game_installed(o["steam_appid"])
        exe = o.get("exe_adi")
        if not exe: return False
        kayitli = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if kayitli and Path(kayitli).exists(): return True
        k = self.oyunlar_dizini / oid
        return k.exists() and any(k.rglob(exe))

    def _filtrele(self, oid, o):
        if self.arama and self.arama not in o["isim"].lower(): return False
        return True

    # ============ ANA SAYFA ============
    def _page_anasayfa(self):
        try:
            # HERO
            one = ["pubg", "cs2", "marvelrivals", "apex", "destiny2", "haloinfinite"]
            one = [x for x in one if x in self.oyunlar]
            self._hero_index %= max(len(one), 1)
            aktif_id = one[self._hero_index] if one else None
            onerilen = self.oyunlar.get(aktif_id) if aktif_id else None

            if onerilen:
                hero = ctk.CTkFrame(self.icerik, height=260, corner_radius=16, fg_color=RENKLER["kart"])
                hero.pack(fill="x", pady=(0, 20))
                hero.pack_propagate(False)
                hero.grid_rowconfigure(0, weight=1)
                hero.grid_columnconfigure(0, weight=1)
                self.hero_banner = ctk.CTkLabel(hero, text="")
                self.hero_banner.grid(row=0, column=0, sticky="nsew")
                self.gorsel_yukle_guvenli(self.hero_banner, aktif_id, "banner",
                    onerilen.get("banner_urls", onerilen.get("kapak_urls", [])),
                    (1080, 260), onerilen["isim"], onerilen["tur"], overlay=True)
                info = ctk.CTkFrame(hero, fg_color=RENKLER["yan"], corner_radius=10)
                info.place(x=25, y=150)
                self.hero_title_lbl = ctk.CTkLabel(info, text=onerilen["isim"],
                                                    font=ctk.CTkFont(size=22, weight="bold"),
                                                    text_color="white")
                self.hero_title_lbl.pack(anchor="w", padx=15, pady=(10, 2))
                self.hero_desc_lbl = ctk.CTkLabel(info, text=onerilen["aciklama"][:100] + "...",
                                                   font=ctk.CTkFont(size=11), text_color=RENKLER["soluk"],
                                                   wraplength=500, justify="left")
                self.hero_desc_lbl.pack(anchor="w", padx=15, pady=(0, 8))
                self.hero_incele_btn = ctk.CTkButton(info, text="İncele", width=110, height=30,
                                                      fg_color=RENKLER["vurgu"],
                                                      command=lambda oid=aktif_id: self.oyun_detay_goster(oid))
                self.hero_incele_btn.pack(anchor="w", padx=15, pady=(0, 10))
                ctk.CTkButton(hero, text="◀", width=36, height=36, fg_color=RENKLER["yan"],
                              command=self._hero_prev).place(relx=0.0, rely=0.5, x=15, anchor="w")
                ctk.CTkButton(hero, text="▶", width=36, height=36, fg_color=RENKLER["yan"],
                              command=self._hero_next).place(relx=1.0, rely=0.5, x=-15, anchor="e")
                self.hero_dots = ctk.CTkFrame(hero, fg_color="transparent")
                self.hero_dots.place(relx=0.5, rely=1.0, y=-12, anchor="s")
                self.hero_ids = list(one)
                self.hero_thumbs_frame = ctk.CTkFrame(hero, fg_color="transparent")
                self.hero_thumbs_frame.place(relx=1.0, rely=1.0, x=-80, y=-15, anchor="se")
                hero.bind("<Enter>", self._hero_pause, add="+")
                hero.bind("<Leave>", self._hero_resume, add="+")
                self._hero_guncelle()

            # Update banner
            if self._update_info:
                try:
                    ub = ctk.CTkFrame(self.icerik, fg_color="#0F1F3A", corner_radius=8,
                                       border_width=1, border_color="#00D2FF")
                    ub.pack(fill="x", pady=(0, 15))
                    ctk.CTkLabel(ub, text=f"🔄 v{self._update_info.get('version','?')} sürümü mevcut!",
                                 font=ctk.CTkFont(size=13, weight="bold"),
                                 text_color="#00D2FF").pack(side="left", padx=15, pady=10)
                    ctk.CTkButton(ub, text="Yükle ve yeniden başlat", height=32, width=180,
                                  fg_color=RENKLER["yesil"], command=self._download_update).pack(
                        side="right", padx=5, pady=6)
                except Exception: pass

            # QUESTS
            self._render_quests_section()

            # FREE GAMES
            self._render_games_section("🆓 Bedava Oyunlar", RENKLER["yesil"],
                                        [(oid, o) for oid, o in self.oyunlar.items() if o.get("fiyat", 0) == 0][:8])

            # PAID GAMES
            self._render_games_section("💎 Kredili Oyunlar", RENKLER["altin"],
                                        [(oid, o) for oid, o in self.oyunlar.items() if o.get("fiyat", 0) > 0][:8])
        except Exception: traceback.print_exc()

    def _render_quests_section(self):
        try:
            self._quest_reset_if_needed()
            qf = ctk.CTkFrame(self.icerik, corner_radius=12, fg_color=RENKLER["kart"])
            qf.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(qf, text="📋 Günlük Görevler", font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(10, 8))
            ilerleme = self.veri.get("gorevler", {}).get("ilerleme", {})
            alinan = set(self.veri.get("gorevler", {}).get("alinan", []))
            for key, q in QUESTS.items():
                if q.get("tip") != "daily": continue
                row = ctk.CTkFrame(qf, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=4)
                cur = min(ilerleme.get(key, 0), q["hedef"])
                ctk.CTkLabel(row, text=f"{q['ad']} — {cur}/{q['hedef']}",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=RENKLER["metin"], width=280, anchor="w").pack(side="left")
                bar = ctk.CTkProgressBar(row, height=6, progress_color=RENKLER["vurgu"])
                bar.pack(side="left", fill="x", expand=True, padx=(8, 8))
                bar.set(cur / q["hedef"] if q["hedef"] > 0 else 0)
                if key in alinan:
                    ctk.CTkLabel(row, text="✅ Alındı", font=ctk.CTkFont(size=11, weight="bold"),
                                 text_color=RENKLER["yesil"], width=90).pack(side="right")
                elif cur >= q["hedef"]:
                    ctk.CTkButton(row, text=f"🎁 +{q['kredi']}", width=90, height=26,
                                  fg_color=RENKLER["yesil"],
                                  command=lambda k=key: self._quest_claim(k)).pack(side="right")
                else:
                    ctk.CTkLabel(row, text=f"💎 {q['kredi']}", font=ctk.CTkFont(size=11),
                                 text_color=RENKLER["altin"], width=90).pack(side="right")
        except Exception: traceback.print_exc()

    def _render_games_section(self, title, color, games):
        try:
            if not games: return
            ctk.CTkLabel(self.icerik, text=title,
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=color, anchor="w").pack(fill="x", pady=(10, 8))
            cards_frame = ctk.CTkFrame(self.icerik, fg_color="transparent")
            cards_frame.pack(fill="x", pady=(0, 15))
            for i in range(4):
                cards_frame.grid_columnconfigure(i, weight=1)
            for i, (oid, o) in enumerate(games):
                r, c = divmod(i, 4)
                fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
                try:
                    OyunKarti(cards_frame, oid, o, self, favori=fav).grid(
                        row=r, column=c, padx=8, pady=8, sticky="nsew")
                except Exception:
                    traceback.print_exc()
        except Exception: traceback.print_exc()

    # ============ GÖZAT ============
    def _page_gozat(self):
        try:
            header = ctk.CTkFrame(self.icerik, fg_color="transparent")
            header.pack(fill="x", pady=(0, 12))
            ctk.CTkLabel(header, text="🧭 Tüm Oyunlar",
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=RENKLER["metin"]).pack(side="left")

            sort_bar = ctk.CTkFrame(self.icerik, fg_color="transparent")
            sort_bar.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(sort_bar, text="Sırala:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(side="left", padx=(0, 8))
            sort_map = {"En Popüler": "popular", "Fiyat: Düşükten Yükseğe": "price_asc",
                         "Fiyat: Yüksekten Düşüğe": "price_desc", "A-Z İsim": "az",
                         "Sadece Bedava": "free"}
            cur_label = "En Popüler"
            for k, v in sort_map.items():
                if v == self._gozat_sort: cur_label = k
            ctk.CTkOptionMenu(sort_bar, values=list(sort_map.keys()), width=240,
                              fg_color=RENKLER["yan"],
                              command=lambda v: self._set_sort(sort_map.get(v, "popular"))
                              ).pack(side="left")
            ctk.CTkLabel(sort_bar, text=f"  •  Toplam {len(self.oyunlar)} oyun",
                         font=ctk.CTkFont(size=11), text_color=RENKLER["soluk"]).pack(side="left", padx=10)

            games = [(oid, o) for oid, o in self.oyunlar.items() if self._filtrele(oid, o)]
            if self._gozat_sort == "price_asc":
                games.sort(key=lambda x: x[1].get("fiyat", 0))
            elif self._gozat_sort == "price_desc":
                games.sort(key=lambda x: x[1].get("fiyat", 0), reverse=True)
            elif self._gozat_sort == "az":
                games.sort(key=lambda x: x[1].get("isim", ""))
            elif self._gozat_sort == "free":
                games = [(oid, o) for oid, o in games if o.get("fiyat", 0) == 0]

            if not games:
                ctk.CTkLabel(self.icerik, text="Eşleşen oyun yok.",
                             font=ctk.CTkFont(size=15), text_color=RENKLER["soluk"]).pack(pady=60)
                return

            cards_frame = ctk.CTkFrame(self.icerik, fg_color="transparent")
            cards_frame.pack(fill="x", pady=10)
            for i in range(4):
                cards_frame.grid_columnconfigure(i, weight=1)
            for i, (oid, o) in enumerate(games):
                r, c = divmod(i, 4)
                fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
                try:
                    OyunKarti(cards_frame, oid, o, self, favori=fav).grid(
                        row=r, column=c, padx=8, pady=8, sticky="nsew")
                except Exception: traceback.print_exc()
        except Exception: traceback.print_exc()

    def _set_sort(self, sort_key):
        self._gozat_sort = sort_key
        self.sayfa_degistir("gozat")

    def _page_kutuphane(self):
        try:
            ctk.CTkLabel(self.icerik, text="📚 Kütüphanem", font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=RENKLER["metin"], anchor="w").pack(fill="x", pady=(0, 15))
            kurulu = [(oid, o) for oid, o in self.oyunlar.items() if self._kurulu_mu(oid, o)]
            if not kurulu:
                ctk.CTkLabel(self.icerik, text="Henüz yüklü oyun yok.",
                             font=ctk.CTkFont(size=14),
                             text_color=RENKLER["soluk"]).pack(anchor="w", pady=50); return
            cards_frame = ctk.CTkFrame(self.icerik, fg_color="transparent")
            cards_frame.pack(fill="x", pady=10)
            for i in range(4):
                cards_frame.grid_columnconfigure(i, weight=1)
            for i, (oid, o) in enumerate(kurulu):
                r, c = divmod(i, 4)
                fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
                try:
                    OyunKarti(cards_frame, oid, o, self, favori=fav).grid(
                        row=r, column=c, padx=8, pady=8, sticky="nsew")
                except Exception: traceback.print_exc()
        except Exception: traceback.print_exc()

    def _page_indirmeler(self):
        try:
            ctk.CTkLabel(self.icerik, text="📥 Aktif İndirmeler",
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=RENKLER["metin"], anchor="w").pack(fill="x", pady=(0, 15))
            aktif = dict(self.download_engine.aktif)
            if not aktif:
                ctk.CTkLabel(self.icerik, text="Aktif indirme yok.",
                             font=ctk.CTkFont(size=14),
                             text_color=RENKLER["soluk"]).pack(anchor="w", pady=50); return
            for oid, d in aktif.items():
                oyun = self.oyunlar.get(oid, {})
                kart = ctk.CTkFrame(self.icerik, corner_radius=10, fg_color=RENKLER["kart"])
                kart.pack(fill="x", pady=6)
                ctk.CTkLabel(kart, text=oyun.get("isim", oid),
                             font=ctk.CTkFont(size=15, weight="bold"),
                             text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(8, 3))
                y = d["indirilen"] / d["toplam"] if d["toplam"] else 0
                bar = ctk.CTkProgressBar(kart, height=8, progress_color=RENKLER["vurgu"])
                bar.pack(fill="x", padx=15, pady=4); bar.set(y)
                ctk.CTkLabel(kart, text=f"{fmt_bayt(d['indirilen'])} / {fmt_bayt(d['toplam'])} • "
                                         f"{d.get('hiz', 0):.2f} MB/s",
                             font=ctk.CTkFont(size=11),
                             text_color=RENKLER["soluk"]).pack(anchor="w", padx=15, pady=(0, 8))
        except Exception: traceback.print_exc()

    def _page_istek(self):
        try:
            ctk.CTkLabel(self.icerik, text="⭐ İstek Listem", font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=RENKLER["metin"], anchor="w").pack(fill="x", pady=(0, 15))
            istek = self.veri.get("istek_listesi", [])
            if not istek:
                ctk.CTkLabel(self.icerik, text="İstek listeniz boş.",
                             font=ctk.CTkFont(size=14),
                             text_color=RENKLER["soluk"]).pack(anchor="w", pady=50); return
            cards_frame = ctk.CTkFrame(self.icerik, fg_color="transparent")
            cards_frame.pack(fill="x", pady=10)
            for i in range(4):
                cards_frame.grid_columnconfigure(i, weight=1)
            for i, oid in enumerate(istek):
                o = self.oyunlar.get(oid)
                if not o: continue
                r, c = divmod(i, 4)
                fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
                try:
                    OyunKarti(cards_frame, oid, o, self, favori=fav).grid(
                        row=r, column=c, padx=8, pady=8, sticky="nsew")
                except Exception: traceback.print_exc()
        except Exception: traceback.print_exc()

    # ============ PROFİL ============
    def _page_profil(self):
        try:
            p = self.veri["profil"]
            bf = ctk.CTkFrame(self.icerik, height=180, corner_radius=14, fg_color=RENKLER["kart"])
            bf.pack(fill="x", pady=(0, 30))
            bf.pack_propagate(False)
            banner_lbl = ctk.CTkLabel(bf, text="")
            banner_lbl.pack(fill="both", expand=True)
            if p.get("banner_yolu") and Path(p["banner_yolu"]).exists():
                try:
                    img = Image.open(p["banner_yolu"]).convert("RGB")
                    img = akilli_kirp(img, (1080, 180))
                    ci = ctk.CTkImage(light_image=img, dark_image=img, size=(1080, 180))
                    banner_lbl._arda_ref = ci; banner_lbl.configure(image=ci, text="")
                except Exception: self._banner_tema_uygula(banner_lbl, p.get("banner_tema", 0))
            else: self._banner_tema_uygula(banner_lbl, p.get("banner_tema", 0))

            avf = ctk.CTkFrame(self.icerik, fg_color="transparent")
            avf.pack(fill="x", padx=20, pady=(0, 10))
            av = ctk.CTkLabel(avf, text="", width=120, height=120)
            av.pack(side="left", padx=(0, 20)); self._profil_avatar_yukle(av, 110)
            info = ctk.CTkFrame(avf, fg_color="transparent"); info.pack(side="left")
            ctk.CTkLabel(info, text=f"{p['ad']}#{p['etiket']}",
                         font=ctk.CTkFont(size=28, weight="bold"),
                         text_color=p.get("renk", "#3B82F6")).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Lv.{p['seviye']} • {p['unvan']} • {p['durum']}",
                         font=ctk.CTkFont(size=13), text_color=RENKLER["soluk"]).pack(anchor="w", pady=2)
            ctk.CTkLabel(info, text=p.get("biyografi", ""),
                         font=ctk.CTkFont(size=12), text_color=RENKLER["soluk"],
                         wraplength=600, justify="left").pack(anchor="w", pady=(4, 0))
            ctk.CTkLabel(info, text=f"💎 {p.get('kredi', 0):,} Kredi",
                         font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["altin"]).pack(anchor="w", pady=(8, 0))

            xf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=10)
            xf.pack(fill="x", pady=15, padx=20)
            ctk.CTkLabel(xf, text=f"Level {p['seviye']} — {p['xp'] % 500}/500 XP",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(8, 4))
            xb = ctk.CTkProgressBar(xf, height=10, progress_color=RENKLER["vurgu"])
            xb.pack(fill="x", padx=15, pady=(0, 10)); xb.set((p["xp"] % 500) / 500)

            ctk.CTkButton(self.icerik, text="✏️ Profili Düzenle", height=40,
                          fg_color=RENKLER["vurgu"], command=self.profil_duzenle).pack(
                anchor="e", padx=20, pady=(0, 20))

            # Başarımlar
            rf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=12)
            rf.pack(fill="x", pady=10, padx=20)
            ctk.CTkLabel(rf, text="🏆 Başarımlar", font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(10, 8))
            gf = ctk.CTkFrame(rf, fg_color="transparent"); gf.pack(fill="x", padx=15, pady=(0, 15))
            for i in range(4): gf.grid_columnconfigure(i, weight=1)
            kaz = set(p.get("rozetler", []))
            for idx, (k, b) in enumerate(BASARIMLAR.items()):
                rr, cc = divmod(idx, 4)
                kilitli = k not in kaz
                c = RENKLER["soluk"] if kilitli else RENKLER["vurgu"]
                ctk.CTkLabel(gf, text=f"{'🔒' if kilitli else b['ikon']} {b['ad']}",
                             font=ctk.CTkFont(size=11, weight="bold"), text_color=c).grid(
                    row=rr, column=cc, padx=5, pady=5, sticky="w")

            # Weekly quests
            self._render_quests_section()
        except Exception: traceback.print_exc()

    def _banner_tema_uygula(self, label, idx):
        t = BANNER_TEMALARI[idx % len(BANNER_TEMALARI)]
        img = Image.new("RGB", (1080, 180)); d = ImageDraw.Draw(img)
        for y in range(180):
            o = y / 179
            d.line([(0, y), (1080, y)], fill=(int(t["r1"][0]*(1-o)+t["r2"][0]*o),
                                              int(t["r1"][1]*(1-o)+t["r2"][1]*o),
                                              int(t["r1"][2]*(1-o)+t["r2"][2]*o)))
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(1080, 180))
            label._arda_ref = ci; label.configure(image=ci, text="")
        except Exception: pass

    def _profil_avatar_yukle(self, label, boyut):
        p = self.veri["profil"]
        img = None
        if p.get("avatar_yolu") and Path(p["avatar_yolu"]).exists():
            try: img = Image.open(p["avatar_yolu"]).convert("RGB")
            except Exception: img = None
        if img is None:
            preset = PRESET_AVATARS[p.get("avatar_preset", 0) % len(PRESET_AVATARS)]
            img = preset_avatar_olustur(preset["emoji"], preset["bg"], preset["fg"], boyut).convert("RGB")
        img = yuvarlak_maske(img, boyut)
        renk = CERCEVELER.get(p.get("cerceve", "mavi"), CERCEVELER["mavi"])["renk"]
        img = cerceve_ekle(img, renk, 5)
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            label._arda_ref = ci; label.configure(image=ci, text="")
        except Exception: pass

    def profil_duzenle(self):
        p = self.veri["profil"]
        win = ctk.CTkToplevel(self); win.title("Profili Düzenle"); win.geometry("700x850")
        win.configure(fg_color=RENKLER["arka"]); win.transient(self); win.grab_set()
        sc = ctk.CTkScrollableFrame(win, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=15, pady=15)
        def add_e(lbl, val):
            ctk.CTkLabel(sc, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(anchor="w", pady=(6, 2))
            e = ctk.CTkEntry(sc, height=36, fg_color=RENKLER["kart"], text_color=RENKLER["metin"])
            e.pack(fill="x", pady=(0, 6)); e.insert(0, val); return e
        e_ad = add_e("Kullanıcı Adı:", p.get("ad", ""))
        e_etiket = add_e("4 Haneli Etiket:", p.get("etiket", "1453"))
        e_bio = add_e("Biyografi:", p.get("biyografi", ""))
        ctk.CTkLabel(sc, text="Unvan:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(6, 2))
        uv = ctk.StringVar(value=p.get("unvan", "Yeni Oyuncu"))
        ctk.CTkOptionMenu(sc, values=UNVANLAR, variable=uv,
                          fg_color=RENKLER["kart"]).pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(sc, text="8 Hazır Avatar:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(10, 4))
        av_frame = ctk.CTkFrame(sc, fg_color="transparent"); av_frame.pack(fill="x", pady=(0, 6))
        avatar_var = ctk.IntVar(value=p.get("avatar_preset", 0))
        for i, preset in enumerate(PRESET_AVATARS):
            try:
                img = preset_avatar_olustur(preset["emoji"], preset["bg"], preset["fg"], 60).convert("RGB")
                ci = ctk.CTkImage(light_image=img, dark_image=img, size=(60, 60))
                b = ctk.CTkButton(av_frame, text="", image=ci, width=65, height=65,
                                   fg_color=RENKLER["kart"], hover_color=RENKLER["vurgu"],
                                   command=lambda i=i: avatar_var.set(i))
                b.pack(side="left", padx=3)
                b._img_ref = ci
            except Exception: pass
        ctk.CTkLabel(sc, text="8 Neon Çerçeve:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(10, 4))
        cf = ctk.CTkFrame(sc, fg_color="transparent"); cf.pack(fill="x", pady=(0, 6))
        cv = ctk.StringVar(value=p.get("cerceve", "mavi"))
        for k, c in CERCEVELER.items():
            ctk.CTkButton(cf, text=c["ad"][:10], width=85, height=30, fg_color=c["renk"],
                          command=lambda a=k: cv.set(a)).pack(side="left", padx=2)
        ctk.CTkLabel(sc, text="8 Banner Teması:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(10, 4))
        bfm = ctk.CTkFrame(sc, fg_color="transparent"); bfm.pack(fill="x", pady=(0, 6))
        bv = ctk.IntVar(value=p.get("banner_tema", 0))
        for i, t in enumerate(BANNER_TEMALARI):
            ctk.CTkButton(bfm, text=t["ad"], width=85, height=30,
                          fg_color=f"#{t['r1'][0]:02x}{t['r1'][1]:02x}{t['r1'][2]:02x}",
                          command=lambda i2=i: bv.set(i2)).pack(side="left", padx=2)
        ctk.CTkLabel(sc, text="İsim Rengi:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(10, 4))
        renk_f = ctk.CTkFrame(sc, fg_color="transparent"); renk_f.pack(fill="x", pady=(0, 6))
        rv = ctk.StringVar(value=p.get("renk", "#3B82F6"))
        for ad, c in [("Mavi", "#3B82F6"), ("Yeşil", "#10B981"), ("Mor", "#8B5CF6"),
                       ("Altın", "#F59E0B"), ("Kırmızı", "#EF4444"), ("Pembe", "#EC4899")]:
            ctk.CTkButton(renk_f, text=ad, width=80, height=30, fg_color=c,
                          command=lambda a=c: rv.set(a)).pack(side="left", padx=2)
        def sec_av_dosya():
            f = filedialog.askopenfilename(parent=win, filetypes=[("Resim", "*.png *.jpg *.jpeg")])
            if f:
                try:
                    img = Image.open(f).convert("RGB")
                    hedef = PROFILE_CACHE / f"avatar_{int(time.time())}.png"
                    img.save(hedef, "PNG")
                    p["avatar_yolu"] = str(hedef)
                    save_json(DATA_DOSYASI, self.veri); self.durum("Avatar güncellendi.")
                except Exception as e: messagebox.showerror("Hata", str(e))
        def sec_banner_dosya():
            f = filedialog.askopenfilename(parent=win, filetypes=[("Resim", "*.png *.jpg *.jpeg")])
            if f:
                try:
                    img = Image.open(f).convert("RGB")
                    hedef = PROFILE_CACHE / f"banner_{int(time.time())}.png"
                    img.save(hedef, "PNG")
                    p["banner_yolu"] = str(hedef)
                    save_json(DATA_DOSYASI, self.veri); self.durum("Banner güncellendi.")
                except Exception as e: messagebox.showerror("Hata", str(e))
        bf2 = ctk.CTkFrame(sc, fg_color="transparent"); bf2.pack(fill="x", pady=(10, 5))
        ctk.CTkButton(bf2, text="📷 Avatar Yükle", height=36, fg_color=RENKLER["vurgu"],
                      command=sec_av_dosya).pack(side="left", padx=5)
        ctk.CTkButton(bf2, text="🖼️ Banner Yükle", height=36, fg_color=RENKLER["vurgu"],
                      command=sec_banner_dosya).pack(side="left", padx=5)
        def kaydet():
            p["ad"] = e_ad.get() or "Arda"
            p["etiket"] = e_etiket.get() or "0000"
            p["biyografi"] = e_bio.get()
            p["unvan"] = uv.get()
            p["cerceve"] = cv.get()
            p["banner_tema"] = bv.get()
            p["avatar_preset"] = avatar_var.get()
            p["renk"] = rv.get()
            save_json(DATA_DOSYASI, self.veri)
            self._rozet_ver("customizer")
            self._xp_ver(20, "profil")
            win.destroy()
            self._profil_side_guncelle()
            self.sayfa_degistir("profil")
        ctk.CTkButton(sc, text="💾 Kaydet", height=44, fg_color=RENKLER["yesil"],
                      hover_color="#16A34A", command=kaydet).pack(fill="x", pady=15)

    # ============ OYUN DETAY (SYS + REVIEWS) ============
    def oyun_detay_goster(self, oid):
        self.secili_oyun = oid
        oyun = self.oyunlar[oid]
        try: self._scroll_kaydet(self.aktif_sayfa)
        except Exception: pass
        for w in self.icerik.winfo_children():
            try: w.destroy()
            except Exception: pass
        try:
            ctk.CTkButton(self.icerik, text="← Geri", width=80, fg_color="transparent",
                          command=lambda: self.sayfa_degistir(self.aktif_sayfa)).pack(anchor="w", pady=(0, 10))

            banner = ctk.CTkLabel(self.icerik, text="", height=200)
            banner.pack(fill="x", pady=(0, 15))
            self.gorsel_yukle_guvenli(banner, oid, "detay_banner",
                oyun.get("banner_urls", oyun.get("kapak_urls", [])),
                (1080, 200), oyun["isim"], oyun["tur"], overlay=True)

            tr = ctk.CTkFrame(self.icerik, fg_color="transparent")
            tr.pack(fill="x", pady=(0, 5))
            ctk.CTkLabel(tr, text=oyun["isim"], font=ctk.CTkFont(size=28, weight="bold"),
                         text_color=RENKLER["metin"]).pack(side="left")
            fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
            ctk.CTkButton(tr, text="❤️" if fav else "🤍", width=50, height=34,
                          fg_color=RENKLER["yan"],
                          command=lambda: self.favori_degistir(oid, True)).pack(side="right", padx=4)
            in_wish = oid in self.veri.get("istek_listesi", [])
            ctk.CTkButton(tr, text="⭐ İstekte" if in_wish else "☆ İstek", width=100, height=34,
                          fg_color=RENKLER["yan"],
                          command=lambda: self._toggle_wishlist(oid)).pack(side="right", padx=4)

            fiyat = oyun.get("fiyat", 0)
            meta = f"{oyun['tur']} • "
            if oyun.get("steam_appid"): meta += f"AppID: {oyun['steam_appid']} • "
            meta += "🆓 BEDAVA" if fiyat == 0 else f"💎 {fiyat:,} Kredi"
            ctk.CTkLabel(self.icerik, text=meta, font=ctk.CTkFont(size=12),
                         text_color=RENKLER["soluk"], anchor="w").pack(fill="x")
            ctk.CTkLabel(self.icerik, text=oyun.get("aciklama", ""), wraplength=1000,
                         justify="left", font=ctk.CTkFont(size=13),
                         text_color=RENKLER["soluk"], anchor="w").pack(fill="x", pady=(10, 15))

            # System requirements comparison
            self._render_system_compare(oyun)

            kurulu = self._kurulu_mu(oid, oyun)
            satin_alindi = oid in self.veri.get("satın_alınan", []) or fiyat == 0

            self.detay_bar = ctk.CTkProgressBar(self.icerik, height=10, progress_color=RENKLER["vurgu"])
            self.detay_bar.pack(fill="x", pady=(5, 5)); self.detay_bar.set(0)
            self.detay_lbl = ctk.CTkLabel(self.icerik, text="Hazır", font=ctk.CTkFont(size=11),
                                           text_color=RENKLER["soluk"], anchor="w")
            self.detay_lbl.pack(fill="x", pady=(0, 10))

            br = ctk.CTkFrame(self.icerik, fg_color="transparent")
            br.pack(fill="x", pady=10)

            if oyun.get("steam_appid"):
                appid = oyun["steam_appid"]
                if kurulu:
                    ctk.CTkButton(br, text="▶ OYNA (Steam)", height=48,
                                  font=ctk.CTkFont(size=15, weight="bold"),
                                  fg_color=RENKLER["yesil"],
                                  command=lambda a=appid, o=oid: self._steam_play_action(o, a)).pack(side="left", fill="x", expand=True, padx=(0, 5))
                elif not satin_alindi and fiyat > 0:
                    ctk.CTkButton(br, text=f"💎 {fiyat:,} Kredi ile Satın Al", height=48,
                                  font=ctk.CTkFont(size=15, weight="bold"),
                                  fg_color=RENKLER["altin"], text_color="#0B0E14",
                                  command=lambda o=oid, a=appid, pr=fiyat: self._buy_and_install(o, a, pr)).pack(side="left", fill="x", expand=True, padx=(0, 5))
                else:
                    ctk.CTkButton(br, text="⚡ Steam Üzerinden Yükle", height=48,
                                  font=ctk.CTkFont(size=15, weight="bold"),
                                  fg_color=RENKLER["vurgu"],
                                  command=lambda a=appid: self._steam_install_action(a)).pack(side="left", fill="x", expand=True, padx=(0, 5))
            elif not satin_alindi and fiyat > 0:
                ctk.CTkButton(br, text=f"💎 {fiyat:,} Kredi ile Satın Al", height=48,
                              font=ctk.CTkFont(size=15, weight="bold"),
                              fg_color=RENKLER["altin"], text_color="#0B0E14",
                              command=lambda o=oid, pr=fiyat: self._buy_game(o, pr)).pack(side="left", fill="x", expand=True, padx=(0, 5))
            elif kurulu:
                ctk.CTkButton(br, text="▶ OYNA", height=48, font=ctk.CTkFont(size=15, weight="bold"),
                              fg_color=RENKLER["yesil"],
                              command=lambda: self.oyna(oid)).pack(side="left", fill="x", expand=True, padx=(0, 5))
            else:
                btn = ctk.CTkButton(br, text="📥 İndir", height=48, font=ctk.CTkFont(size=15, weight="bold"),
                                     fg_color=RENKLER["vurgu"])
                btn.configure(command=lambda b=btn: self._start_download_animated(oid, b))
                btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

            # Reviews
            self._render_reviews_section(oid)
        except Exception: traceback.print_exc()

    def _render_system_compare(self, oyun):
        try:
            sf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=10)
            sf.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(sf, text="🖥️ Sistem Karşılaştırması",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(10, 5))
            my_ram = toplam_ram_gb()
            need_ram = oyun.get("min_ram", 2)
            my_cpu = sistem_cpu_cores()
            need_cpu = 2
            rows = [("RAM", f"{my_ram:.1f} GB", f"{need_ram} GB", my_ram >= need_ram),
                    ("CPU Çekirdek", f"{my_cpu}", f"{need_cpu}", my_cpu >= need_cpu),
                    ("İşletim Sistemi", "Windows 10/11", "Windows 7+", True)]
            tbl = ctk.CTkFrame(sf, fg_color="transparent"); tbl.pack(fill="x", padx=15, pady=(0, 10))
            for i in range(4): tbl.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(tbl, text="Bileşen", font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(tbl, text="Sizin", font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(tbl, text="Gerekli", font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).grid(row=0, column=2, sticky="w")
            ctk.CTkLabel(tbl, text="Durum", font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).grid(row=0, column=3, sticky="w")
            for i, (lbl, mine, need, ok) in enumerate(rows, start=1):
                ctk.CTkLabel(tbl, text=lbl, font=ctk.CTkFont(size=11)).grid(
                    row=i, column=0, sticky="w", pady=2)
                ctk.CTkLabel(tbl, text=mine, font=ctk.CTkFont(size=11),
                             text_color=RENKLER["metin"]).grid(row=i, column=1, sticky="w", pady=2)
                ctk.CTkLabel(tbl, text=need, font=ctk.CTkFont(size=11)).grid(
                    row=i, column=2, sticky="w", pady=2)
                ctk.CTkLabel(tbl, text="✅ Uyumlu" if ok else "⚠️ Yetersiz",
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=RENKLER["yesil"] if ok else RENKLER["kirmizi"]).grid(
                    row=i, column=3, sticky="w", pady=2)
        except Exception: traceback.print_exc()

    def _render_reviews_section(self, oid):
        try:
            rf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=10)
            rf.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(rf, text="📝 İnceleme & Puanım",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(10, 5))
            rv = self.veri.get("incelemeler", {}).get(oid, {})
            star_frame = ctk.CTkFrame(rf, fg_color="transparent")
            star_frame.pack(anchor="w", padx=15, pady=5)
            ctk.CTkLabel(star_frame, text="Puan:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(side="left", padx=(0, 8))
            star_var = ctk.IntVar(value=rv.get("yildiz", 0))
            for i in range(1, 6):
                btn = ctk.CTkButton(star_frame, text=f"★{i}", width=50, height=30,
                                     fg_color=RENKLER["vurgu"] if i == star_var.get() else RENKLER["yan"],
                                     command=lambda i=i: (star_var.set(i),
                                                          [b.configure(fg_color=RENKLER["vurgu"] if j == i else RENKLER["yan"])
                                                           for j, b in enumerate(star_frame.winfo_children()[1:], 1)]))
                btn.pack(side="left", padx=2)
            ctk.CTkLabel(rf, text="Yorum:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(anchor="w", padx=15, pady=(8, 2))
            txt = ctk.CTkTextbox(rf, height=80, fg_color=RENKLER["yan"],
                                  text_color=RENKLER["metin"], font=ctk.CTkFont(size=12))
            txt.pack(fill="x", padx=15, pady=(0, 6))
            txt.insert("1.0", rv.get("metin", ""))
            def kaydet():
                try:
                    yildiz = star_var.get()
                    if yildiz < 1:
                        messagebox.showinfo("Bilgi", "Lütfen 1-5 yıldız verin."); return
                    self.veri["incelemeler"][oid] = {
                        "yildiz": yildiz,
                        "metin": txt.get("1.0", "end-1c"),
                        "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    save_json(DATA_DOSYASI, self.veri)
                    self._rozet_ver("reviewer")
                    self.durum("İnceleme kaydedildi.")
                    self.oyun_detay_goster(oid)
                except Exception: traceback.print_exc()
            ctk.CTkButton(rf, text="💾 İncelemeyi Kaydet", height=34,
                          fg_color=RENKLER["yesil"],
                          command=kaydet).pack(anchor="e", padx=15, pady=(0, 15))
        except Exception: traceback.print_exc()

    def _toggle_wishlist(self, oid):
        wl = self.veri.setdefault("istek_listesi", [])
        if oid in wl:
            wl.remove(oid); self.durum("İstekten kaldırıldı.")
        else:
            wl.append(oid); self.durum("İsteğe eklendi.")
            self._rozet_ver("wishlister")
            self._quest_progress("daily_fav")
        save_json(DATA_DOSYASI, self.veri)
        self.oyun_detay_goster(oid)

    def _buy_game(self, oid, fiyat):
        oyun = self.oyunlar[oid]
        if self.veri["profil"].get("kredi", 0) < fiyat:
            messagebox.showerror("Yetersiz Kredi",
                f"Gerekli: {fiyat:,} Kredi\nMevcut: {self.veri['profil'].get('kredi', 0):,}"); return
        if not messagebox.askyesno("Satın Al", f"'{oyun['isim']}' {fiyat:,} Kredi ile alınsın mı?"): return
        if self._kredi_harca(fiyat):
            self.veri.setdefault("satın_alınan", []).append(oid)
            save_json(DATA_DOSYASI, self.veri)
            self._rozet_ver("first_purchase")
            self._quest_progress("weekly_buy")
            self.durum(f"✅ '{oyun['isim']}' satın alındı!")
            self.oyun_detay_goster(oid)

    def _buy_and_install(self, oid, appid, fiyat):
        if not messagebox.askyesno("Satın Al + Yükle",
            f"'{self.oyunlar[oid]['isim']}' {fiyat:,} Kredi ile satın alıp Steam'i açmak ister misiniz?"): return
        if self._kredi_harca(fiyat):
            self.veri.setdefault("satın_alınan", []).append(oid)
            save_json(DATA_DOSYASI, self.veri)
            self._rozet_ver("first_purchase")
            self._quest_progress("weekly_buy")
            self._steam_install_action(appid)

    def _steam_play_action(self, oid, appid):
        if _steam_launch(appid):
            self._xp_ver(50, "oyun")
            self._aktivite_ekle(f"{self.oyunlar[oid]['isim']} başlatıldı")
            self.durum(f"{self.oyunlar[oid]['isim']} başlatıldı.")
        else:
            messagebox.showerror("Hata", "Steam başlatılamadı.")

    def _steam_install_action(self, appid):
        if not _steam_install_path() and sys.platform == "win32":
            if messagebox.askyesno("Steam Bulunamadı",
                "Steam yüklü değil. Resmi indirme sayfası açılsın mı?"):
                webbrowser.open("https://store.steampowered.com/about/")
            return
        if _steam_install(appid):
            messagebox.showinfo("Steam Yükleyici Açıldı", "Steam yükleme penceresi açıldı.")
        else:
            if messagebox.askyesno("Hata", "Steam başlatılamadı. Web sayfası açılsın mı?"):
                webbrowser.open(f"https://store.steampowered.com/app/{appid}/")

    def favori_degistir(self, oid, detail=False):
        v = self.veri["oyunlar"].setdefault(oid, {})
        v["favori"] = not v.get("favori", False)
        save_json(DATA_DOSYASI, self.veri)
        if v["favori"]:
            self._quest_progress("daily_fav")
        if detail and self.secili_oyun == oid:
            self.oyun_detay_goster(oid)
        else:
            try: saved_pos = self.icerik._parent_canvas.yview()[0]
            except Exception: saved_pos = 0.0
            self.sayfa_degistir(self.aktif_sayfa)
            if saved_pos > 0.001:
                self.after(50, lambda p=saved_pos: self._scroll_geri_yukle(p))

    def detay_ilerleme(self, oid, y, h, i, t, e):
        try:
            if self.secili_oyun == oid and hasattr(self, "detay_bar"):
                self.detay_bar.set(y)
                self.detay_lbl.configure(text=f"{fmt_bayt(i)}/{fmt_bayt(t)} • {h:.2f} MB/s • {y*100:.1f}%")
        except Exception: pass

    def detay_durum_metni(self, oid, mesaj):
        try:
            if self.secili_oyun == oid and hasattr(self, "detay_lbl"):
                self.detay_lbl.configure(text=mesaj)
        except Exception: pass

    def indirme_basarili(self, oid, exe, asset):
        self.veri["oyunlar"].setdefault(oid, {})["exe_yolu"] = str(exe)
        self.veri["oyunlar"][oid]["asset"] = asset
        self.veri["indirme_sayaci"] = self.veri.get("indirme_sayaci", 0) + 1
        save_json(DATA_DOSYASI, self.veri)
        self._rozet_guncelle()
        self._xp_ver(100, "oyun_indir")
        self._render_quick_access()
        if self.secili_oyun == oid: self.oyun_detay_goster(oid)
        else: self.sayfa_degistir(self.aktif_sayfa)

    def indirme_hatali(self, oid, hata):
        self._rozet_guncelle()
        messagebox.showerror("İndirme Hatası", f"{self.oyunlar.get(oid, {}).get('isim', oid)}:\n{hata}")

    def _rozet_guncelle(self):
        try:
            n = len(self.download_engine.aktif)
            if n > 0: self.indirme_rozet.configure(text=str(n)); self.indirme_rozet.grid()
            else: self.indirme_rozet.grid_remove()
        except Exception: pass

    def _start_download_animated(self, oid, btn):
        self._shimmer(btn)
        self.download_engine.baslat(oid, self.oyunlar[oid])
        self._rozet_guncelle()

    def oyna(self, oid):
        oyun = self.oyunlar[oid]
        if oyun.get("steam_appid"):
            self._steam_play_action(oid, oyun["steam_appid"]); return
        exe = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if not exe or not Path(exe).exists():
            k = self.oyunlar_dizini / oid
            b = list(k.rglob(oyun["exe_adi"])) if k.exists() else []
            if b: exe = str(b[0])
        if not exe or not Path(exe).exists():
            messagebox.showerror("Hata", "Oyun dosyası bulunamadı."); return
        gb = self.veri["settings"].get("game_booster", True)
        mn = self.veri["settings"].get("minimize_on_play", False)
        cwd = str(Path(exe).parent)
        try:
            proc = yuksek_oncelik(exe, cwd) if gb else subprocess.Popen([exe], cwd=cwd)
            if gb: self._rozet_ver("booster")
            self._xp_ver(50, "oyun")
            if mn:
                try: self.iconify()
                except Exception: pass
            threading.Thread(target=self._sure_izle, args=(oid, proc), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def _sure_izle(self, oid, proc):
        bas = time.time()
        try: proc.wait()
        except Exception: pass
        gecen = time.time() - bas
        v = self.veri["oyunlar"].setdefault(oid, {})
        v["oynama_suresi"] = v.get("oynama_suresi", 0) + gecen
        v["son_oynama"] = time.time()
        bugun = datetime.now().strftime("%Y-%m-%d")
        self.veri["gunluk_oynama"][bugun] = self.veri["gunluk_oynama"].get(bugun, 0) + gecen
        dakika = int(gecen / 60)
        if dakika >= 1:
            self._quest_progress("daily_play", delta=dakika)
        kazanc = int(gecen / 300) * 150
        if kazanc > 0:
            self.veri["profil"]["kredi"] = self.veri["profil"].get("kredi", 0) + kazanc
            self.after(0, lambda: self.durum(f"🎮 +{kazanc} Kredi oynama ödülü!"))
            self.after(0, self._kredi_guncelle)
        save_json(DATA_DOSYASI, self.veri)
        if self.veri["settings"].get("restore_after_game", True):
            self.after(0, lambda: self.deiconify())

    # ============ GELİŞTİRİCİ CTRL+SHIFT+D ============
    def _open_pin_dialog(self):
        win = ctk.CTkToplevel(self); win.title("Geliştirici Erişimi")
        win.geometry("380x220"); win.configure(fg_color=RENKLER["arka"])
        win.transient(self); win.grab_set()
        ctk.CTkLabel(win, text="🔒 Geliştirici PIN", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=RENKLER["metin"]).pack(pady=(20, 10))
        ctk.CTkLabel(win, text="4 haneli PIN girin:", font=ctk.CTkFont(size=12),
                     text_color=RENKLER["soluk"]).pack()
        entry = ctk.CTkEntry(win, height=38, fg_color=RENKLER["kart"], show="•",
                              font=ctk.CTkFont(size=16), justify="center")
        entry.pack(fill="x", padx=30, pady=15); entry.focus_set()
        def kontrol():
            if entry.get() == str(self._dev_pin):
                win.destroy(); self._open_dev_panel()
            else:
                messagebox.showerror("Hatalı PIN", "PIN yanlış.")
        ctk.CTkButton(win, text="Giriş", height=36, fg_color=RENKLER["yesil"],
                      command=kontrol).pack(fill="x", padx=30, pady=(0, 15))
        entry.bind("<Return>", lambda e: kontrol())

    def _open_dev_panel(self):
        win = ctk.CTkToplevel(self); win.title("Gizli Geliştirici Modu")
        win.geometry("640x780"); win.configure(fg_color=RENKLER["arka"])
        win.transient(self); win.grab_set()
        sc = ctk.CTkScrollableFrame(win, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(sc, text="🚀 Gizli Geliştirici Modu", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=RENKLER["altin"]).pack(pady=(5, 15))
        d = self.veri.get("dev", {})
        def _row(lbl, val, show=None):
            ctk.CTkLabel(sc, text=lbl, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(anchor="w", pady=(4, 2))
            e = ctk.CTkEntry(sc, height=32, fg_color=RENKLER["kart"], text_color=RENKLER["metin"], show=show or "")
            e.pack(fill="x", pady=(0, 4)); e.insert(0, val); return e
        owner_e = _row("GitHub Owner:", d.get("owner", DEFAULT_GH_OWNER))
        repo_e = _row("GitHub Repo:", d.get("repo", DEFAULT_GH_REPO))
        token_e = _row("GitHub PAT:", d.get("token", ""), show="•")
        branch_e = _row("Branch:", d.get("branch", DEFAULT_GH_BRANCH))
        ver_e = _row("Yeni Sürüm:", "9.2")
        ctk.CTkLabel(sc, text="Yayın Notları:", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(4, 2))
        notes_box = ctk.CTkTextbox(sc, height=70, fg_color=RENKLER["kart"], text_color=RENKLER["metin"])
        notes_box.pack(fill="x", pady=(0, 8)); notes_box.insert("1.0", d.get("notes", ""))
        progress = ctk.CTkProgressBar(sc, height=8, progress_color=RENKLER["altin"])
        progress.pack(fill="x", pady=(4, 4)); progress.set(0)
        status_lbl = ctk.CTkLabel(sc, text="Hazır", font=ctk.CTkFont(size=10),
                                    text_color=RENKLER["soluk"])
        status_lbl.pack(anchor="w", pady=(0, 10))
        def publish():
            owner = owner_e.get().strip(); repo = repo_e.get().strip()
            token = token_e.get().strip(); branch = branch_e.get().strip()
            nv = ver_e.get().strip(); notes = notes_box.get("1.0", "end-1c").strip()
            if not (owner and repo and token and nv):
                messagebox.showerror("Eksik", "Tüm alanları doldurun."); return
            script = _get_script_path()
            if not script:
                messagebox.showerror("Hata", "launcher.pyw yolu yok."); return
            d.update({"owner": owner, "repo": repo, "token": token, "branch": branch,
                      "next_version": nv, "notes": notes})
            self.veri["dev"] = d; save_json(DATA_DOSYASI, self.veri)
            status_lbl.configure(text="⏳ Yayınlanıyor...", text_color=RENKLER["sari"])
            def cb(msg, pct):
                def u():
                    try:
                        status_lbl.configure(text=f"⏳ {msg}")
                        progress.set(pct/100)
                    except Exception: pass
                self.after(0, u)
            def work():
                try:
                    pub = GitHubPublisher(token, owner, repo, branch)
                    res = pub.publish_all(script, nv, notes, catalog_data=None, progress_cb=cb)
                    def done():
                        if res.get("ok"):
                            status_lbl.configure(text=f"✅ Yayınlandı! v{nv}", text_color=RENKLER["yesil"])
                            progress.set(1.0)
                            messagebox.showinfo("Başarılı", f"v{nv} yayınlandı!")
                        else:
                            status_lbl.configure(text=f"❌ {res.get('error','?')[:50]}",
                                                  text_color=RENKLER["kirmizi"])
                            messagebox.showerror("Hata", f"{res.get('step','?')}: {res.get('error','?')}")
                    self.after(0, done)
                except Exception as e:
                    err = str(e)
                    self.after(0, lambda: status_lbl.configure(text=f"❌ {err[:50]}",
                                                                 text_color=RENKLER["kirmizi"]))
            threading.Thread(target=work, daemon=True).start()
        ctk.CTkButton(sc, text="🚀 Yayınla (4 Dosya)", height=42, fg_color=RENKLER["yesil"],
                      command=publish).pack(fill="x", pady=8)
        ctk.CTkButton(sc, text="💰 +10.000 Kredi", height=38, fg_color=RENKLER["altin"],
                      text_color="#0B0E14",
                      command=lambda: (self._kredi_ver(10000, "dev"),
                                       messagebox.showinfo("Tamam", "+10.000 Kredi eklendi."))).pack(fill="x", pady=4)
        def add_game():
            ad = ctk.CTkInputDialog(text="Oyun adı:", title="Oyun Ekle").get_input()
            if not ad: return
            appid_str = ctk.CTkInputDialog(text="Steam AppID:", title="Oyun Ekle").get_input()
            if not appid_str: return
            try: appid = int(appid_str)
            except Exception:
                messagebox.showerror("Hata", "Geçersiz AppID."); return
            fiyat_str = ctk.CTkInputDialog(text="Fiyat (0=bedava):", title="Oyun Ekle").get_input() or "0"
            try: fiyat = int(fiyat_str)
            except Exception: fiyat = 0
            oid = f"custom_{appid}"
            entry = _mk(appid, ad, "Aksiyon", fiyat)
            self.oyunlar[oid] = entry
            self.veri["eklenen_oyunlar"][oid] = entry
            save_json(DATA_DOSYASI, self.veri)
            messagebox.showinfo("Eklendi", f"'{ad}' eklendi.")
            self.sayfa_degistir("gozat")
        ctk.CTkButton(sc, text="➕ Yeni Oyun Ekle", height=38, fg_color=RENKLER["vurgu"],
                      command=add_game).pack(fill="x", pady=4)
        ctk.CTkLabel(sc, text=f"PIN: {self._dev_pin}", font=ctk.CTkFont(size=10),
                     text_color=RENKLER["soluk"]).pack(pady=(15, 0))

    # ============ AYARLAR ============
    def _page_ayarlar(self):
        try:
            ctk.CTkLabel(self.icerik, text="⚙️ Ayarlar Merkezi", font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=RENKLER["metin"], anchor="w").pack(fill="x", pady=(0, 15))
            tabs = ctk.CTkTabview(self.icerik, fg_color=RENKLER["kart"],
                                  segmented_button_fg_color=RENKLER["yan"],
                                  segmented_button_selected_color=RENKLER["vurgu"])
            tabs.pack(fill="x", pady=5)
            t1 = tabs.add("📁 Dizin"); t2 = tabs.add("🌐 Ağ"); t3 = tabs.add("⚡ Performans")
            t4 = tabs.add("🎨 Görünüm"); t5 = tabs.add("🔔 Ses"); t6 = tabs.add("🛠️ Bakım")

            # Dizin
            f = ctk.CTkFrame(t1, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(f, text="Sistem Veri Dizini:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
            r1 = ctk.CTkFrame(f, fg_color="transparent"); r1.pack(fill="x", pady=(0, 8))
            self.sys_path_entry = ctk.CTkEntry(r1, height=32, fg_color=RENKLER["yan"], text_color=RENKLER["metin"])
            self.sys_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.sys_path_entry.insert(0, str(BASE_DIR))
            ctk.CTkButton(r1, text="📁 Gözat", width=80, height=32, fg_color=RENKLER["vurgu"],
                          command=self.sistem_dizin_sec).pack(side="left", padx=2)
            ctk.CTkButton(r1, text="✅", width=50, height=32, fg_color=RENKLER["yesil"],
                          command=lambda: self._sistem_dizin_uygula(self.sys_path_entry.get())).pack(side="left", padx=2)

            ctk.CTkLabel(f, text="Oyun Kurulum Klasörü:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(8, 2))
            r2 = ctk.CTkFrame(f, fg_color="transparent"); r2.pack(fill="x", pady=(0, 8))
            self.games_path_entry = ctk.CTkEntry(r2, height=32, fg_color=RENKLER["yan"], text_color=RENKLER["metin"])
            self.games_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.games_path_entry.insert(0, str(self.oyunlar_dizini))
            ctk.CTkButton(r2, text="📁 Gözat", width=80, height=32, fg_color=RENKLER["vurgu"],
                          command=self.games_dizin_sec).pack(side="left", padx=2)
            ctk.CTkButton(r2, text="✅", width=50, height=32, fg_color=RENKLER["yesil"],
                          command=lambda: self._oyun_dizin_uygula(self.games_path_entry.get())).pack(side="left", padx=2)

            ctk.CTkLabel(f, text="Kayıt Yedekleme Klasörü:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(8, 2))
            r3 = ctk.CTkFrame(f, fg_color="transparent"); r3.pack(fill="x", pady=(0, 8))
            self.backups_path_entry = ctk.CTkEntry(r3, height=32, fg_color=RENKLER["yan"], text_color=RENKLER["metin"])
            self.backups_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.backups_path_entry.insert(0, str(self.yedek_dizini))
            ctk.CTkButton(r3, text="📁 Gözat", width=80, height=32, fg_color=RENKLER["vurgu"],
                          command=self.backups_dizin_sec).pack(side="left", padx=2)
            ctk.CTkButton(r3, text="✅", width=50, height=32, fg_color=RENKLER["yesil"],
                          command=lambda: self._yedek_dizin_uygula(self.backups_path_entry.get())).pack(side="left", padx=2)

            try:
                total, used, free = disk_usage_gb(self.oyunlar_dizini)
                df = ctk.CTkFrame(f, fg_color=RENKLER["yan"], corner_radius=8)
                df.pack(fill="x", pady=(10, 5))
                ctk.CTkLabel(df, text=f"💽 {used:.1f}/{total:.1f} GB dolu",
                             font=ctk.CTkFont(size=11), text_color=RENKLER["metin"]).pack(
                    anchor="w", padx=10, pady=(6, 3))
                db = ctk.CTkProgressBar(df, height=8, progress_color=RENKLER["vurgu"])
                db.pack(fill="x", padx=10, pady=(0, 8)); db.set(used/total if total > 0 else 0)
            except Exception: pass

            # Ağ
            g = ctk.CTkFrame(t2, fg_color="transparent"); g.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(g, text="İndirme Hız Limiti:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
            sm = {0: "Sınırsız", 5: "5 MB/s", 10: "10 MB/s", 25: "25 MB/s", 50: "50 MB/s"}
            ctk.CTkOptionMenu(g, values=list(sm.values()), width=200, fg_color=RENKLER["yan"],
                              command=lambda v: self._set_speed(v)).pack(anchor="w", pady=(0, 8))
            ctk.CTkButton(g, text="🔍 Tanılama", height=34, fg_color=RENKLER["vurgu"],
                          command=self._diagnostics).pack(fill="x", pady=10)

            # Performans
            h = ctk.CTkFrame(t3, fg_color="transparent"); h.pack(fill="x", padx=10, pady=5)
            ctk.CTkSwitch(h, text="Windows başlangıcı", fg_color=RENKLER["vurgu"],
                          command=lambda: self._set_startup(True)).pack(anchor="w", pady=4)
            ctk.CTkSwitch(h, text="Game Booster", fg_color=RENKLER["vurgu"]).pack(anchor="w", pady=4)
            ctk.CTkSwitch(h, text="Oyun kapanınca launcher'ı geri getir", fg_color=RENKLER["vurgu"]).pack(anchor="w", pady=4)

            # Görünüm
            i = ctk.CTkFrame(t4, fg_color="transparent"); i.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(i, text="Tema Rengi:", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 4))
            tf = ctk.CTkFrame(i, fg_color="transparent"); tf.pack(anchor="w", pady=(0, 10))
            for ak, tt in TEMALAR.items():
                ctk.CTkButton(tf, text=tt["ad"][:8], width=85, height=30, fg_color=tt["renk"],
                              command=lambda a=ak: self.tema_degistir(a)).pack(side="left", padx=2)
            ctk.CTkLabel(i, text="Pencere Şeffaflığı:", font=ctk.CTkFont(size=11),
                         text_color=RENKLER["soluk"]).pack(anchor="w", pady=(8, 2))
            ctk.CTkSlider(i, from_=0.85, to=1.0, number_of_steps=15,
                          command=lambda v: self.attributes("-alpha", v)).pack(fill="x", pady=(0, 8))

            # Ses
            s = ctk.CTkFrame(t5, fg_color="transparent"); s.pack(fill="x", padx=10, pady=5)
            ctk.CTkSwitch(s, text="Ses efektleri", fg_color=RENKLER["vurgu"]).pack(anchor="w", pady=4)
            ctk.CTkSwitch(s, text="Masaüstü bildirimleri", fg_color=RENKLER["vurgu"]).pack(anchor="w", pady=4)
            ctk.CTkSwitch(s, text="Günlük hatırlatıcı", fg_color=RENKLER["vurgu"]).pack(anchor="w", pady=4)

            # Bakım
            j = ctk.CTkFrame(t6, fg_color="transparent"); j.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(j, text=f"Sürüm: v{APP_VERSION}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 4))
            ctk.CTkButton(j, text="🔍 Güncelleme Denetle", height=36, fg_color=RENKLER["vurgu"],
                          command=self._manuel_guncelleme_denetle).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="🖥️ Kısayol Oluştur", height=36, fg_color=RENKLER["vurgu"],
                          command=lambda: self.masaustu_kisayolu_olustur(False)).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="📦 Installer .bat Dışa Aktar", height=36,
                          fg_color=RENKLER["neon_mavi"], text_color="#0B0E14",
                          command=self._export_installer_bat).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="📤 JSON Dışa", height=36, fg_color=RENKLER["yesil"],
                          command=self.disa_aktar).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="📥 JSON İçe", height=36, fg_color=RENKLER["sari"],
                          command=self.ice_aktar).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="🖼️ Kapak Temizle", height=36, fg_color=RENKLER["yan"],
                          command=self.onb_temizle).pack(fill="x", pady=3)
            ctk.CTkButton(j, text="🚨 Tamamen Kaldır", height=40, fg_color=RENKLER["kirmizi"],
                          command=self.launcher_uninstall).pack(fill="x", pady=(10, 5))
        except Exception: traceback.print_exc()

    def _set_speed(self, val):
        m = {"Sınırsız": 0, "5 MB/s": 5, "10 MB/s": 10, "25 MB/s": 25, "50 MB/s": 50}
        self.veri["settings"]["download_speed_limit"] = m.get(val, 0)
        save_json(DATA_DOSYASI, self.veri)

    def _diagnostics(self):
        def work():
            try:
                t0 = time.time()
                r = requests.get("https://api.github.com", timeout=5)
                ping = (time.time() - t0) * 1000
                steam = _steam_install_path()
                msg = f"🌐 İnternet: ✅ ({ping:.0f} ms)\n"
                msg += f"🎮 Steam: {'✅ ' + str(steam) if steam else '❌ Yok'}\n"
                msg += f"🔗 GitHub: {'✅' if r.status_code == 200 else '❌ ' + str(r.status_code)}\n"
                self.after(0, lambda: messagebox.showinfo("Tanılama", msg))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: messagebox.showerror("Hata", err))
        threading.Thread(target=work, daemon=True).start()

    def sistem_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(BASE_DIR))
        if yeni: self._sistem_dizin_uygula(yeni)

    def _sistem_dizin_uygula(self, yol):
        global BASE_DIR, CACHE_COVERS, PROFILE_CACHE, MODS_DIR, DATA_DOSYASI, ICON_DOSYASI
        yol = (yol or "").strip()
        if not yol: return
        try: newp = Path(yol).resolve()
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        try:
            if newp == BASE_DIR.resolve(): self.durum("Zaten bu dizin."); return
        except Exception: pass
        if not messagebox.askyesno("Taşıma", f"Veriler şuraya taşınacak:\n{newp}"): return
        eski_dizin = BASE_DIR
        try:
            newp.mkdir(parents=True, exist_ok=True)
            for item in [DATA_DOSYASI, ICON_DOSYASI]:
                try:
                    if item.exists():
                        tgt = newp / item.name
                        if tgt.exists(): tgt.unlink()
                        shutil.move(str(item), str(tgt))
                except Exception: pass
            for folder in [CACHE_COVERS, PROFILE_CACHE, MODS_DIR]:
                try:
                    if folder.exists() and folder.resolve().parent == eski_dizin.resolve():
                        tgt = newp / folder.name
                        if tgt.exists(): shutil.rmtree(tgt, ignore_errors=True)
                        shutil.move(str(folder), str(tgt))
                except Exception: pass
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"base_dir": str(newp)}, f, indent=2)
            BASE_DIR = newp; CACHE_COVERS = BASE_DIR / "cache_covers"
            PROFILE_CACHE = BASE_DIR / "arda_profile_cache"; MODS_DIR = BASE_DIR / "mods"
            DATA_DOSYASI = BASE_DIR / "arda_launcher_data.json"; ICON_DOSYASI = BASE_DIR / "arda_icon.ico"
            for _d in (CACHE_COVERS, PROFILE_CACHE, MODS_DIR): _d.mkdir(parents=True, exist_ok=True)
            icon_olustur(); self._pencere_ikonu_uygula()
            messagebox.showinfo("Başarılı", f"✅ Taşındı: {newp}\nYeniden başlatın.")
            self.sayfa_degistir("ayarlar")
        except Exception as e: messagebox.showerror("Hata", str(e))

    def games_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(self.oyunlar_dizini))
        if yeni: self._oyun_dizin_uygula(yeni)
    def _oyun_dizin_uygula(self, yol):
        yol = (yol or "").strip()
        if not yol: return
        p = Path(yol)
        try: p.mkdir(parents=True, exist_ok=True)
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        self.oyunlar_dizini = p; self.veri["indirme_dizini"] = str(p)
        save_json(DATA_DOSYASI, self.veri)
        messagebox.showinfo("Başarılı", f"✅ {p}")
    def backups_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(self.yedek_dizini))
        if yeni: self._yedek_dizin_uygula(yeni)
    def _yedek_dizin_uygula(self, yol):
        yol = (yol or "").strip()
        if not yol: return
        p = Path(yol)
        try: p.mkdir(parents=True, exist_ok=True)
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        self.yedek_dizini = p; self.veri["yedek_dizini"] = str(p)
        save_json(DATA_DOSYASI, self.veri)
        messagebox.showinfo("Başarılı", f"✅ {p}")

    def masaustu_kisayolu_olustur(self, sessiz=False):
        if sys.platform != "win32":
            if not sessiz: messagebox.showinfo("Bilgi", "Sadece Windows.")
            return False
        try:
            py = sys.executable; pyw = py.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pyw): pyw = py
            script = _get_script_path() or os.path.abspath(sys.argv[0])
            icon = str(ICON_DOSYASI) if ICON_DOSYASI.exists() else pyw
            desktop = win_desktop_path(); desktop.mkdir(parents=True, exist_ok=True)
            lnk = desktop / "ARDA LAUNCHER.lnk"
            vbs = ('Set oWS = WScript.CreateObject("WScript.Shell")\r\n'
                   f'Set oLink = oWS.CreateShortcut("{str(lnk)}")\r\n'
                   f'oLink.TargetPath = "{pyw}"\r\n'
                   f'oLink.Arguments = """{script}"""\r\n'
                   f'oLink.WorkingDirectory = "{str(BASE_DIR)}"\r\n'
                   f'oLink.IconLocation = "{icon},0"\r\n'
                   'oLink.Save\r\n')
            tmp = Path(tempfile.gettempdir()) / "arda_shortcut.vbs"
            tmp.write_text(vbs, encoding="utf-8")
            try: subprocess.run(["cscript", "//nologo", str(tmp)], creationflags=0x08000000,
                                capture_output=True, timeout=15)
            finally:
                try: tmp.unlink()
                except Exception: pass
            if lnk.exists():
                if not sessiz: messagebox.showinfo("Başarılı", f"✅ {lnk}")
                return True
            return False
        except Exception: return False

    def _ilk_kisayol_olustur(self):
        if sys.platform != "win32": return
        if self.veri.get("desktop_shortcut_created", False): return
        if self.masaustu_kisayolu_olustur(sessiz=True):
            self.veri["desktop_shortcut_created"] = True
            save_json(DATA_DOSYASI, self.veri)

    def _set_startup(self, enabled):
        if not WINREG_OK: return
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if enabled:
                pyw = sys.executable.replace("python.exe", "pythonw.exe")
                if not os.path.exists(pyw): pyw = sys.executable
                cmd = f'"{pyw}" "{_get_script_path() or sys.argv[0]}"'
                winreg.SetValueEx(key, "ArdaLauncher", 0, winreg.REG_SZ, cmd)
            else:
                try: winreg.DeleteValue(key, "ArdaLauncher")
                except FileNotFoundError: pass
            winreg.CloseKey(key)
            self.veri["settings"]["startup_enabled"] = enabled
            save_json(DATA_DOSYASI, self.veri)
        except Exception: pass

    def launcher_uninstall(self):
        if not messagebox.askyesno("Kaldır", "ARDA LAUNCHER tamamen silinecek!"): return
        try:
            lnk = win_desktop_path() / "ARDA LAUNCHER.lnk"
            if lnk.exists(): lnk.unlink()
        except Exception: pass
        try:
            if WINREG_OK:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
                try: winreg.DeleteValue(key, "ArdaLauncher")
                except FileNotFoundError: pass
                winreg.CloseKey(key)
        except Exception: pass
        script = _get_script_path() or sys.argv[0]
        bat = Path(tempfile.gettempdir()) / "arda_uninstall.bat"
        bat.write_text(f'@echo off\r\ntimeout /t 2 /nobreak >nul\r\nrmdir /s /q "{BASE_DIR}" 2>nul\r\n'
                       f'del /f /q "{script}" 2>nul\r\ndel /f /q "%~f0" 2>nul\r\n', encoding="utf-8")
        try: subprocess.Popen(["cmd", "/c", str(bat)],
                              creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS)
        except Exception: pass
        self.destroy(); sys.exit(0)

    def _export_installer_bat(self):
        try:
            d = self.veri.get("dev", {})
            owner = d.get("owner") or DEFAULT_GH_OWNER
            repo = d.get("repo") or DEFAULT_GH_REPO
            branch = d.get("branch") or DEFAULT_GH_BRANCH
            content = generate_installer_bat(owner, repo, branch)
            f = filedialog.asksaveasfilename(parent=self, defaultextension=".bat",
                initialfile="ArdaLauncher_Installer.bat", filetypes=[("Batch", "*.bat")])
            if not f: return
            with open(f, "w", encoding="utf-8", newline="\r\n") as fp: fp.write(content)
            messagebox.showinfo("Başarılı", f"Installer:\n{f}")
        except Exception as e: messagebox.showerror("Hata", str(e))

    def disa_aktar(self):
        try:
            f = filedialog.asksaveasfilename(parent=self, defaultextension=".json",
                initialfile=f"arda_backup_{datetime.now().strftime('%Y%m%d')}.json",
                filetypes=[("JSON", "*.json")])
            if not f: return
            shutil.copy2(DATA_DOSYASI, f)
            messagebox.showinfo("Başarılı", f)
        except Exception as e: messagebox.showerror("Hata", str(e))
    def ice_aktar(self):
        f = filedialog.askopenfilename(parent=self, filetypes=[("JSON", "*.json")])
        if not f: return
        if not messagebox.askyesno("İçe Aktar", "Mevcut veriler değişecek?"): return
        try:
            shutil.copy2(f, DATA_DOSYASI)
            messagebox.showinfo("Başarılı", "İçe aktarıldı. Yeniden başlatın.")
        except Exception as e: messagebox.showerror("Hata", str(e))
    def onb_temizle(self):
        for x in CACHE_COVERS.glob("*"):
            if x.is_file():
                try: x.unlink()
                except Exception: pass
        self.image_refs.clear()
        self.sayfa_degistir("ayarlar")

    def _auto_update_check(self):
        try:
            res = AutoUpdater.check(UPDATE_VERSION_URL, APP_VERSION, timeout=5)
            if res:
                self._update_info = res
                self.after(0, lambda: self.sayfa_degistir(self.aktif_sayfa))
        except Exception: pass

    def _manuel_guncelleme_denetle(self):
        def work():
            try:
                res = AutoUpdater.check(UPDATE_VERSION_URL, APP_VERSION, timeout=5)
                if res:
                    self._update_info = res
                    self.after(0, lambda: messagebox.showinfo("Güncelleme",
                        f"Yeni sürüm: v{res.get('version','?')}"))
                    self.after(0, lambda: self.sayfa_degistir(self.aktif_sayfa))
                else:
                    self.after(0, lambda: messagebox.showinfo("Güncelleme",
                        f"✅ En son sürüm: v{APP_VERSION}"))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: messagebox.showerror("Hata", err))
        threading.Thread(target=work, daemon=True).start()

    def _download_update(self):
        if not self._update_info: return
        url = self._update_info.get("url", "")
        if not url or AutoUpdater.is_placeholder(url):
            messagebox.showerror("Hata", "Geçerli URL yok."); return
        def work():
            try:
                r = requests.get(url, timeout=60, headers=HEADERS)
                if r.status_code != 200: raise RuntimeError(f"HTTP {r.status_code}")
                script = _get_script_path()
                if not script: raise RuntimeError("Yol yok.")
                with open(script + ".new", "wb") as f: f.write(r.content)
                try: os.replace(script + ".new", script)
                except Exception:
                    with open(script, "wb") as f: f.write(r.content)
                self.after(500, lambda: self._restart())
            except Exception as e:
                err = str(e)
                self.after(0, lambda: messagebox.showerror("Hata", err))
        threading.Thread(target=work, daemon=True).start()

    def _restart(self):
        try: self.destroy()
        except Exception: pass
        script = _get_script_path() or sys.argv[0]
        os.execl(sys.executable, sys.executable, script, *sys.argv[1:])

    def _sync_catalog(self):
        try:
            extra = CatalogSync.fetch(CATALOG_URL)
            if extra:
                n = 0
                for oid, entry in extra.items():
                    if oid not in self.oyunlar:
                        self.oyunlar[oid] = entry
                        self.veri["eklenen_oyunlar"][oid] = entry
                        n += 1
                if n:
                    save_json(DATA_DOSYASI, self.veri)
                    self.after(0, lambda: self.durum(f"📥 {n} yeni oyun eklendi!"))
        except Exception: pass


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ArdaLauncher.Ultimate.9.1")
        except Exception: pass
    try:
        app = ArdaLauncher()
        app.mainloop()
    except Exception:
        traceback.print_exc()
        try:
            import tkinter.messagebox as mb
            mb.showerror("ARDA LAUNCHER Başlatma Hatası",
                         "Detaylar için konsolu kontrol edin.")
        except Exception: pass
        raise