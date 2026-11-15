"""
ARDA LAUNCHER v8.3 ZERO-BUG EDITION
Scroll Koruması + In-place Hero Carousel + Self Auto-Updater + Developer Push
"""

import os, sys, io, json, time, math, hashlib, zipfile, shutil, subprocess, threading, ctypes, tempfile, random, re, base64
import xml.etree.ElementTree as ET
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
# SÜRÜM + OTOMATİK GÜNCELLEME SABİTLERİ
# ======================================================================
APP_VERSION = "8.3"
UPDATE_VERSION_URL = "https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/version.json"
UPDATE_CODE_URL = "https://raw.githubusercontent.com/ardafatih707-coder/Game-Launcher/main/launcher.pyw"

# ======================================================================
# DİZİN YÖNETİMİ
# ======================================================================
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".arda_launcher_config.json")

def _get_base_dir() -> Path:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                custom = d.get("base_dir")
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
        if sys.argv and sys.argv[0] and os.path.exists(sys.argv[0]):
            return os.path.abspath(sys.argv[0])
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

def _varsayilan_oyun_dizini() -> Path:
    p = Path(os.path.join(os.path.expanduser("~"), "ArdaLauncherGames"))
    try: p.mkdir(parents=True, exist_ok=True)
    except Exception: pass
    return p

def _varsayilan_yedek_dizini() -> Path:
    p = Path(os.path.join(os.path.expanduser("~"), "ArdaLauncherBackups"))
    try: p.mkdir(parents=True, exist_ok=True)
    except Exception: pass
    return p

# ======================================================================
# TEMA / RENKLER
# ======================================================================
TEMALAR = {
    "mavi":   {"ad": "Elektrik Mavisi", "renk": "#3B82F6", "hover": "#2563EB"},
    "yesil":  {"ad": "Zümrüt Yeşili",   "renk": "#10B981", "hover": "#059669"},
    "mor":    {"ad": "Siber Mor",       "renk": "#8B5CF6", "hover": "#7C3AED"},
    "turuncu":{"ad": "Alev Turuncusu",  "renk": "#F97316", "hover": "#EA580C"},
    "kirmizi":{"ad": "Yakut Kırmızısı", "renk": "#EF4444", "hover": "#DC2626"},
    "altin":  {"ad": "Altın Sarısı",    "renk": "#F59E0B", "hover": "#D97706"},
    "galaksi":{"ad": "Galaksi Moru",    "renk": "#9D00FF", "hover": "#7B00CC"},
}
CERCEVELER = {
    "mavi":   {"ad": "Elektrik Mavisi", "renk": "#3B82F6"},
    "altin":  {"ad": "Altın Şampiyon",  "renk": "#F59E0B"},
    "zumrut": {"ad": "Zümrüt Siber",    "renk": "#10B981"},
    "kizil":  {"ad": "Kızıl Ateş",      "renk": "#EF4444"},
    "mor":    {"ad": "Mor Galaksi",     "renk": "#8B5CF6"},
}
BANNER_TEMALARI = [
    {"ad": "Neon Cyber", "r1": (0,210,255),  "r2": (157,0,255)},
    {"ad": "Sunset",     "r1": (249,115,22), "r2": (239,68,68)},
    {"ad": "Emerald",    "r1": (16,185,129), "r2": (59,130,246)},
    {"ad": "Cosmic",     "r1": (30,27,75),   "r2": (157,0,255)},
    {"ad": "Firestorm",  "r1": (127,29,29),  "r2": (249,115,22)},
]
DURUMLAR = ["Çevrimiçi", "Oyunda", "Rahatsız Etmeyin", "Görünmez"]
UNVANLAR = ["Yeni Oyuncu", "Gece Kuşu", "Strateji Ustası", "Koleksiyoncu",
            "Speedrunner", "Kaşif", "Arşivci", "Modcu", "Şampiyon", "Galaktik Kaptan"]
CARD_SIZES = {"compact": {"img": (150, 200)}, "standard": {"img": (200, 280)}, "wide": {"img": (260, 340)}}
RENKLER = {
    "arka": "#0B0E14", "yan": "#131822", "kart": "#1A1F2E", "kart_hover": "#232A3D",
    "vurgu": TEMALAR["mavi"]["renk"], "vurgu_hover": TEMALAR["mavi"]["hover"],
    "metin": "#E2E8F0", "soluk": "#94A3B8",
    "yesil": "#22C55E", "kirmizi": "#EF4444", "sari": "#F59E0B", "cizgi": "#1E293B",
    "galaksi": "#9D00FF", "neon_mavi": "#00D2FF",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ======================================================================
# OTOMATİK GÜNCELLEME MOTORU
# ======================================================================
class AutoUpdater:
    @staticmethod
    def is_placeholder(url):
        if not url: return True
        u = url.strip().lower()
        if u in ("https://githubusercontent.com", "https://raw.githubusercontent.com",
                 "https://github.com", "https://github.com/"):
            return True
        if "kullanici" in u or "/your-user/" in u or "/your-username/" in u:
            return True
        return False

    @staticmethod
    def parse_version(v):
        try:
            parts = []
            for x in str(v).replace("v","").replace("V","").split("."):
                digits = "".join(c for c in x if c.isdigit())
                if digits: parts.append(int(digits))
            return parts if parts else [0]
        except Exception:
            return [0]

    @staticmethod
    def check(version_url, current_version, timeout=5):
        if AutoUpdater.is_placeholder(version_url): return None
        try:
            r = requests.get(version_url, timeout=timeout,
                             headers={**HEADERS, "Accept": "application/json"})
            if r.status_code != 200: return None
            try: data = r.json()
            except Exception: return None
            if not isinstance(data, dict): return None
            remote = str(data.get("version", "")).strip()
            if not remote: return None
            if AutoUpdater.parse_version(remote) > AutoUpdater.parse_version(current_version):
                return data
            return None
        except Exception: return None

# ======================================================================
# GITHUB PUBLISHER
# ======================================================================
class GitHubPublisher:
    def __init__(self, token, owner, repo, branch="main"):
        self.token = token.strip()
        self.owner = owner.strip()
        self.repo = repo.strip()
        self.branch = (branch or "main").strip()
        self.api = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "ArdaLauncher-Publisher/8.3",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_sha(self, path):
        try:
            r = requests.get(f"{self.api}/{path}?ref={self.branch}", headers=self.headers, timeout=12)
            if r.status_code == 200: return r.json().get("sha")
            return None
        except Exception: return None

    def _put_file(self, path, content_bytes, message):
        sha = self._get_sha(path)
        payload = {"message": message,
                   "content": base64.b64encode(content_bytes).decode("ascii"),
                   "branch": self.branch}
        if sha: payload["sha"] = sha
        r = requests.put(f"{self.api}/{path}", headers=self.headers, json=payload, timeout=45)
        if r.status_code in (200, 201): return {"ok": True, "data": r.json()}
        try: err = r.json().get("message", r.text[:200])
        except Exception: err = r.text[:200]
        return {"ok": False, "status": r.status_code, "error": err}

    @staticmethod
    def patch_content(content, new_version, owner, repo, branch):
        try:
            content = re.sub(r'^APP_VERSION\s*=\s*"[^"]*"', f'APP_VERSION = "{new_version}"',
                             content, flags=re.MULTILINE)
            ver_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/version.json"
            code_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/launcher.pyw"
            content = re.sub(r'^UPDATE_VERSION_URL\s*=\s*"[^"]*"',
                             f'UPDATE_VERSION_URL = "{ver_url}"', content, flags=re.MULTILINE)
            content = re.sub(r'^UPDATE_CODE_URL\s*=\s*"[^"]*"',
                             f'UPDATE_CODE_URL = "{code_url}"', content, flags=re.MULTILINE)
        except Exception as e: print(f"[PATCH] {e}")
        return content.encode("utf-8")

    def publish(self, script_path, new_version, notes, progress_cb=None):
        if not os.path.exists(script_path):
            return {"ok": False, "error": "launcher.pyw bulunamadı."}
        try:
            with open(script_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            return {"ok": False, "error": f"Dosya okunamadı: {e}"}
        if progress_cb: progress_cb("Dosya içeriği hazırlanıyor...", 10)
        patched = self.patch_content(content, new_version, self.owner, self.repo, self.branch)
        if progress_cb: progress_cb("launcher.pyw yükleniyor...", 30)
        res1 = self._put_file("launcher.pyw", patched,
                             f"ARDA LAUNCHER v{new_version} — kod güncellemesi")
        if not res1.get("ok"):
            return {"ok": False, "step": "launcher.pyw",
                    "error": res1.get("error", "Bilinmeyen hata"),
                    "status": res1.get("status")}
        if progress_cb: progress_cb("launcher.pyw yüklendi ✓", 60)
        ver_data = {
            "version": new_version,
            "notes": notes.strip() or f"ARDA LAUNCHER v{new_version}",
            "url": f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/launcher.pyw",
            "released": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        ver_bytes = json.dumps(ver_data, indent=2, ensure_ascii=False).encode("utf-8")
        if progress_cb: progress_cb("version.json yükleniyor...", 80)
        res2 = self._put_file("version.json", ver_bytes,
                             f"ARDA LAUNCHER v{new_version} — version.json")
        if not res2.get("ok"):
            return {"ok": False, "step": "version.json",
                    "error": res2.get("error", "Bilinmeyen hata"),
                    "status": res2.get("status")}
        if progress_cb: progress_cb("Tüm dosyalar yüklendi ✓", 100)
        return {"ok": True, "version_url": ver_data["url"],
                "code_url": ver_data["url"].replace("version.json","launcher.pyw"),
                "data": ver_data}

# ======================================================================
# OYUN KATALOĞU
# ======================================================================
def _steam_cover_urls(appid):
    return [
        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/library_600x900.jpg",
        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_600x900.jpg",
        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
    ]
def _steam_banner_urls(appid):
    return [
        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
        f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
    ]

OYUN_KATALOGU = {
    "mindustry": {"isim": "Mindustry", "repo": "Anuken/Mindustry", "exe_adi": "Mindustry.exe",
        "tur": "Strateji", "aciklama": "Tower defense ve fabrika otomasyonunu birleştiren açık kaynak oyun.",
        "sistem": "Windows 7+, 2 GB RAM, 200 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(1127400), "banner_urls": _steam_banner_urls(1127400)},
    "wesnoth": {"isim": "Battle for Wesnoth", "repo": "wesnoth/wesnoth", "exe_adi": "wesnoth.exe",
        "tur": "Strateji", "aciklama": "Yüksek fantezi temalı sıra tabanlı strateji. 17 solo kampanya.",
        "sistem": "Windows 7+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(599390), "banner_urls": _steam_banner_urls(599390)},
    "endlesssky": {"isim": "Endless Sky", "repo": "endless-sky/endless-sky", "exe_adi": "EndlessSky.exe",
        "tur": "RPG", "aciklama": "Klasik Escape Velocity tarzı 2D uzay ticareti ve savaş oyunu.",
        "sistem": "Windows 7+, 1 GB RAM, 300 MB alan", "min_ram": 1,
        "kapak_urls": _steam_cover_urls(404410), "banner_urls": _steam_banner_urls(404410)},
    "shatteredpd": {"isim": "Shattered Pixel Dungeon", "repo": "00-Evan/shattered-pixel-dungeon",
        "exe_adi": "ShatteredPD.exe", "tur": "Roguelike",
        "aciklama": "Başlaması kolay, ustalaşması zor roguelike zindan tarayıcısı.",
        "sistem": "Windows 10+, 1 GB RAM, 100 MB alan", "min_ram": 1,
        "kapak_urls": _steam_cover_urls(1769170), "banner_urls": _steam_banner_urls(1769170)},
    "openttd": {"isim": "OpenTTD", "repo": "OpenTTD/OpenTTD", "exe_adi": "openttd.exe",
        "tur": "Simülasyon", "aciklama": "Transport Tycoon Deluxe'un açık kaynak yeniden yapımı.",
        "sistem": "Windows 7+, 1 GB RAM, 100 MB alan", "min_ram": 1,
        "kapak_urls": _steam_cover_urls(1536610), "banner_urls": _steam_banner_urls(1536610)},
    "warzone2100": {"isim": "Warzone 2100", "repo": "Warzone2100/warzone2100", "exe_adi": "warzone2100.exe",
        "tur": "Strateji", "aciklama": "3D bilim kurgu gerçek zamanlı strateji. Birim tasarımı ve kampanya.",
        "sistem": "Windows 7+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(1241950), "banner_urls": _steam_banner_urls(1241950)},
    "cataclysm": {"isim": "Cataclysm: DDA", "repo": "CleverRaven/Cataclysm-DDA",
        "exe_adi": "cataclysm-tiles.exe", "tur": "RPG", "aciklama": "Zombi kıyameti sonrası hayatta kalma RPG.",
        "sistem": "Windows 10+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(2330750), "banner_urls": _steam_banner_urls(2330750)},
    "tome4": {"isim": "Tales of Maj'Eyal", "repo": "tome4/tome", "exe_adi": "t-engine.exe",
        "tur": "Roguelike", "aciklama": "Fantastik roguelike RPG. Derin taktik savaş.",
        "sistem": "Windows 7+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(259680), "banner_urls": _steam_banner_urls(259680)},
    "unciv": {"isim": "Unciv", "repo": "yairm210/Unciv", "exe_adi": "Unciv.exe",
        "tur": "Strateji", "aciklama": "Civilization V'in açık kaynak yeniden yapımı. Sıra tabanlı 4X strateji.",
        "sistem": "Windows 7+, 2 GB RAM, 100 MB alan", "min_ram": 2,
        "kapak_urls": _steam_cover_urls(2247670), "banner_urls": _steam_banner_urls(2247670)},
    "openra": {"isim": "OpenRA", "repo": "OpenRA/OpenRA", "exe_adi": "OpenRA.exe",
        "tur": "Strateji", "aciklama": "Red Alert, Tiberian Dawn ve Dune 2000 modernize eden RTS motoru.",
        "sistem": "Windows 7+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": ["https://www.openra.net/images/social.jpg",
                       "https://raw.githubusercontent.com/OpenRA/OpenRA/master/mods/cnc/chrome/mainmenu.png"],
        "banner_urls": ["https://www.openra.net/images/social.jpg"]},
    "supertuxkart": {"isim": "SuperTuxKart", "repo": "supertuxkart/stk-code", "exe_adi": "supertuxkart.exe",
        "tur": "Yarış", "aciklama": "Tux ve arkadaşlarının 3D karting yarışı.",
        "sistem": "Windows 7+, 2 GB RAM, 500 MB alan", "min_ram": 2,
        "kapak_urls": ["https://www.supertuxkart.net/assets/gallery/STK1.0_2.jpg",
                       "https://www.supertuxkart.net/images/screenshots/STK1.0_2.jpg",
                       "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/SuperTuxKart_Logo.svg/512px-SuperTuxKart_Logo.svg.png"],
        "banner_urls": ["https://www.supertuxkart.net/assets/gallery/STK1.0_2.jpg",
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/SuperTuxKart_Logo.svg/1024px-SuperTuxKart_Logo.svg.png"]},
    "veloren": {"isim": "Veloren", "repo": "veloren/veloren", "exe_adi": "veloren.exe",
        "tur": "RPG", "aciklama": "Cube World ve Minecraft'tan ilham alan açık dünya voxel RPG.",
        "sistem": "Windows 10+, 4 GB RAM, 1 GB alan", "min_ram": 4,
        "kapak_urls": ["https://veloren.net/logo.png",
                       "https://raw.githubusercontent.com/veloren/veloren/master/docs/logo.png",
                       "https://raw.githubusercontent.com/veloren/veloren/main/docs/logo.png"],
        "banner_urls": ["https://veloren.net/processed_images/0d97e31074771fbb00.png",
                        "https://raw.githubusercontent.com/veloren/veloren/master/docs/logo.png"]},
    "zeroad": {"isim": "0 A.D.", "repo": "0ad/0ad", "exe_adi": "pyrogenesis.exe",
        "tur": "Strateji", "aciklama": "Antik savaş temalı, ücretsiz ve açık kaynaklı RTS.",
        "sistem": "Windows 7+, 2 GB RAM, 1 GB alan", "min_ram": 2,
        "kapak_urls": ["https://play0ad.com/wp-content/uploads/2021/07/cropped-0ad_logo_512.png",
                       "https://play0ad.com/wp-content/themes/play0ad/images/logo.png",
                       "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/0_AD_logo.svg/512px-0_AD_logo.svg.png",
                       "https://cdn.akamai.steamstatic.com/steam/apps/37060/library_600x900.jpg"],
        "banner_urls": ["https://play0ad.com/wp-content/uploads/2021/07/0ad_banner.jpg",
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/0_AD_logo.svg/1024px-0_AD_logo.svg.png",
                        "https://cdn.akamai.steamstatic.com/steam/apps/37060/header.jpg"]},
    "ddnet": {"isim": "DDNet (Teeworlds)", "repo": "ddnet/ddnet", "exe_adi": "DDNet.exe",
        "tur": "Aksiyon", "aciklama": "Teeworlds tabanlı çok oyunculu 2D aksiyon.",
        "sistem": "Windows 7+, 1 GB RAM, 100 MB alan", "min_ram": 1,
        "kapak_urls": _steam_cover_urls(380840), "banner_urls": _steam_banner_urls(380840)},
}

def _refresh_eski_cache():
    marker = BASE_DIR / ".cache_refreshed_v82"
    if marker.exists(): return
    try:
        hashes = set()
        for oid in ("unciv","supertuxkart","veloren","zeroad"):
            if oid in OYUN_KATALOGU:
                for url in OYUN_KATALOGU[oid].get("kapak_urls", []): hashes.add(hashlib.md5(url.encode()).hexdigest())
                for url in OYUN_KATALOGU[oid].get("banner_urls", []): hashes.add(hashlib.md5(url.encode()).hexdigest())
        for h in hashes:
            cp = CACHE_COVERS / f"{h}.png"
            if cp.exists():
                try: cp.unlink()
                except Exception: pass
        marker.write_text(str(time.time()), encoding="utf-8")
    except Exception: pass
_refresh_eski_cache()

BASARIMLAR = {
    "first_step": {"ad": "İlk Adım", "ikon": "🎯", "aciklama": "İlk oyununu kur"},
    "marathon":   {"ad": "Maratoncu", "ikon": "⏱️", "aciklama": "Toplam 1 saat oyun oyna"},
    "archivist":  {"ad": "Arşivci", "ikon": "📚", "aciklama": "5 oyun ekle"},
    "safe_player":{"ad": "Güvenli Oyuncu", "ikon": "🛡️", "aciklama": "İlk yedeğini al"},
    "collector":  {"ad": "Koleksiyoncu", "ikon": "💎", "aciklama": "10 oyun ekle"},
    "customizer": {"ad": "Kişiselleştir", "ikon": "🎨", "aciklama": "Profilini düzenle"},
    "downloader": {"ad": "İndirici", "ikon": "⬇️", "aciklama": "3 indirme tamamla"},
    "explorer":   {"ad": "Kaşif", "ikon": "🔍", "aciklama": "Klasör tara"},
    "booster":    {"ad": "Hız Tutkunu", "ikon": "🚀", "aciklama": "Yüksek öncelikle başlat"},
    "theme_master":{"ad": "Tema Ustası", "ikon": "🌈", "aciklama": "Tema değiştir"},
}
XP_ODULLERI = {"oyun_indir": 100, "oyun_baslat": 50, "oynama_10dk": 25, "yedekle": 30, "tarama": 40, "tema_degistir": 15}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

def fmt_sure(s):
    s = int(s); h, d, sn = s // 3600, (s % 3600) // 60, s % 60
    if h > 0: return f"{h} sa {d} dk"
    if d > 0: return f"{d} dk {sn} sn"
    return f"{sn} sn"

def sistem_cpu():
    if PSUTIL_OK:
        try: return psutil.cpu_percent(interval=None)
        except Exception: return 0.0
    return 0.0

def sistem_ram():
    if PSUTIL_OK:
        try: return psutil.virtual_memory().percent
        except Exception: pass
    if sys.platform == "win32":
        try:
            class M(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            s = M(); s.dwLength = ctypes.sizeof(M)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
            return float(s.dwMemoryLoad)
        except Exception: pass
    return 0.0

def toplam_ram_gb():
    if PSUTIL_OK:
        try: return psutil.virtual_memory().total / (1024**3)
        except Exception: pass
    return 8.0

def disk_usage_gb(path):
    try:
        anchor = os.path.splitdrive(str(Path(path).resolve()))[0] + "\\"
        u = shutil.disk_usage(anchor)
        return u.total / (1024**3), u.used / (1024**3), u.free / (1024**3)
    except Exception: return 0.0, 0.0, 0.0

def folder_size_bayt(path):
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try: total += os.path.getsize(os.path.join(root, f))
                except Exception: pass
    except Exception: pass
    return total

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

# ======================================================================
# GÖRSEL ÜRETİCİ
# ======================================================================
PALETLER = {
    "Strateji":   [(20, 25, 60),  (60, 30, 90),   (120, 60, 40)],
    "RPG":        [(30, 10, 50),  (100, 40, 80),  (220, 100, 60)],
    "Roguelike":  [(10, 10, 20),  (60, 20, 60),   (200, 50, 80)],
    "Yarış":      [(10, 30, 60),  (60, 100, 150), (240, 180, 60)],
    "Simülasyon": [(20, 40, 30),  (60, 120, 100), (180, 200, 100)],
    "Aksiyon":    [(40, 10, 10),  (150, 40, 40),  (240, 120, 40)],
    "Araçlar":    [(20, 20, 40),  (60, 60, 100),  (150, 100, 200)],
}

def _draw_star(d, cx, cy, size, fill):
    p = [(cx, cy - size), (cx + size*0.18, cy - size*0.18), (cx + size, cy),
         (cx + size*0.18, cy + size*0.18), (cx, cy + size), (cx - size*0.18, cy + size*0.18),
         (cx - size, cy), (cx - size*0.18, cy - size*0.18)]
    d.polygon(p, fill=fill)

def _draw_genre_icon(draw, tur, cx, cy, size):
    white = (240, 240, 250); dark = (20, 20, 30)
    if tur == "Strateji":
        bw, bh = size, size * 0.7; x0, y0 = cx - bw/2, cy - bh/2
        draw.rectangle([x0, y0, x0 + bw, y0 + bh], fill=white)
        for i in range(4):
            bx = x0 + i * (bw / 4)
            draw.rectangle([bx, y0 - size*0.12, bx + bw/8, y0], fill=white)
        draw.rectangle([cx - size*0.08, y0 + bh*0.5, cx + size*0.08, y0 + bh], fill=dark)
    elif tur == "RPG":
        draw.polygon([(cx, cy - size*0.5), (cx - size*0.08, cy + size*0.25),
                      (cx + size*0.08, cy + size*0.25)], fill=white)
        draw.rectangle([cx - size*0.15, cy + size*0.25, cx + size*0.15, cy + size*0.32], fill=(200, 150, 80))
        draw.rectangle([cx - size*0.2, cy + size*0.22, cx + size*0.2, cy + size*0.26], fill=white)
        draw.rectangle([cx - size*0.03, cy + size*0.32, cx + size*0.03, cy + size*0.5], fill=(120, 80, 40))
    elif tur == "Roguelike":
        draw.ellipse([cx - size*0.35, cy - size*0.35, cx + size*0.35, cy + size*0.25], fill=white)
        draw.rectangle([cx - size*0.15, cy + size*0.15, cx + size*0.15, cy + size*0.32], fill=white)
        draw.ellipse([cx - size*0.18, cy - size*0.08, cx - size*0.08, cy + size*0.05], fill=dark)
        draw.ellipse([cx + size*0.08, cy - size*0.08, cx + size*0.18, cy + size*0.05], fill=dark)
    elif tur == "Yarış":
        draw.rounded_rectangle([cx - size*0.45, cy - size*0.08, cx + size*0.45, cy + size*0.15], radius=size*0.06, fill=white)
        draw.rounded_rectangle([cx - size*0.28, cy - size*0.22, cx + size*0.28, cy - size*0.05], radius=size*0.08, fill=white)
        draw.ellipse([cx - size*0.45, cy + size*0.10, cx - size*0.28, cy + size*0.28], fill=dark)
        draw.ellipse([cx + size*0.28, cy + size*0.10, cx + size*0.45, cy + size*0.28], fill=dark)
    elif tur == "Simülasyon":
        draw.ellipse([cx - size*0.3, cy - size*0.3, cx + size*0.3, cy + size*0.3], fill=white)
        for i in range(8):
            ang = math.radians(i * 45)
            tx = cx + math.cos(ang) * size*0.45; ty = cy + math.sin(ang) * size*0.45
            draw.ellipse([tx - size*0.07, ty - size*0.07, tx + size*0.07, ty + size*0.07], fill=white)
        draw.ellipse([cx - size*0.12, cy - size*0.12, cx + size*0.12, cy + size*0.12], fill=dark)
    elif tur == "Aksiyon":
        draw.ellipse([cx - size*0.3, cy - size*0.3, cx + size*0.3, cy + size*0.3], outline=white, width=int(size*0.06))
        draw.line([cx - size*0.5, cy, cx + size*0.5, cy], fill=white, width=int(size*0.06))
        draw.line([cx, cy - size*0.5, cx, cy + size*0.5], fill=white, width=int(size*0.06))
        draw.ellipse([cx - size*0.06, cy - size*0.06, cx + size*0.06, cy + size*0.06], fill=white)
    else:
        _draw_star(draw, cx, cy, size*0.45, white)

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
    cx, cy = w // 2, h // 2
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    for i in range(90, 0, -3):
        a = int(120 * (1 - i / 90))
        gd.ellipse((cx - i, cy - i, cx + i, cy + i), fill=(180, 200, 255, a))
    for ang_deg in (30, 150, 210, 330):
        ang = math.radians(ang_deg); length = max(w, h) * 1.2
        for span in (2, 4, 6):
            x1 = cx + math.cos(ang) * 30; y1 = cy + math.sin(ang) * 30
            x2 = cx + math.cos(ang) * length; y2 = cy + math.sin(ang) * length
            gd.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 20), width=span * 4)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=18))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)
    icon_size = min(w, h) * 0.32
    _draw_genre_icon(d, tur, cx, int(cy - h * 0.08), icon_size)
    try:
        font_size = int(h * 0.085); font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        try: font = ImageFont.truetype("arial.ttf", font_size)
        except Exception: font = ImageFont.load_default()
    words = isim.split(); lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        bb = d.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] > w - 24:
            if cur: lines.append(cur)
            cur = word
        else: cur = test
    if cur: lines.append(cur)
    total_h = len(lines) * font_size; start_y = h - total_h - int(h * 0.06)
    for i, line in enumerate(lines):
        bb = d.textbbox((0, 0), line, font=font); tw = bb[2] - bb[0]
        tx = (w - tw) / 2; ty = start_y + i * font_size
        d.text((tx + 2, ty + 2), line, font=font, fill=(0, 0, 0))
        d.text((tx, ty), line, font=font, fill=(255, 255, 255))
    try: fk = ImageFont.truetype("arial.ttf", int(h * 0.045))
    except Exception: fk = ImageFont.load_default()
    if tur:
        bb2 = d.textbbox((0, 0), tur.upper(), font=fk); tw2 = bb2[2] - bb2[0]
        d.text(((w - tw2) / 2 + 1, h - int(h * 0.07) + 1), tur.upper(), font=fk, fill=(0, 0, 0))
        d.text(((w - tw2) / 2, h - int(h * 0.07)), tur.upper(), font=fk, fill=(180, 200, 255))
    return img

def akilli_kirp(img, boyut):
    try: resample = Image.Resampling.LANCZOS
    except AttributeError: resample = Image.LANCZOS
    try: return ImageOps.fit(img, boyut, method=resample)
    except Exception:
        hedef_o = boyut[0] / boyut[1]; w, h = img.size; o = w / h
        if o > hedef_o:
            yw = int(h * hedef_o); s = (w - yw) // 2; img = img.crop((s, 0, s + yw, h))
        else:
            yh = int(w / hedef_o); u = (h - yh) // 2; img = img.crop((0, u, w, u + yh))
        return img.resize(boyut, resample)

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
                    else:
                        try: cache_path.unlink()
                        except Exception: pass
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

def icon_olustur():
    if ICON_DOSYASI.exists():
        try:
            Image.open(ICON_DOSYASI).verify(); return
        except Exception:
            try: ICON_DOSYASI.unlink()
            except Exception: pass
    sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
    try:
        logo_png = BASE_DIR / "logo.png"
        if logo_png.exists():
            im = Image.open(logo_png).convert("RGBA").resize((256, 256), Image.LANCZOS)
            im.save(ICON_DOSYASI, format="ICO", sizes=sizes); return
    except Exception: pass
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
            r = int(0 * (1-t) + 157 * t); g = int(210 * (1-t) + 0 * t); b = int(255 * (1-t) + 255 * t)
            gd.line([(x, 0), (x, S)], fill=(r, g, b))
        fm = Image.new("L", (S, S), 0)
        ImageDraw.Draw(fm).rounded_rectangle((10, 10, S-11, S-11), radius=44, outline=255, width=6)
        frame = Image.new("RGBA", (S, S), (0, 0, 0, 0)); frame.paste(grad, (0, 0), fm)
        img = Image.alpha_composite(img, frame); d = ImageDraw.Draw(img)
        cx, cy = S // 2, S // 2
        try:
            d.arc([cx-95, cy-42, cx+95, cy+42], start=20, end=200, fill=(0, 210, 255, 200), width=3)
            d.arc([cx-95, cy-42, cx+95, cy+42], start=200, end=380, fill=(157, 0, 255, 200), width=3)
        except Exception: pass
        glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); gld = ImageDraw.Draw(glow)
        for i in range(55, 0, -2):
            a = int(45 * (1 - i / 55)); gld.ellipse((cx-i, cy-i, cx+i, cy+i), fill=(140, 100, 255, a))
        img = Image.alpha_composite(img, glow); d = ImageDraw.Draw(img)
        star_sz = 72
        _draw_star(d, cx, cy, star_sz, (255, 255, 255, 255))
        _draw_star(d, cx, cy, star_sz * 0.65, (200, 230, 255, 255))
        _draw_star(d, cx, cy, star_sz * 0.35, (0, 210, 255, 255))
        d.ellipse((cx-8, cy-8, cx+8, cy+8), fill=(255, 255, 255, 255))
        d.ellipse((cx-4, cy-4, cx+4, cy+4), fill=(157, 0, 255, 255))
        com_x, com_y = S - 42, 42
        for i in range(35, 0, -1):
            a = int(210 * (1 - i / 35)); w = max(1, i // 9)
            d.line([(com_x + i*1.7, com_y - i*1.7), (com_x, com_y)], fill=(180, 200, 255, a), width=w)
        d.ellipse((com_x-5, com_y-5, com_x+5, com_y+5), fill=(255, 255, 255, 255))
        d.ellipse((com_x-3, com_y-3, com_x+3, com_y+3), fill=(0, 210, 255, 255))
        img.save(ICON_DOSYASI, format="ICO", sizes=sizes)
    except Exception as e: print(f"[ICON] {e}")
icon_olustur()

# ======================================================================
# GITHUB İNDİRME MOTORU
# ======================================================================
class GitHubMotoru:
    _cache = {}
    @classmethod
    def _select_windows(cls, assets):
        if not assets: return None
        tests = [lambda n: "win64" in n and n.endswith(".zip"),
                 lambda n: "windows" in n and n.endswith(".zip"),
                 lambda n: "win" in n and n.endswith(".zip"),
                 lambda n: "x64" in n and n.endswith(".zip"),
                 lambda n: n.endswith(".zip") and "source" not in n,
                 lambda n: "win" in n and n.endswith(".7z"),
                 lambda n: "win" in n and n.endswith(".exe"),
                 lambda n: n.endswith(".zip"), lambda n: n.endswith(".7z")]
        for t in tests:
            for x in assets:
                if t(x["name"].lower()): return x
        return None
    @classmethod
    def _api_asset(cls, repo):
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/releases/latest",
                             timeout=15, headers={**HEADERS, "Accept": "application/vnd.github+json"})
            if r.status_code != 200: return None
            data = r.json()
            assets = [{"name": a["name"], "url": a["browser_download_url"],
                       "size": a.get("size", 0)} for a in data.get("assets", [])]
            return cls._select_windows(assets)
        except Exception: return None
    @classmethod
    def _html_asset(cls, repo):
        try:
            r = requests.get(f"https://github.com/{repo}/releases/latest",
                             timeout=15, headers=HEADERS, allow_redirects=True)
            if r.status_code != 200: return None
            tag = None
            if "/tag/" in r.url: tag = r.url.split("/tag/")[-1].split("?")[0]
            urls = []
            if tag: urls.append(f"https://github.com/{repo}/releases/expanded_assets/{tag}")
            urls.append(f"https://github.com/{repo}/releases/expanded_assets/latest")
            for ex_url in urls:
                try:
                    r2 = requests.get(ex_url, timeout=15, headers=HEADERS)
                    if r2.status_code != 200: continue
                    matches = re.findall(r'href="(/[^"]+/releases/download/[^"]+)"', r2.text)
                    assets, seen = [], set()
                    for m in matches:
                        if m in seen: continue
                        seen.add(m)
                        assets.append({"name": m.split("/")[-1], "url": f"https://github.com{m}", "size": 0})
                    if assets: return cls._select_windows(assets)
                except Exception: continue
            return None
        except Exception: return None
    @classmethod
    def windows_asset(cls, repo):
        if not repo: return None
        if repo in cls._cache: return cls._cache[repo]
        a = cls._api_asset(repo)
        if a: cls._cache[repo] = a; return a
        a = cls._html_asset(repo)
        if a: cls._cache[repo] = a; return a
        return None

def arsiv_cikar(archive_path, extract_to):
    extract_to.mkdir(parents=True, exist_ok=True)
    ext = archive_path.suffix.lower()
    if ext == ".zip" or zipfile.is_zipfile(archive_path):
        try:
            with zipfile.ZipFile(archive_path, "r") as zf: zf.extractall(extract_to)
            return True
        except Exception: pass
    if ext == ".7z":
        if PY7ZR_OK:
            try:
                with py7zr.SevenZipFile(archive_path, mode="r") as z: z.extractall(extract_to)
                return True
            except Exception: pass
        try:
            flags = 0x08000000 if sys.platform == "win32" else 0
            r = subprocess.run(["tar", "-xf", str(archive_path), "-C", str(extract_to)],
                               capture_output=True, timeout=300, creationflags=flags)
            if r.returncode == 0: return True
        except Exception: pass
        try:
            flags = 0x08000000 if sys.platform == "win32" else 0
            r = subprocess.run(["7z", "x", str(archive_path), f"-o{extract_to}", "-y"],
                               capture_output=True, timeout=300, creationflags=flags)
            if r.returncode == 0: return True
        except Exception: pass
    try:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, "r") as zf: zf.extractall(extract_to)
            return True
    except Exception: pass
    return False

# ======================================================================
# İNDİRME YÖNETİCİSİ
# ======================================================================
class IndirmeYoneticisi:
    def __init__(self, app):
        self.app = app; self.aktif = {}; self.lock = threading.Lock()
    def baslat(self, oid, oyun):
        with self.lock:
            if oid in self.aktif: return
            self.aktif[oid] = {"durum": "hazirlaniyor", "iptal": False, "duraklat": False,
                               "indirilen": 0, "toplam": 0, "hiz": 0, "eta": 0, "asset": None}
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
            self.app.after(0, lambda: self.app.detay_durum_metni(oid, "Sürüm kontrol ediliyor..."))
            asset = GitHubMotoru.windows_asset(oyun["repo"])
            if not asset: raise RuntimeError(f"'{oyun['repo']}' için Windows paketi bulunamadı.")
            with self.lock:
                if oid in self.aktif:
                    self.aktif[oid]["asset"] = asset; self.aktif[oid]["durum"] = "indiriliyor"
            self.app.after(0, lambda n=asset['name']: self.app.detay_durum_metni(oid, f"İndiriliyor: {n}"))
            mevcut = part.stat().st_size if part.exists() else 0
            h = dict(HEADERS)
            if mevcut > 0: h["Range"] = f"bytes={mevcut}-"
            r = requests.get(asset["url"], stream=True, timeout=60, headers=h, allow_redirects=True)
            r.raise_for_status()
            toplam = int(r.headers.get("content-length", 0)) + mevcut or asset.get("size", 0)
            with open(part, "ab" if mevcut else "wb") as f:
                indirilen, son_t, son_i = mevcut, time.time(), mevcut
                bas = time.time() - (mevcut / max(speed_limit, 0.01) / 1024 / 1024 if speed_limit > 0 and mevcut > 0 else 0)
                for chunk in r.iter_content(chunk_size=16384):
                    if not chunk: continue
                    with self.lock:
                        if oid not in self.aktif or self.aktif[oid]["iptal"]: return
                        while self.aktif[oid]["duraklat"] and not self.aktif[oid]["iptal"]: time.sleep(0.15)
                        if self.aktif[oid]["iptal"]: return
                    f.write(chunk); indirilen += len(chunk); simdi = time.time()
                    if speed_limit > 0:
                        beklenen = indirilen / (speed_limit * 1024 * 1024); gecen = simdi - bas
                        if gecen < beklenen: time.sleep(min(beklenen - gecen, 0.5))
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
            self.app.after(0, lambda: self.app.detay_ilerleme(oid, 1.0, 0, toplam, toplam, 0))
            self.app.after(0, lambda: self.app.detay_durum_metni(oid, "Çıkartılıyor..."))
            if auto_extract:
                ok = arsiv_cikar(part, hedef)
                if ok:
                    try: part.unlink()
                    except Exception: pass
                elif not zipfile.is_zipfile(part) and part.suffix.lower() not in (".7z", ".zip"):
                    hedef_exe = hedef / oyun["exe_adi"]
                    try:
                        if hedef_exe.exists(): hedef_exe.unlink()
                        shutil.move(str(part), str(hedef_exe))
                    except Exception: pass
            else:
                if not zipfile.is_zipfile(part) and part.suffix.lower() not in (".7z",):
                    hedef_exe = hedef / oyun["exe_adi"]
                    try:
                        if hedef_exe.exists(): hedef_exe.unlink()
                        shutil.move(str(part), str(hedef_exe))
                    except Exception: pass
            exe_yolu = None; aranan = oyun["exe_adi"]
            for p in [hedef / aranan] + list(hedef.rglob(aranan)):
                if p.exists(): exe_yolu = p; break
            if not exe_yolu:
                exes = list(hedef.rglob("*.exe"))
                if exes:
                    exes.sort(key=lambda x: x.stat().st_size, reverse=True); exe_yolu = exes[0]
            if not exe_yolu: raise FileNotFoundError(".exe bulunamadı.")
            with self.lock:
                if oid in self.aktif: del self.aktif[oid]
            self.app.after(0, lambda ep=exe_yolu, an=asset["name"]: self.app.indirme_basarili(oid, ep, an))
        except Exception as e:
            with self.lock:
                if oid in self.aktif: self.aktif[oid]["durum"] = "hata"
            err = str(e)
            self.app.after(0, lambda err=err: self.app.indirme_hatali(oid, err))

# ======================================================================
# OYUN KARTI
# ======================================================================
class OyunKarti(ctk.CTkFrame):
    def __init__(self, master, oid, oyun, app, favori=False):
        super().__init__(master, corner_radius=12, fg_color=RENKLER["kart"], cursor="hand2")
        self.oid, self.oyun, self.app = oid, oyun, app
        self.grid_columnconfigure(0, weight=1)
        size_key = app.veri.get("settings", {}).get("card_size", "standard")
        dims = CARD_SIZES.get(size_key, CARD_SIZES["standard"]); w, h = dims["img"]
        self.kapak = ctk.CTkLabel(self, text="", width=w, height=h)
        self.kapak.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.kapak.bind("<Button-1>", lambda e: self.app.oyun_detay_goster(oid))
        self.app.gorsel_yukle_guvenli(self.kapak, oid, "kapak", oyun.get("kapak_urls", []), (w, h),
                                       oyun["isim"], oyun["tur"], overlay=False)
        ctk.CTkLabel(self, text=oyun["isim"], font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=RENKLER["metin"], wraplength=w+10).grid(row=1, column=0, padx=8, sticky="w")
        sure = app.veri["oyunlar"].get(oid, {}).get("oynama_suresi", 0)
        alt = oyun["tur"] + (f" • {fmt_sure(sure)}" if sure > 0 else "")
        ctk.CTkLabel(self, text=alt, font=ctk.CTkFont(size=10),
                     text_color=RENKLER["soluk"]).grid(row=2, column=0, padx=8, pady=(0, 10), sticky="w")
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
        self.title(f"ARDA LAUNCHER v{APP_VERSION} ZERO-BUG")
        self.geometry("1500x950"); self.minsize(1280, 820)
        self.configure(fg_color=RENKLER["arka"])
        self.image_refs = {}
        self._updating = False
        self._dev_visible = False
        # --- SCROLL + HERO FIX DEĞİŞKENLERİ ---
        self._scroll_positions = {}
        self._hero_paused = False
        self.hero_frame = None
        self.hero_banner = None
        self.hero_title_lbl = None
        self.hero_desc_lbl = None
        self.hero_incele_btn = None
        self.hero_dots = None
        self.hero_ids = []
        # ---
        self._pencere_ikonu_uygula()

        self.veri = load_json(DATA_DOSYASI, {})
        self.veri.setdefault("profil", {
            "ad": "Arda", "unvan": "Yeni Oyuncu", "biyografi": "ARDA Launcher kullanıcısı.",
            "durum": "Çevrimiçi", "avatar_yolu": "", "banner_yolu": "", "banner_tema": 0,
            "cerceve": "mavi", "xp": 0, "seviye": 1, "rozetler": [], "vitrin_oyun": ""})
        self.veri.setdefault("oyunlar", {})
        self.veri.setdefault("eklenen_oyunlar", {})
        self.veri.setdefault("tema", "galaksi")
        self.veri.setdefault("son_aktiviteler", [])
        self.veri.setdefault("indirme_sayaci", 0)
        self.veri.setdefault("desktop_shortcut_created", False)
        self.veri.setdefault("gunluk_oynama", {})
        self.veri.setdefault("koleksiyonlar", {})
        self.veri.setdefault("dev", {"owner": "", "repo": "", "token": "", "branch": "main",
                                     "next_version": "", "notes": ""})
        self.veri.setdefault("settings", {
            "download_speed_limit": 0, "auto_extract": True,
            "startup_enabled": False, "game_booster": True,
            "minimize_on_play": False, "monitor_refresh": 2000,
            "card_size": "standard"})
        self.veri.setdefault("indirme_dizini", str(_varsayilan_oyun_dizini()))
        self.veri.setdefault("yedek_dizini", str(_varsayilan_yedek_dizini()))

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
        self.aktif_sayfa = "kesfet"
        self.arama = ""
        self.indirme_yon = IndirmeYoneticisi(self)
        self._hero_index = 0
        self._monitor_job = None
        self._tema_uygula(self.veri["tema"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=0)
        self._build_sidebar(); self._build_main()
        self.sayfa_degistir("kesfet")
        self._sistem_monitor()
        self._auto_slider()
        save_json(DATA_DOSYASI, self.veri)
        self.after(1500, self._ilk_kisayol_olustur)
        self.after(3000, lambda: threading.Thread(target=self._auto_update_check, daemon=True).start())

    # ============ OTOMATİK GÜNCELLEME ============
    def _auto_update_check(self):
        try:
            res = AutoUpdater.check(UPDATE_VERSION_URL, APP_VERSION, timeout=5)
            if res: self.after(0, lambda r=res: self._show_update_dialog(r, auto=True))
        except Exception: pass

    def _show_update_dialog(self, info, auto=False):
        try:
            remote_v = str(info.get("version", "?"))
            notes = str(info.get("notes", "Yama notları yok."))
            url = str(info.get("url", "") or info.get("download_url", ""))
            win = ctk.CTkToplevel(self); win.title(f"Yeni Güncelleme: v{remote_v}")
            win.geometry("540x480"); win.configure(fg_color=RENKLER["arka"])
            win.transient(self); win.grab_set()
            ctk.CTkLabel(win, text=f"🎉 Yeni Güncelleme Mevcut! (v{remote_v})",
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=RENKLER["metin"]).pack(pady=(20, 5), padx=20)
            ctk.CTkLabel(win, text=f"Mevcut: v{APP_VERSION} → Yeni: v{remote_v}",
                         font=ctk.CTkFont(size=12), text_color=RENKLER["soluk"]).pack()
            ctk.CTkLabel(win, text="📋 Yama Notları:",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=20, pady=(15, 5))
            tb = ctk.CTkTextbox(win, height=180, fg_color=RENKLER["kart"],
                                 text_color=RENKLER["metin"], font=ctk.CTkFont(size=12))
            tb.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            tb.insert("1.0", notes); tb.configure(state="disabled")
            self._upd_progress = ctk.CTkProgressBar(win, height=10, progress_color=RENKLER["vurgu"])
            self._upd_progress.pack(fill="x", padx=20, pady=(0, 5)); self._upd_progress.set(0)
            bf = ctk.CTkFrame(win, fg_color="transparent"); bf.pack(pady=(0, 20))
            def do_update():
                win.destroy()
                threading.Thread(target=self._download_and_apply_update, args=(url, remote_v), daemon=True).start()
            ctk.CTkButton(bf, text="⬇️ Güncelle", width=140, height=40,
                          fg_color=RENKLER["yesil"], hover_color="#16A34A",
                          command=do_update).pack(side="left", padx=5)
            ctk.CTkButton(bf, text="Şimdi Değil", width=120, height=40,
                          fg_color=RENKLER["kart"], hover_color=RENKLER["kart_hover"],
                          command=win.destroy).pack(side="left", padx=5)
        except Exception as e: print(f"[UPDATE DIALOG] {e}")

    def _download_and_apply_update(self, url, new_version):
        if not url or AutoUpdater.is_placeholder(url):
            self.after(0, lambda: messagebox.showerror("Hata", "Geçerli indirme URL'si yok.")); return
        try:
            r = requests.get(url, timeout=60, headers=HEADERS, allow_redirects=True)
            if r.status_code != 200 or len(r.content) < 1000:
                raise RuntimeError(f"İndirme başarısız (HTTP {r.status_code}).")
            script = _get_script_path()
            if not script: raise RuntimeError("launcher.pyw yolu tespit edilemedi.")
            tmp = script + ".new"
            with open(tmp, "wb") as f: f.write(r.content)
            try: os.replace(tmp, script)
            except Exception:
                with open(script, "wb") as f: f.write(r.content)
                try: os.remove(tmp)
                except Exception: pass
            self.after(400, lambda: self._restart_app())
        except Exception as e:
            err = str(e)
            self.after(0, lambda: messagebox.showerror("Güncelleme Hatası", err))

    def _restart_app(self):
        try:
            try: self.destroy()
            except Exception: pass
            script = _get_script_path() or sys.argv[0]
            os.execl(sys.executable, sys.executable, script, *sys.argv[1:])
        except Exception as e:
            try:
                subprocess.Popen([sys.executable, _get_script_path() or sys.argv[0]])
                sys.exit(0)
            except Exception:
                messagebox.showerror("Hata", f"Yeniden başlatma başarısız: {e}")

    def _manuel_guncelleme_denetle(self):
        def work():
            try:
                res = AutoUpdater.check(UPDATE_VERSION_URL, APP_VERSION, timeout=5)
                if res: self.after(0, lambda r=res: self._show_update_dialog(r, auto=False))
                else:
                    self.after(0, lambda: messagebox.showinfo("Güncelleme Kontrolü",
                        f"✅ En son sürümü kullanıyorsunuz: v{APP_VERSION}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Hata", f"Kontrol başarısız: {e}"))
        threading.Thread(target=work, daemon=True).start()

    def gorsel_yukle_guvenli(self, label, oid, tur_adi, urls, boyut, isim, tur, overlay=False):
        key = f"{oid}_{tur_adi}_{boyut[0]}x{boyut[1]}"
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
                try:
                    img = Image.open(ICON_DOSYASI).convert("RGBA")
                    self._icon_ref = ctk.CTkImage(light_image=img, dark_image=img, size=(64,64))
                    self.iconphoto(True, self._icon_ref._light_image)
                except Exception: pass
        except Exception: pass

    def _tema_uygula(self, anahtar):
        t = TEMALAR.get(anahtar, TEMALAR["mavi"])
        RENKLER["vurgu"] = t["renk"]; RENKLER["vurgu_hover"] = t["hover"]

    def tema_degistir(self, anahtar):
        self.veri["tema"] = anahtar
        self._tema_uygula(anahtar)
        self._xp_ver(XP_ODULLERI["tema_degistir"], "tema_degistir")
        self._rozet_ver("theme_master")
        save_json(DATA_DOSYASI, self.veri)
        for w in self.winfo_children(): w.destroy()
        self._build_sidebar(); self._build_main()
        self.sayfa_degistir(self.aktif_sayfa)

    def _xp_ver(self, miktar, kaynak=""):
        p = self.veri["profil"]
        p["xp"] = p.get("xp", 0) + miktar
        yeni = 1 + p["xp"] // 500
        if yeni > p.get("seviye", 1):
            p["seviye"] = yeni
            self.durum(f"🎉 Seviye {yeni}!")
        if kaynak: self._aktivite_ekle(f"+{miktar} XP ({kaynak})")
        save_json(DATA_DOSYASI, self.veri); self._profil_guncelle()

    def _rozet_ver(self, anahtar):
        if anahtar not in self.veri["profil"]["rozetler"]:
            self.veri["profil"]["rozetler"].append(anahtar)
            save_json(DATA_DOSYASI, self.veri)

    def _rozet_kontrol(self):
        p = self.veri["profil"]
        kurulu = sum(1 for oid, o in self.oyunlar.items() if self._kurulu_mu(oid, o))
        toplam_sn = sum(v.get("oynama_suresi", 0) for v in self.veri["oyunlar"].values())
        if kurulu >= 1: self._rozet_ver("first_step")
        if toplam_sn >= 3600: self._rozet_ver("marathon")
        if kurulu >= 5: self._rozet_ver("archivist")
        if kurulu >= 10: self._rozet_ver("collector")
        if self.veri.get("indirme_sayaci", 0) >= 3: self._rozet_ver("downloader")
        if p.get("avatar_yolu") or p.get("banner_yolu"): self._rozet_ver("customizer")

    def _aktivite_ekle(self, metin):
        self.veri["son_aktiviteler"].insert(0, {"metin": metin, "zaman": time.time()})
        self.veri["son_aktiviteler"] = self.veri["son_aktiviteler"][:30]
        save_json(DATA_DOSYASI, self.veri)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=RENKLER["yan"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        lf = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        lf.grid(row=0, column=0, padx=15, pady=(20, 10), sticky="ew")
        try:
            if ICON_DOSYASI.exists():
                li = Image.open(ICON_DOSYASI).convert("RGBA").resize((40, 40), Image.LANCZOS)
                self._logo_ref = ctk.CTkImage(light_image=li, dark_image=li, size=(40,40))
                ctk.CTkLabel(lf, text="", image=self._logo_ref).pack(side="left", padx=(5, 10))
        except Exception: pass
        ctk.CTkLabel(lf, text="ARDA\nLAUNCHER", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=RENKLER["vurgu"], justify="left").pack(side="left")
        self.profil_mini = ctk.CTkFrame(self.sidebar, fg_color=RENKLER["kart"],
                                         corner_radius=12, cursor="hand2")
        self.profil_mini.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.profil_mini.bind("<Button-1>", lambda e: self.sayfa_degistir("profil"))
        self.mini_avatar = ctk.CTkLabel(self.profil_mini, text="", width=56, height=56)
        self.mini_avatar.pack(pady=(10, 4))
        self.mini_avatar.bind("<Button-1>", lambda e: self.sayfa_degistir("profil"))
        self._mini_avatar_yukle()
        self.mini_ad = ctk.CTkLabel(self.profil_mini, text="", font=ctk.CTkFont(size=14, weight="bold"),
                                     text_color=RENKLER["metin"])
        self.mini_ad.pack()
        self.mini_unvan = ctk.CTkLabel(self.profil_mini, text="", font=ctk.CTkFont(size=10),
                                        text_color=RENKLER["soluk"])
        self.mini_unvan.pack(pady=(0, 4))
        self.mini_xp_bar = ctk.CTkProgressBar(self.profil_mini, height=6, progress_color=RENKLER["vurgu"])
        self.mini_xp_bar.pack(fill="x", padx=12, pady=(2, 2))
        self.mini_seviye = ctk.CTkLabel(self.profil_mini, text="", font=ctk.CTkFont(size=9),
                                         text_color=RENKLER["soluk"])
        self.mini_seviye.pack(pady=(0, 10))
        self.nav_btn = {}
        nav = [("kesfet","🔍  Keşfet"), ("kutuphanem","📚  Kütüphanem"),
               ("indirmeler","📥  İndirmeler"), ("profil","👤  Profilim"),
               ("ayarlar","⚙️  Ayarlar")]
        row = 2
        for key, text in nav:
            if key == "indirmeler":
                holder = ctk.CTkFrame(self.sidebar, fg_color="transparent")
                holder.grid(row=row, column=0, padx=10, pady=3, sticky="ew")
                holder.grid_columnconfigure(0, weight=1)
                b = ctk.CTkButton(holder, text=text, anchor="w", height=42, corner_radius=8,
                                   fg_color="transparent", hover_color=RENKLER["kart_hover"],
                                   text_color=RENKLER["metin"], font=ctk.CTkFont(size=13),
                                   command=lambda k=key: self.sayfa_degistir(k))
                b.grid(row=0, column=0, sticky="ew")
                self.indirme_rozet = ctk.CTkLabel(holder, text="", width=24, height=24,
                                                   corner_radius=12, fg_color=RENKLER["kirmizi"],
                                                   text_color="white", font=ctk.CTkFont(size=11, weight="bold"))
                self.indirme_rozet.grid(row=0, column=1, padx=(5, 5))
                self.indirme_rozet.grid_remove()
                self.nav_btn[key] = b
            else:
                b = ctk.CTkButton(self.sidebar, text=text, anchor="w", height=42, corner_radius=8,
                                   fg_color="transparent", hover_color=RENKLER["kart_hover"],
                                   text_color=RENKLER["metin"], font=ctk.CTkFont(size=13),
                                   command=lambda k=key: self.sayfa_degistir(k))
                b.grid(row=row, column=0, padx=10, pady=3, sticky="ew")
                self.nav_btn[key] = b
            row += 1
        self.sidebar.grid_rowconfigure(row, weight=1); row += 1
        mf = ctk.CTkFrame(self.sidebar, fg_color=RENKLER["kart"], corner_radius=10)
        mf.grid(row=row, column=0, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(mf, text="SİSTEM", font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", padx=12, pady=(8, 4))
        self.cpu_lbl = ctk.CTkLabel(mf, text="CPU  --%", font=ctk.CTkFont(size=10),
                                     text_color=RENKLER["metin"])
        self.cpu_lbl.pack(anchor="w", padx=12)
        self.cpu_bar = ctk.CTkProgressBar(mf, height=5, progress_color=RENKLER["vurgu"])
        self.cpu_bar.pack(fill="x", padx=12, pady=(2, 5)); self.cpu_bar.set(0)
        self.ram_lbl = ctk.CTkLabel(mf, text="RAM  --%", font=ctk.CTkFont(size=10),
                                     text_color=RENKLER["metin"])
        self.ram_lbl.pack(anchor="w", padx=12)
        self.ram_bar = ctk.CTkProgressBar(mf, height=5, progress_color=RENKLER["sari"])
        self.ram_bar.pack(fill="x", padx=12, pady=(2, 10)); self.ram_bar.set(0)
        row += 1
        ctk.CTkLabel(self.sidebar, text=f"v{APP_VERSION} ZERO-BUG", font=ctk.CTkFont(size=9),
                     text_color=RENKLER["soluk"]).grid(row=row, column=0, padx=20, pady=(0, 12), sticky="w")

    def _mini_avatar_yukle(self):
        p = self.veri["profil"]
        img = None
        if p.get("avatar_yolu") and Path(p["avatar_yolu"]).exists():
            try: img = Image.open(p["avatar_yolu"]).convert("RGB")
            except Exception: img = None
        if img is None: img = sinematik_kapak_uret(p.get("ad", "A"), "Araçlar", (100, 100))
        img = img.resize((56, 56), Image.LANCZOS) if img.size != (56, 56) else img
        img = yuvarlak_maske(img, 56)
        renk = CERCEVELER.get(p.get("cerceve", "mavi"), CERCEVELER["mavi"])["renk"]
        img = cerceve_ekle(img, renk, 3)
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(62, 62))
            self._mini_av_ref = ci
            self.mini_avatar.configure(image=ci, text="")
        except Exception: pass

    def _profil_guncelle(self):
        p = self.veri["profil"]
        try:
            self.mini_ad.configure(text=p.get("ad", "Oyuncu"))
            self.mini_unvan.configure(text=f"Lv.{p.get('seviye',1)} • {p.get('unvan','Yeni')}")
            ic_xp = p.get("xp", 0) % 500
            self.mini_xp_bar.set(ic_xp / 500)
            self.mini_seviye.configure(text=f"{ic_xp} / 500 XP")
            self._mini_avatar_yukle()
        except Exception: pass

    def _build_main(self):
        self.ana = ctk.CTkFrame(self, corner_radius=0, fg_color=RENKLER["arka"])
        self.ana.grid(row=0, column=1, sticky="nsew")
        self.ana.grid_rowconfigure(0, weight=0); self.ana.grid_rowconfigure(1, weight=1)
        self.ana.grid_columnconfigure(0, weight=1)
        bar = ctk.CTkFrame(self.ana, height=60, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 10))
        bar.grid_columnconfigure(1, weight=1)
        self.arama_entry = ctk.CTkEntry(bar, placeholder_text="🔎  Oyun Ara...", width=380, height=40,
                                         fg_color=RENKLER["yan"], border_color=RENKLER["cizgi"],
                                         text_color=RENKLER["metin"], placeholder_text_color=RENKLER["soluk"])
        self.arama_entry.grid(row=0, column=0, sticky="w")
        self.arama_entry.bind("<KeyRelease>", self._arama_degisti)
        self.kat_seg = ctk.CTkSegmentedButton(
            bar, values=["Tümü","Strateji","Yarış","RPG","Roguelike","Simülasyon","Aksiyon","Kurulu Olanlar"],
            command=self._kat_degisti, fg_color=RENKLER["yan"], selected_color=RENKLER["vurgu"],
            selected_hover_color=RENKLER["vurgu_hover"], unselected_color=RENKLER["yan"],
            unselected_hover_color=RENKLER["kart_hover"], text_color=RENKLER["metin"])
        self.kat_seg.set("Tümü")
        self.kat_seg.grid(row=0, column=2, padx=(20, 0), sticky="e")
        self.icerik = ctk.CTkScrollableFrame(self.ana, fg_color="transparent")
        self.icerik.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.icerik.grid_columnconfigure((0,1,2,3), weight=1)
        self.status = ctk.CTkLabel(self, text=f"ARDA LAUNCHER v{APP_VERSION} • Hazır", height=28, anchor="w",
                                    fg_color=RENKLER["yan"], text_color=RENKLER["soluk"],
                                    font=ctk.CTkFont(size=11))
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def durum(self, mesaj):
        try: self.status.configure(text=f"  {mesaj}")
        except Exception: pass

    def _sistem_monitor(self):
        try:
            if self._monitor_job: self.after_cancel(self._monitor_job)
        except Exception: pass
        refresh = int(self.veri.get("settings", {}).get("monitor_refresh", 2000))
        if refresh > 0:
            cpu, ram = sistem_cpu(), sistem_ram()
            try:
                self.cpu_lbl.configure(text=f"CPU  {cpu:.0f}%")
                self.ram_lbl.configure(text=f"RAM  {ram:.0f}%")
                self.cpu_bar.set(cpu / 100); self.ram_bar.set(ram / 100)
            except Exception: pass
            self._monitor_job = self.after(refresh, self._sistem_monitor)

    # ================================================================
    # HERO CAROUSEL — SCROLL FIX: SADECE HERO İÇERİĞİNİ GÜNCELLER
    # ================================================================
    def _auto_slider(self):
        """Her 6 saniyede hero'yu ilerlet. Sayfa yeniden çizilmez."""
        try:
            if (self.aktif_sayfa == "kesfet" and not self.arama
                    and not self._hero_paused
                    and getattr(self, "hero_ids", None)):
                self._hero_index += 1
                self._hero_guncelle()
        except Exception:
            pass
        self.after(6000, self._auto_slider)

    def _hero_prev(self):
        """Önceki slayda geç - sadece hero içeriğini günceller."""
        if not getattr(self, "hero_ids", None): return
        self._hero_index -= 1
        self._hero_guncelle()

    def _hero_next(self):
        """Sonraki slayda geç - sadece hero içeriğini günceller."""
        if not getattr(self, "hero_ids", None): return
        self._hero_index += 1
        self._hero_guncelle()

    def _hero_pause(self, event=None):
        self._hero_paused = True

    def _hero_resume(self, event=None):
        self._hero_paused = False

    def _hero_guncelle(self):
        """Hero banner içindeki görsel, başlık, açıklama, buton, noktaları günceller.
        Tüm sayfayı yeniden çizmez → scroll konumu korunur."""
        try:
            if not self.hero_ids: return
            self._hero_index %= len(self.hero_ids)
            aktif_id = self.hero_ids[self._hero_index]
            onerilen = self.oyunlar.get(aktif_id)
            if not onerilen: return
            if self.hero_banner is not None:
                self.gorsel_yukle_guvenli(self.hero_banner, aktif_id, "banner",
                    onerilen.get("banner_urls", onerilen.get("kapak_urls", [])),
                    (1080, 280), onerilen["isim"], onerilen["tur"], overlay=True)
            if self.hero_title_lbl is not None:
                self.hero_title_lbl.configure(text=onerilen["isim"])
            if self.hero_desc_lbl is not None:
                self.hero_desc_lbl.configure(text=onerilen["aciklama"][:90] + "...")
            if self.hero_incele_btn is not None:
                self.hero_incele_btn.configure(
                    command=lambda oid=aktif_id: self.oyun_detay_goster(oid))
            if self.hero_dots is not None:
                for w in self.hero_dots.winfo_children():
                    try: w.destroy()
                    except Exception: pass
                for i in range(len(self.hero_ids)):
                    c = RENKLER["vurgu"] if i == self._hero_index else RENKLER["soluk"]
                    ctk.CTkLabel(self.hero_dots, text="●", font=ctk.CTkFont(size=12),
                                 text_color=c).pack(side="left", padx=3)
        except Exception as e:
            print(f"[HERO] {e}")

    def _arama_degisti(self, _=None):
        self.arama = self.arama_entry.get().strip().lower()
        if self.aktif_sayfa in ("kesfet","kutuphanem"): self.sayfa_degistir(self.aktif_sayfa)
    def _kat_degisti(self, _):
        if self.aktif_sayfa in ("kesfet","kutuphanem"): self.sayfa_degistir(self.aktif_sayfa)

    def _filtrele(self, oid, o):
        if self.arama and self.arama not in o["isim"].lower(): return False
        k = self.kat_seg.get()
        if k == "Tümü": return True
        if k == "Kurulu Olanlar": return self._kurulu_mu(oid, o)
        return o.get("tur", "") == k

    def _kurulu_mu(self, oid, o):
        exe = o.get("exe_adi")
        if not exe: return False
        kayitli = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if kayitli and Path(kayitli).exists(): return True
        k = self.oyunlar_dizini / oid
        return k.exists() and any(k.rglob(exe))

    # ================================================================
    # SCROLL KONUMU KORUMALI SAYFA DEĞİŞTİRME
    # ================================================================
    def _scroll_kaydet(self, sayfa):
        """Mevcut sayfanın dikey kaydırma konumunu kaydet (0.0 - 1.0)."""
        try:
            pos = self.icerik._parent_canvas.yview()[0]
            self._scroll_positions[sayfa] = float(pos)
        except Exception:
            pass

    def _scroll_geri_yukle(self, pos):
        """Kaydedilmiş kaydırma konumunu geri yükle."""
        try:
            if pos and pos > 0.001:
                self.icerik._parent_canvas.yview_moveto(pos)
        except Exception:
            pass

    def sayfa_degistir(self, s):
        # Hero referanslarını temizle (sayfa değişiyor)
        self.hero_frame = None
        self.hero_banner = None
        self.hero_title_lbl = None
        self.hero_desc_lbl = None
        self.hero_incele_btn = None
        self.hero_dots = None
        self.hero_ids = []

        # Mevcut scroll pozisyonunu kaydet
        try:
            if self.aktif_sayfa:
                self._scroll_kaydet(self.aktif_sayfa)
        except Exception:
            pass

        self.aktif_sayfa = s
        for k, b in self.nav_btn.items():
            b.configure(fg_color=RENKLER["vurgu"] if k == s else "transparent",
                        text_color="white" if k == s else RENKLER["metin"])
        for w in self.icerik.winfo_children(): w.destroy()
        {"kesfet": self._kesfet, "kutuphanem": self._kutuphanem, "indirmeler": self._indirmeler,
         "profil": self._profil, "ayarlar": self._ayarlar}.get(s, lambda: None)()

        # Hedef sayfanın kaydedilmiş scroll konumunu geri yükle
        saved = self._scroll_positions.get(s, 0.0)
        if saved and saved > 0.001:
            self.after(50, lambda p=saved: self._scroll_geri_yukle(p))

    # ================================================================
    # KEŞFET — Hero'yu sınıf özelliği olarak sakla
    # ================================================================
    def _kesfet(self):
        one = ["mindustry","openttd","warzone2100","zeroad","veloren","supertuxkart"]
        one = [x for x in one if x in self.oyunlar]
        if not one: one = list(self.oyunlar.keys())[:6]
        self._hero_index %= max(len(one), 1)
        aktif_id = one[self._hero_index] if one else None
        onerilen = self.oyunlar.get(aktif_id) if aktif_id else None

        if onerilen:
            hero = ctk.CTkFrame(self.icerik, height=280, corner_radius=16, fg_color=RENKLER["kart"])
            hero.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 25))
            hero.grid_propagate(False); hero.grid_rowconfigure(0, weight=1)
            hero.grid_columnconfigure(0, weight=1)
            self.hero_frame = hero

            banner = ctk.CTkLabel(hero, text="")
            banner.grid(row=0, column=0, sticky="nsew")
            self.hero_banner = banner
            self.gorsel_yukle_guvenli(banner, aktif_id, "banner",
                onerilen.get("banner_urls", onerilen.get("kapak_urls", [])),
                (1080, 280), onerilen["isim"], onerilen["tur"], overlay=True)

            info = ctk.CTkFrame(hero, fg_color=RENKLER["yan"], corner_radius=10)
            info.place(x=25, y=165)
            title_lbl = ctk.CTkLabel(info, text=onerilen["isim"],
                                      font=ctk.CTkFont(size=22, weight="bold"),
                                      text_color="white")
            title_lbl.pack(anchor="w", padx=15, pady=(10, 2))
            self.hero_title_lbl = title_lbl

            desc_lbl = ctk.CTkLabel(info, text=onerilen["aciklama"][:90] + "...",
                                     font=ctk.CTkFont(size=11), text_color=RENKLER["soluk"],
                                     wraplength=500, justify="left")
            desc_lbl.pack(anchor="w", padx=15, pady=(0, 8))
            self.hero_desc_lbl = desc_lbl

            incele_btn = ctk.CTkButton(info, text="İncele", width=110, height=30,
                                        fg_color=RENKLER["vurgu"], hover_color=RENKLER["vurgu_hover"],
                                        command=lambda oid=aktif_id: self.oyun_detay_goster(oid))
            incele_btn.pack(anchor="w", padx=15, pady=(0, 10))
            self.hero_incele_btn = incele_btn

            ctk.CTkButton(hero, text="◀", width=36, height=36, font=ctk.CTkFont(size=16),
                          fg_color=RENKLER["yan"], hover_color=RENKLER["vurgu_hover"],
                          command=self._hero_prev).place(relx=0.0, rely=0.5, x=15, anchor="w")
            ctk.CTkButton(hero, text="▶", width=36, height=36, font=ctk.CTkFont(size=16),
                          fg_color=RENKLER["yan"], hover_color=RENKLER["vurgu_hover"],
                          command=self._hero_next).place(relx=1.0, rely=0.5, x=-15, anchor="e")

            dots = ctk.CTkFrame(hero, fg_color="transparent")
            dots.place(relx=0.5, rely=1.0, y=-15, anchor="s")
            self.hero_dots = dots
            for i in range(len(one)):
                c = RENKLER["vurgu"] if i == self._hero_index else RENKLER["soluk"]
                ctk.CTkLabel(dots, text="●", font=ctk.CTkFont(size=12), text_color=c).pack(side="left", padx=3)

            self.hero_ids = list(one)

            # --- FARE HERO ÜZERİNDEYKEN OTOMATİK GEÇİŞİ DURDUR ---
            hero.bind("<Enter>", self._hero_pause, add="+")
            hero.bind("<Leave>", self._hero_resume, add="+")
            for w in (banner, title_lbl, desc_lbl, incele_btn, dots):
                try:
                    w.bind("<Enter>", self._hero_pause, add="+")
                    w.bind("<Leave>", self._hero_resume, add="+")
                except Exception:
                    pass

        filtreli = [(oid, o) for oid, o in self.oyunlar.items() if self._filtrele(oid, o)]
        if not filtreli:
            ctk.CTkLabel(self.icerik, text="Eşleşen oyun bulunamadı.",
                         font=ctk.CTkFont(size=15), text_color=RENKLER["soluk"]).grid(
                row=1, column=0, columnspan=4, pady=60); return
        for i, (oid, o) in enumerate(filtreli):
            r, c = divmod(i, 4)
            fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
            OyunKarti(self.icerik, oid, o, self, favori=fav).grid(
                row=r + 1, column=c, padx=10, pady=10, sticky="nsew")

    def _kutuphanem(self):
        header = ctk.CTkFrame(self.icerik, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="📚 Kütüphanem", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=0, column=0, sticky="w")
        btn_f = ctk.CTkFrame(header, fg_color="transparent")
        btn_f.grid(row=0, column=1, sticky="e")
        for t, cb, c in [("📂 Klasör Tara", self.klasor_tara, RENKLER["vurgu"]),
                         ("⚡ Hızlı Tarama", self.hizli_tara, RENKLER["sari"]),
                         ("+ Oyun Ekle", self.oyun_ekle, RENKLER["yesil"])]:
            ctk.CTkButton(btn_f, text=t, width=130, height=35, fg_color=c, command=cb).pack(side="left", padx=4)
        kurulu = [(oid, o) for oid, o in self.oyunlar.items() if self._kurulu_mu(oid, o)]
        if not kurulu:
            ctk.CTkLabel(self.icerik, text="Kütüphanenizde henüz oyun yok.\n'Keşfet'ten indirin veya 'Klasör Tara' kullanın.",
                         font=ctk.CTkFont(size=14), text_color=RENKLER["soluk"], justify="left").grid(
                row=1, column=0, columnspan=4, pady=50, sticky="w"); return
        if self.veri["koleksiyonlar"]:
            ctk.CTkLabel(self.icerik, text="🗂️ Koleksiyonlarım", font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).grid(row=1, column=0, columnspan=4, sticky="w", pady=(5, 8))
            cf = ctk.CTkFrame(self.icerik, fg_color="transparent")
            cf.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 15))
            for cname, cids in self.veri["koleksiyonlar"].items():
                ctk.CTkButton(cf, text=f"🗂️ {cname} ({len(cids)})", width=180, height=32,
                              fg_color=RENKLER["vurgu"], hover_color=RENKLER["vurgu_hover"],
                              command=lambda cn=cname: self._koleksiyon_goster(cn)).pack(side="left", padx=3)
        favoriler = [x for x in kurulu if self.veri["oyunlar"].get(x[0], {}).get("favori")]
        son_row = 3 if self.veri["koleksiyonlar"] else 1
        if favoriler:
            ctk.CTkLabel(self.icerik, text="❤️ Favorilerim", font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).grid(row=son_row, column=0, columnspan=4,
                                                            sticky="w", pady=(10, 10))
            for i, (oid, o) in enumerate(favoriler[:4]):
                OyunKarti(self.icerik, oid, o, self, favori=True).grid(
                    row=son_row + 1, column=i, padx=10, pady=10, sticky="nsew")
            son_row += 2
        ctk.CTkLabel(self.icerik, text="📁 Tüm Oyunlarım", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=son_row, column=0, columnspan=4,
                                                        sticky="w", pady=(15, 10))
        for i, (oid, o) in enumerate(kurulu):
            r, c = divmod(i, 4)
            fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
            OyunKarti(self.icerik, oid, o, self, favori=fav).grid(
                row=son_row + r + 1, column=c, padx=10, pady=10, sticky="nsew")

    def _koleksiyon_goster(self, cname):
        cids = self.veri["koleksiyonlar"].get(cname, [])
        for w in self.icerik.winfo_children(): w.destroy()
        ctk.CTkButton(self.icerik, text="← Geri", width=80, fg_color="transparent",
                      hover_color=RENKLER["kart_hover"],
                      command=lambda: self.sayfa_degistir("kutuphanem")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        ctk.CTkLabel(self.icerik, text=f"🗂️ {cname}", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 15))
        for i, oid in enumerate(cids):
            if oid in self.oyunlar:
                r, c = divmod(i, 4)
                fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
                OyunKarti(self.icerik, oid, self.oyunlar[oid], self, favori=fav).grid(
                    row=2 + r, column=c, padx=10, pady=10, sticky="nsew")

    def _indirmeler(self):
        ctk.CTkLabel(self.icerik, text="📥 Aktif İndirmeler", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 20))
        aktif = dict(self.indirme_yon.aktif)
        if not aktif:
            ctk.CTkLabel(self.icerik, text="Aktif indirme yok.", font=ctk.CTkFont(size=14),
                         text_color=RENKLER["soluk"]).grid(row=1, column=0, columnspan=4, pady=50, sticky="w"); return
        for i, (oid, d) in enumerate(aktif.items()):
            oyun = self.oyunlar.get(oid, {})
            kart = ctk.CTkFrame(self.icerik, corner_radius=10, fg_color=RENKLER["kart"])
            kart.grid(row=i + 1, column=0, columnspan=4, sticky="ew", pady=8, padx=5)
            kart.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(kart, text=oyun.get("isim", oid), font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
            y = d["indirilen"] / d["toplam"] if d["toplam"] else 0
            bar = ctk.CTkProgressBar(kart, height=8, progress_color=RENKLER["vurgu"])
            bar.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="ew"); bar.set(y)
            et = f" • Kalan: {fmt_sure(d.get('eta', 0))}" if d.get("eta", 0) > 0 else ""
            ctk.CTkLabel(kart, text=f"{fmt_bayt(d['indirilen'])} / {fmt_bayt(d['toplam'])} • "
                                     f"{d.get('hiz', 0):.2f} MB/s • {y*100:.1f}%{et}",
                         font=ctk.CTkFont(size=12), text_color=RENKLER["soluk"]).grid(
                row=2, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")
            bf = ctk.CTkFrame(kart, fg_color="transparent")
            bf.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="e")
            if d["durum"] == "indiriliyor":
                ctk.CTkButton(bf, text="⏸", width=45, height=30, fg_color=RENKLER["sari"],
                              command=lambda o=oid: self.indirme_yon.duraklat(o)).pack(side="left", padx=3)
            elif d["durum"] == "duraklatildi":
                ctk.CTkButton(bf, text="▶", width=45, height=30, fg_color=RENKLER["yesil"],
                              command=lambda o=oid, ov=oyun: self.indirme_yon.devam(o, ov)).pack(side="left", padx=3)
            ctk.CTkButton(bf, text="✖", width=45, height=30, fg_color=RENKLER["kirmizi"],
                          command=lambda o=oid: self.indirme_yon.iptal(o)).pack(side="left", padx=3)

    # ============ AYARLAR ============
    def _dizin_ac(self, path):
        try: Path(path).mkdir(parents=True, exist_ok=True)
        except Exception: pass
        try:
            if sys.platform == "win32": subprocess.Popen(["explorer", str(path)])
            elif sys.platform == "darwin": subprocess.Popen(["open", str(path)])
            else: subprocess.Popen(["xdg-open", str(path)])
        except Exception as e: self.durum(f"Açılamadı: {e}")

    def _update_entry(self, entry, val):
        try:
            entry.delete(0, "end"); entry.insert(0, str(val))
        except Exception: pass

    def sistem_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(BASE_DIR))
        if not yeni: return
        self._update_entry(self.sys_path_entry, yeni)
        self._sistem_dizin_uygula(yeni)

    def _eski_dizin_bosalt(self, eski):
        try:
            if not eski.exists() or not eski.is_dir(): return True
            try:
                if eski.resolve() == BASE_DIR.resolve(): return False
            except Exception: pass
            dosya_var = any(True for _, _, fs in os.walk(eski) for _ in fs)
            if dosya_var: return False
            shutil.rmtree(eski, ignore_errors=True); return True
        except Exception: return False

    def _sistem_dizin_uygula(self, yol):
        global BASE_DIR, CACHE_COVERS, PROFILE_CACHE, MODS_DIR, DATA_DOSYASI, ICON_DOSYASI
        yol = (yol or "").strip()
        if not yol: return
        try: newp = Path(yol).resolve()
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        try:
            if newp == BASE_DIR.resolve(): self.durum("Zaten bu dizin."); return
        except Exception: pass
        if not messagebox.askyesno("Taşıma", f"Veriler şuraya taşınacak:\n{newp}\n\nDevam?"): return
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
            nv = load_json(DATA_DOSYASI, {})
            if nv: self.veri = nv
            save_json(DATA_DOSYASI, self.veri)
            eski_silindi = self._eski_dizin_bosalt(eski_dizin)
            if eski_silindi:
                messagebox.showinfo("Başarılı", f"✅ Taşındı: {newp}\n🗑️ Eski dizin silindi.\nYeniden başlatın.")
            else:
                messagebox.showwarning("Kısmi Temizlik", f"✅ Taşındı: {newp}\n⚠️ Eski dizinde dosyalar var.\nYeniden başlatın.")
            self.sayfa_degistir("ayarlar")
        except Exception as e: messagebox.showerror("Hata", str(e))

    def games_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(self.oyunlar_dizini))
        if not yeni: return
        self._update_entry(self.games_path_entry, yeni); self._oyun_dizin_uygula(yeni)
    def _oyun_dizin_uygula(self, yol):
        yol = (yol or "").strip()
        if not yol: return
        p = Path(yol)
        try: p.mkdir(parents=True, exist_ok=True)
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        self.oyunlar_dizini = p; self.veri["indirme_dizini"] = str(p)
        save_json(DATA_DOSYASI, self.veri)
        self._update_entry(self.games_path_entry, p)
        self.durum(f"🎮 {p}")
        messagebox.showinfo("Başarılı", f"✅ {p}")
        self.sayfa_degistir("ayarlar")

    def backups_dizin_sec(self):
        yeni = filedialog.askdirectory(parent=self, initialdir=str(self.yedek_dizini))
        if not yeni: return
        self._update_entry(self.backups_path_entry, yeni); self._yedek_dizin_uygula(yeni)
    def _yedek_dizin_uygula(self, yol):
        yol = (yol or "").strip()
        if not yol: return
        p = Path(yol)
        try: p.mkdir(parents=True, exist_ok=True)
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        self.yedek_dizini = p; self.veri["yedek_dizini"] = str(p)
        save_json(DATA_DOSYASI, self.veri)
        self._update_entry(self.backups_path_entry, p)
        self.durum(f"💾 {p}")
        messagebox.showinfo("Başarılı", f"✅ {p}")
        self.sayfa_degistir("ayarlar")

    def masaustu_kisayolu_olustur(self, sessiz=False):
        if sys.platform != "win32":
            if not sessiz: messagebox.showinfo("Bilgi", "Windows.")
            return False
        try:
            py = sys.executable
            pyw = py.replace("python.exe", "pythonw.exe")
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
            try:
                subprocess.run(["cscript", "//nologo", str(tmp)],
                               creationflags=0x08000000, capture_output=True, timeout=15)
            finally:
                try: tmp.unlink()
                except Exception: pass
            if lnk.exists():
                if not sessiz:
                    messagebox.showinfo("Başarılı", f"✅ Kısayol:\n{lnk}")
                    self._aktivite_ekle("Masaüstü kısayolu")
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
        except Exception as e: messagebox.showerror("Hata", str(e))

    def oyun_kaldir(self, oid):
        oyun = self.oyunlar[oid]
        if not messagebox.askyesno("Kaldır", f"'{oyun['isim']}' silinsin mi?"): return
        k = self.oyunlar_dizini / oid
        if k.exists():
            try: shutil.rmtree(k, ignore_errors=True)
            except Exception: pass
        self.veri["oyunlar"].pop(oid, None)
        if oid in self.veri["eklenen_oyunlar"]:
            del self.veri["eklenen_oyunlar"][oid]; self.oyunlar.pop(oid, None)
        save_json(DATA_DOSYASI, self.veri)
        self.sayfa_degistir(self.aktif_sayfa)

    def launcher_uninstall(self):
        if not messagebox.askyesno("Kaldır", "ARDA LAUNCHER tamamen silinecek!\nDevam?"): return
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
        bat.write_text(
            f'@echo off\r\ntimeout /t 2 /nobreak >nul\r\n'
            f'rmdir /s /q "{BASE_DIR}" 2>nul\r\n'
            f'del /f /q "{script}" 2>nul\r\ndel /f /q "%~f0" 2>nul\r\n',
            encoding="utf-8")
        try:
            subprocess.Popen(["cmd", "/c", str(bat)],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS)
        except Exception: pass
        self.destroy(); sys.exit(0)

    def disa_aktar(self):
        try:
            f = filedialog.asksaveasfilename(parent=self, defaultextension=".json",
                initialfile=f"arda_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                filetypes=[("JSON", "*.json")])
            if not f: return
            shutil.copy2(DATA_DOSYASI, f)
            messagebox.showinfo("Başarılı", f)
        except Exception as e: messagebox.showerror("Hata", str(e))
    def ice_aktar(self):
        f = filedialog.askopenfilename(parent=self, filetypes=[("JSON", "*.json")])
        if not f: return
        if not messagebox.askyesno("İçe Aktar", "Mevcut veriler değişecek. Devam?"): return
        try:
            shutil.copy2(f, DATA_DOSYASI)
            messagebox.showinfo("Başarılı", "İçe aktarıldı. Yeniden başlatın.")
        except Exception as e: messagebox.showerror("Hata", str(e))
    def onb_temizle(self):
        for x in CACHE_COVERS.glob("*"):
            if x.is_file():
                try: x.unlink()
                except Exception: pass
        self.sayfa_degistir("ayarlar")
    def sifirla(self):
        if messagebox.askyesno("Onay", "Tüm veriler silinecek?"):
            self.veri["oyunlar"] = {}; self.veri["son_aktiviteler"] = []
            self.veri["gunluk_oynama"] = {}
            p = self.veri["profil"]; p["xp"] = 0; p["seviye"] = 1; p["rozetler"] = []
            save_json(DATA_DOSYASI, self.veri)
            self.sayfa_degistir("ayarlar")

    # ============ GELİŞTİRİCİ MODU ============
    def _dev_toggle(self):
        self._dev_visible = not self._dev_visible
        if self._dev_visible:
            self.dev_frame.pack(fill="x", padx=10, pady=(5, 15))
            self.dev_toggle_btn.configure(text="🔧 Geliştirici Modu (Kapat)")
        else:
            self.dev_frame.pack_forget()
            self.dev_toggle_btn.configure(text="🔧 Geliştirici Modu (Gizli)")

    def _dev_auto_next_version(self):
        try:
            parts = APP_VERSION.split(".")
            if parts and parts[-1].isdigit():
                parts[-1] = str(int(parts[-1]) + 1)
                return ".".join(parts)
        except Exception: pass
        return APP_VERSION

    def _dev_publish(self):
        owner = (self.dev_owner_entry.get() or "").strip()
        repo = (self.dev_repo_entry.get() or "").strip()
        token = (self.dev_token_entry.get() or "").strip()
        branch = (self.dev_branch_entry.get() or "main").strip()
        new_version = (self.dev_version_entry.get() or "").strip()
        notes = self.dev_notes_box.get("1.0", "end-1c").strip()
        if not owner or not repo or not token:
            messagebox.showerror("Eksik", "GitHub Kullanıcı Adı, Repo Adı ve PAT zorunludur."); return
        if not new_version:
            messagebox.showerror("Eksik", "Yeni sürüm numarası zorunludur."); return
        script = _get_script_path()
        if not script:
            messagebox.showerror("Hata", "launcher.pyw yolu tespit edilemedi."); return
        if not messagebox.askyesno("Yayınla", f"Yüklenecek:\n\n📦 {owner}/{repo}\n🌿 {branch}\n🔖 v{new_version}\n\nDevam?"):
            return
        self.veri["dev"] = {"owner": owner, "repo": repo, "token": token, "branch": branch,
                            "next_version": new_version, "notes": notes}
        save_json(DATA_DOSYASI, self.veri)
        self.dev_status_lbl.configure(text="⏳ Yayınlanıyor...", text_color=RENKLER["sari"])
        self.dev_progress.set(0)
        try: self.dev_publish_btn.configure(state="disabled")
        except Exception: pass
        def progress_cb(msg, pct):
            def _u():
                try:
                    self.dev_status_lbl.configure(text=f"⏳ {msg}")
                    self.dev_progress.set(pct / 100)
                except Exception: pass
            try: self.after(0, _u)
            except Exception: pass
        def work():
            try:
                pub = GitHubPublisher(token, owner, repo, branch)
                res = pub.publish(script, new_version, notes, progress_cb=progress_cb)
                self.after(0, lambda r=res, nv=new_version, ow=owner, rp=repo, br=branch:
                           self._dev_publish_done(r, nv, ow, rp, br))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: self._dev_publish_fail(err))
        threading.Thread(target=work, daemon=True).start()

    def _dev_publish_done(self, res, new_version, owner, repo, branch):
        try: self.dev_publish_btn.configure(state="normal")
        except Exception: pass
        if res.get("ok"):
            self.dev_status_lbl.configure(text=f"✅ Yayınlandı! v{new_version}", text_color=RENKLER["yesil"])
            self.dev_progress.set(1.0)
            messagebox.showinfo("Başarılı",
                f"✅ v{new_version} başarıyla yayınlandı!\n\n📦 {owner}/{repo} ({branch})\n\n"
                "Kullanıcılar bir sonraki açılışta güncelleme alacak.")
        else:
            self.dev_status_lbl.configure(text=f"❌ Hata: {res.get('error','?')}", text_color=RENKLER["kirmizi"])
            messagebox.showerror("Yayın Hatası",
                f"Adım: {res.get('step','?')}\nDurum: {res.get('status','?')}\nHata: {res.get('error','?')}")

    def _dev_publish_fail(self, err):
        try: self.dev_publish_btn.configure(state="normal")
        except Exception: pass
        try:
            self.dev_status_lbl.configure(text=f"❌ {err[:60]}", text_color=RENKLER["kirmizi"])
        except Exception: pass
        messagebox.showerror("Bağlantı Hatası", err)

    def _dev_test_connection(self):
        owner = (self.dev_owner_entry.get() or "").strip()
        repo = (self.dev_repo_entry.get() or "").strip()
        token = (self.dev_token_entry.get() or "").strip()
        if not owner or not repo or not token:
            messagebox.showerror("Eksik", "Tüm alanlar gerekli."); return
        def work():
            try:
                r = requests.get(f"https://api.github.com/repos/{owner}/{repo}",
                                 headers={"Authorization": f"token {token}",
                                          "Accept": "application/vnd.github+json",
                                          "User-Agent": "ArdaLauncher-Publisher/8.3"},
                                 timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    perms = data.get("permissions", {})
                    push = perms.get("push", False)
                    self.after(0, lambda: messagebox.showinfo(
                        "Bağlantı Başarılı",
                        f"✅ Repo: {data.get('full_name')}\n"
                        f"🌿 Default branch: {data.get('default_branch')}\n"
                        f"📝 Push yetkisi: {'✅ VAR' if push else '❌ YOK'}"))
                else:
                    self.after(0, lambda: messagebox.showerror("Hata",
                        f"HTTP {r.status_code}\nPAT 'repo' scope kontrol edin."))
            except Exception as e:
                err = str(e)
                self.after(0, lambda: messagebox.showerror("Hata", err))
        threading.Thread(target=work, daemon=True).start()

    def _ayarlar(self):
        ctk.CTkLabel(self.icerik, text="⚙️ Ayarlar Merkezi", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))
        tabs = ctk.CTkTabview(self.icerik, fg_color=RENKLER["kart"],
                              segmented_button_fg_color=RENKLER["yan"],
                              segmented_button_selected_color=RENKLER["vurgu"],
                              segmented_button_selected_hover_color=RENKLER["vurgu_hover"],
                              text_color=RENKLER["metin"])
        tabs.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        t1 = tabs.add("📁 Dizin"); t2 = tabs.add("🌐 Ağ"); t3 = tabs.add("⚡ Performans")
        t4 = tabs.add("🎨 Görünüm"); t5 = tabs.add("🛠️ Bakım")

        # TAB 1
        f = ctk.CTkFrame(t1, fg_color="transparent"); f.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f, text="Sistem Veri Dizini:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
        r1 = ctk.CTkFrame(f, fg_color="transparent"); r1.pack(fill="x", pady=(0, 10))
        self.sys_path_entry = ctk.CTkEntry(r1, height=34, fg_color=RENKLER["yan"],
                                            text_color=RENKLER["metin"], font=ctk.CTkFont(size=11))
        self.sys_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.sys_path_entry.insert(0, str(BASE_DIR))
        ctk.CTkButton(r1, text="📁 Gözat", width=80, height=34, fg_color=RENKLER["vurgu"],
                      command=self.sistem_dizin_sec).pack(side="left", padx=2)
        ctk.CTkButton(r1, text="✅ Uygula", width=80, height=34, fg_color=RENKLER["yesil"],
                      command=lambda: self._sistem_dizin_uygula(self.sys_path_entry.get())).pack(side="left", padx=2)
        ctk.CTkButton(r1, text="📂 Aç", width=70, height=34, fg_color=RENKLER["yan"],
                      command=lambda: self._dizin_ac(BASE_DIR)).pack(side="left", padx=2)

        ctk.CTkLabel(f, text="Oyun Kurulum Klasörü:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
        r2 = ctk.CTkFrame(f, fg_color="transparent"); r2.pack(fill="x", pady=(0, 10))
        self.games_path_entry = ctk.CTkEntry(r2, height=34, fg_color=RENKLER["yan"],
                                              text_color=RENKLER["metin"], font=ctk.CTkFont(size=11))
        self.games_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.games_path_entry.insert(0, str(self.oyunlar_dizini))
        ctk.CTkButton(r2, text="📁 Gözat", width=80, height=34, fg_color=RENKLER["vurgu"],
                      command=self.games_dizin_sec).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="✅ Uygula", width=80, height=34, fg_color=RENKLER["yesil"],
                      command=lambda: self._oyun_dizin_uygula(self.games_path_entry.get())).pack(side="left", padx=2)
        ctk.CTkButton(r2, text="📂 Aç", width=70, height=34, fg_color=RENKLER["yan"],
                      command=lambda: self._dizin_ac(self.oyunlar_dizini)).pack(side="left", padx=2)

        ctk.CTkLabel(f, text="Kayıt Yedekleme Klasörü:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
        r3 = ctk.CTkFrame(f, fg_color="transparent"); r3.pack(fill="x", pady=(0, 10))
        self.backups_path_entry = ctk.CTkEntry(r3, height=34, fg_color=RENKLER["yan"],
                                                text_color=RENKLER["metin"], font=ctk.CTkFont(size=11))
        self.backups_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.backups_path_entry.insert(0, str(self.yedek_dizini))
        ctk.CTkButton(r3, text="📁 Gözat", width=80, height=34, fg_color=RENKLER["vurgu"],
                      command=self.backups_dizin_sec).pack(side="left", padx=2)
        ctk.CTkButton(r3, text="✅ Uygula", width=80, height=34, fg_color=RENKLER["yesil"],
                      command=lambda: self._yedek_dizin_uygula(self.backups_path_entry.get())).pack(side="left", padx=2)
        ctk.CTkButton(r3, text="📂 Aç", width=70, height=34, fg_color=RENKLER["yan"],
                      command=lambda: self._dizin_ac(self.yedek_dizini)).pack(side="left", padx=2)

        try:
            total, used, free = disk_usage_gb(self.oyunlar_dizini)
            ob = folder_size_bayt(self.oyunlar_dizini) / (1024**3)
            df = ctk.CTkFrame(f, fg_color=RENKLER["yan"], corner_radius=8)
            df.pack(fill="x", pady=(10, 5))
            ctk.CTkLabel(df, text=f"💽 {used:.1f}/{total:.1f} GB • Oyunlar: {ob:.2f} GB",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["metin"]).pack(padx=10, pady=(8, 4), anchor="w")
            db = ctk.CTkProgressBar(df, height=10, progress_color=RENKLER["vurgu"])
            db.pack(fill="x", padx=10, pady=(0, 10))
            db.set(used / total if total > 0 else 0)
        except Exception: pass

        # TAB 2
        g = ctk.CTkFrame(t2, fg_color="transparent"); g.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(g, text="İndirme Hız Limiti:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 2))
        sm = {0: "Sınırsız", 5: "5 MB/s", 10: "10 MB/s", 25: "25 MB/s"}
        cur_s = sm.get(int(self.veri["settings"].get("download_speed_limit", 0)), "Sınırsız")
        sp = ctk.CTkOptionMenu(g, values=list(sm.values()), width=200, fg_color=RENKLER["yan"],
                                command=lambda v: self._set_speed(v))
        sp.set(cur_s); sp.pack(anchor="w", pady=(0, 10))
        av = ctk.BooleanVar(value=self.veri["settings"].get("auto_extract", True))
        ctk.CTkSwitch(g, text="Arşivi otomatik çıkar", variable=av, fg_color=RENKLER["vurgu"],
                      command=lambda: self._set_setting("auto_extract", av.get())).pack(anchor="w", pady=5)

        # TAB 3
        h = ctk.CTkFrame(t3, fg_color="transparent"); h.pack(fill="x", padx=10, pady=5)
        sv = ctk.BooleanVar(value=self.veri["settings"].get("startup_enabled", False))
        ctk.CTkSwitch(h, text="Windows Başlangıcında Çalıştır", variable=sv,
                      fg_color=RENKLER["vurgu"], command=lambda: self._set_startup(sv.get())).pack(anchor="w", pady=8)
        gb = ctk.BooleanVar(value=self.veri["settings"].get("game_booster", True))
        ctk.CTkSwitch(h, text="Game Booster", variable=gb, fg_color=RENKLER["vurgu"],
                      command=lambda: self._set_setting("game_booster", gb.get())).pack(anchor="w", pady=8)
        mv = ctk.BooleanVar(value=self.veri["settings"].get("minimize_on_play", False))
        ctk.CTkSwitch(h, text="Oyun başlarken pencereyi küçült", variable=mv, fg_color=RENKLER["vurgu"],
                      command=lambda: self._set_setting("minimize_on_play", mv.get())).pack(anchor="w", pady=8)

        # TAB 4
        i = ctk.CTkFrame(t4, fg_color="transparent"); i.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(i, text="Tema:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", pady=(5, 4))
        tf = ctk.CTkFrame(i, fg_color="transparent"); tf.pack(anchor="w", pady=(0, 10))
        for ak, tt in TEMALAR.items():
            ctk.CTkButton(tf, text=tt["ad"], width=110, height=32, fg_color=tt["renk"],
                          hover_color=tt["hover"],
                          command=lambda a=ak: self.tema_degistir(a)).pack(side="left", padx=3)

        # TAB 5
        j = ctk.CTkFrame(t5, fg_color="transparent"); j.pack(fill="x", padx=10, pady=5)
        upd_frame = ctk.CTkFrame(j, fg_color=RENKLER["yan"], corner_radius=8)
        upd_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(upd_frame, text=f"🔄 Mevcut Sürüm: v{APP_VERSION}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", padx=12, pady=(8, 4))
        ctk.CTkButton(upd_frame, text="🔍 Güncellemeleri Denetle", height=36,
                      fg_color=RENKLER["vurgu"], hover_color=RENKLER["vurgu_hover"],
                      command=self._manuel_guncelleme_denetle).pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkButton(j, text="🖥️ Masaüstü Kısayolu Oluştur", height=36,
                      fg_color=RENKLER["vurgu"], hover_color=RENKLER["vurgu_hover"],
                      command=lambda: self.masaustu_kisayolu_olustur(sessiz=False)).pack(fill="x", pady=4)
        ctk.CTkButton(j, text="📤 JSON Dışa Aktar", height=36, fg_color=RENKLER["yesil"],
                      command=self.disa_aktar).pack(fill="x", pady=4)
        ctk.CTkButton(j, text="📥 JSON İçe Aktar", height=36, fg_color=RENKLER["sari"],
                      command=self.ice_aktar).pack(fill="x", pady=4)
        ctk.CTkButton(j, text="🖼️ Kapak Önbelleğini Temizle", height=36, fg_color=RENKLER["yan"],
                      command=self.onb_temizle).pack(fill="x", pady=4)
        ctk.CTkButton(j, text="🗑️ Verileri Sıfırla", height=36, fg_color=RENKLER["sari"],
                      command=self.sifirla).pack(fill="x", pady=4)
        ctk.CTkButton(j, text="🚨 ARDA LAUNCHER'ı Tamamen Kaldır", height=40,
                      fg_color=RENKLER["kirmizi"], hover_color="#B91C1C",
                      command=self.launcher_uninstall).pack(fill="x", pady=(10, 5))

        # GELİŞTİRİCİ MODU
        dev_header = ctk.CTkFrame(t5, fg_color="transparent")
        dev_header.pack(fill="x", pady=(15, 0))
        self.dev_toggle_btn = ctk.CTkButton(dev_header, text="🔧 Geliştirici Modu (Gizli)",
                                             height=34, fg_color="#2a2a3a", hover_color="#3a3a4a",
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             command=self._dev_toggle)
        self.dev_toggle_btn.pack(fill="x")

        self.dev_frame = ctk.CTkFrame(t5, fg_color="#12121c", corner_radius=8,
                                       border_width=1, border_color="#3a3a4a")
        d = self.veri.get("dev", {})
        ctk.CTkLabel(self.dev_frame, text="🚀 GitHub'a Sürüm Yayınla",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=RENKLER["vurgu"]).pack(anchor="w", padx=12, pady=(12, 4))
        def _row(lbl, value, show=None):
            r = ctk.CTkFrame(self.dev_frame, fg_color="transparent"); r.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(r, text=lbl, width=140, anchor="w",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(side="left")
            e = ctk.CTkEntry(r, height=30, fg_color=RENKLER["yan"],
                             text_color=RENKLER["metin"], font=ctk.CTkFont(size=11),
                             show=show if show else "")
            e.pack(side="left", fill="x", expand=True)
            e.insert(0, value); return e
        self.dev_owner_entry = _row("👤 GitHub Kullanıcı:", d.get("owner", ""))
        self.dev_repo_entry = _row("📦 Repo Adı:", d.get("repo", ""))
        self.dev_token_entry = _row("🔑 GitHub PAT:", d.get("token", ""), show="•")
        self.dev_branch_entry = _row("🌿 Branch:", d.get("branch", "main"))
        next_v = d.get("next_version", "") or self._dev_auto_next_version()
        self.dev_version_entry = _row("🔖 Yeni Sürüm:", next_v)
        ctk.CTkLabel(self.dev_frame, text="📝 Yayın Notları:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", padx=12, pady=(8, 2))
        self.dev_notes_box = ctk.CTkTextbox(self.dev_frame, height=70, fg_color=RENKLER["yan"],
                                             text_color=RENKLER["metin"], font=ctk.CTkFont(size=11))
        self.dev_notes_box.pack(fill="x", padx=12, pady=(0, 8))
        self.dev_notes_box.insert("1.0", d.get("notes", ""))
        self.dev_progress = ctk.CTkProgressBar(self.dev_frame, height=8, progress_color=RENKLER["vurgu"])
        self.dev_progress.pack(fill="x", padx=12, pady=(4, 2)); self.dev_progress.set(0)
        self.dev_status_lbl = ctk.CTkLabel(self.dev_frame, text="Hazır",
                                            font=ctk.CTkFont(size=10), text_color=RENKLER["soluk"])
        self.dev_status_lbl.pack(anchor="w", padx=12, pady=(0, 8))
        btn_row = ctk.CTkFrame(self.dev_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(btn_row, text="🔗 Bağlantı Testi", width=120, height=34,
                      fg_color=RENKLER["yan"], hover_color=RENKLER["kart_hover"],
                      command=self._dev_test_connection).pack(side="left", padx=(0, 5))
        self.dev_publish_btn = ctk.CTkButton(btn_row, text="🚀 Bu Sürümü Yayınla", height=36,
                                              fg_color=RENKLER["yesil"], hover_color="#16A34A",
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              command=self._dev_publish)
        self.dev_publish_btn.pack(side="left", fill="x", expand=True)
        if self._dev_visible:
            self.dev_frame.pack(fill="x", padx=10, pady=(5, 15))

    def _set_speed(self, val):
        m = {"Sınırsız": 0, "5 MB/s": 5, "10 MB/s": 10, "25 MB/s": 25}
        self.veri["settings"]["download_speed_limit"] = m.get(val, 0)
        save_json(DATA_DOSYASI, self.veri)
    def _set_setting(self, key, val):
        self.veri["settings"][key] = val
        save_json(DATA_DOSYASI, self.veri)

    # ============ PROFİL ============
    def _profil(self):
        p = self.veri["profil"]
        bf = ctk.CTkFrame(self.icerik, height=200, corner_radius=14, fg_color=RENKLER["kart"])
        bf.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 30))
        bf.grid_propagate(False); bf.grid_rowconfigure(0, weight=1); bf.grid_columnconfigure(0, weight=1)
        banner_lbl = ctk.CTkLabel(bf, text="")
        banner_lbl.grid(row=0, column=0, sticky="nsew")
        if p.get("banner_yolu") and Path(p["banner_yolu"]).exists():
            try:
                img = Image.open(p["banner_yolu"]).convert("RGB")
                img = akilli_kirp(img, (1080, 200))
                ci = ctk.CTkImage(light_image=img, dark_image=img, size=(1080, 200))
                banner_lbl._arda_ref = ci; banner_lbl.configure(image=ci, text="")
            except Exception: self._banner_tema_uygula(banner_lbl, p.get("banner_tema", 0))
        else: self._banner_tema_uygula(banner_lbl, p.get("banner_tema", 0))
        avf = ctk.CTkFrame(self.icerik, fg_color="transparent")
        avf.grid(row=1, column=0, columnspan=4, sticky="w", padx=20)
        av = ctk.CTkLabel(avf, text="", width=120, height=120)
        av.pack(side="left", padx=(0, 20)); self._profil_avatar_yukle(av, 110)
        info = ctk.CTkFrame(avf, fg_color="transparent"); info.pack(side="left")
        ctk.CTkLabel(info, text=p["ad"], font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Lv.{p['seviye']} • {p['unvan']} • {p['durum']}",
                     font=ctk.CTkFont(size=13), text_color=RENKLER["soluk"]).pack(anchor="w", pady=2)
        ctk.CTkLabel(info, text=p.get("biyografi", ""), font=ctk.CTkFont(size=12),
                     text_color=RENKLER["soluk"], wraplength=600, justify="left").pack(anchor="w", pady=(4, 0))
        xf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=10)
        xf.grid(row=2, column=0, columnspan=4, sticky="ew", pady=15, padx=20)
        ctk.CTkLabel(xf, text=f"Level {p['seviye']} — {p['xp'] % 500}/500 XP",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(8, 4))
        xb = ctk.CTkProgressBar(xf, height=10, progress_color=RENKLER["vurgu"])
        xb.pack(fill="x", padx=15, pady=(0, 10)); xb.set((p["xp"] % 500) / 500)
        ctk.CTkButton(self.icerik, text="✏️ Profili Düzenle", height=40, fg_color=RENKLER["vurgu"],
                      hover_color=RENKLER["vurgu_hover"],
                      command=self.profil_duzenle).grid(row=3, column=0, columnspan=4,
                                                         sticky="e", pady=(0, 20), padx=20)
        ec = sorted([(oid, v.get("oynama_suresi", 0)) for oid, v in self.veri["oyunlar"].items()
                     if v.get("oynama_suresi", 0) > 0], key=lambda x: x[1], reverse=True)[:3]
        if ec:
            cf = ctk.CTkFrame(self.icerik, fg_color=RENKLER["kart"], corner_radius=12)
            cf.grid(row=4, column=0, columnspan=4, sticky="ew", pady=10, padx=20)
            ctk.CTkLabel(cf, text="📊 En Çok Oynadıklarım", font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=RENKLER["metin"]).pack(anchor="w", padx=15, pady=(10, 8))
            ms = ec[0][1] if ec else 1
            for oid, s in ec:
                rf = ctk.CTkFrame(cf, fg_color="transparent"); rf.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(rf, text=self.oyunlar.get(oid, {}).get("isim", oid), width=200, anchor="w",
                             font=ctk.CTkFont(size=12), text_color=RENKLER["metin"]).pack(side="left")
                bb = ctk.CTkProgressBar(rf, height=8, progress_color=RENKLER["vurgu"])
                bb.pack(side="left", fill="x", expand=True, padx=(10, 10)); bb.set(s / ms)
                ctk.CTkLabel(rf, text=fmt_sure(s), font=ctk.CTkFont(size=11),
                             text_color=RENKLER["soluk"]).pack(side="right")
            ctk.CTkLabel(cf, text="", height=8).pack()

    def _banner_tema_uygula(self, label, idx):
        t = BANNER_TEMALARI[idx % len(BANNER_TEMALARI)]
        img = Image.new("RGB", (1080, 200)); d = ImageDraw.Draw(img)
        for y in range(200):
            o = y / 199
            d.line([(0, y), (1080, y)], fill=(int(t["r1"][0]*(1-o)+t["r2"][0]*o),
                                              int(t["r1"][1]*(1-o)+t["r2"][1]*o),
                                              int(t["r1"][2]*(1-o)+t["r2"][2]*o)))
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(1080, 200))
            label._arda_ref = ci; label.configure(image=ci, text="")
        except Exception: pass

    def _profil_avatar_yukle(self, label, boyut):
        p = self.veri["profil"]
        img = None
        if p.get("avatar_yolu") and Path(p["avatar_yolu"]).exists():
            try: img = Image.open(p["avatar_yolu"]).convert("RGB")
            except Exception: img = None
        if img is None: img = sinematik_kapak_uret(p.get("ad", "A"), "Araçlar", (boyut, boyut))
        img = yuvarlak_maske(img, boyut)
        renk = CERCEVELER.get(p.get("cerceve", "mavi"), CERCEVELER["mavi"])["renk"]
        img = cerceve_ekle(img, renk, 5)
        try:
            ci = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            label._arda_ref = ci; label.configure(image=ci, text="")
        except Exception: pass

    def profil_duzenle(self):
        p = self.veri["profil"]
        win = ctk.CTkToplevel(self); win.title("Profili Düzenle"); win.geometry("620x800")
        win.configure(fg_color=RENKLER["arka"]); win.transient(self); win.grab_set()
        sc = ctk.CTkScrollableFrame(win, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=15, pady=15)
        def add_e(lbl, val):
            ctk.CTkLabel(sc, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=RENKLER["soluk"]).pack(anchor="w", pady=(6, 2))
            e = ctk.CTkEntry(sc, height=36, fg_color=RENKLER["kart"], text_color=RENKLER["metin"])
            e.pack(fill="x", pady=(0, 6)); e.insert(0, val); return e
        e_ad = add_e("Kullanıcı Adı:", p.get("ad", ""))
        e_bio = add_e("Biyografi:", p.get("biyografi", ""))
        ctk.CTkLabel(sc, text="Unvan:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=RENKLER["soluk"]).pack(anchor="w", pady=(6, 2))
        uv = ctk.StringVar(value=p.get("unvan", "Yeni Oyuncu"))
        ctk.CTkOptionMenu(sc, values=UNVANLAR, variable=uv,
                          fg_color=RENKLER["kart"]).pack(fill="x", pady=(0, 6))
        def kaydet():
            p["ad"] = e_ad.get() or "Oyuncu"; p["biyografi"] = e_bio.get()
            p["unvan"] = uv.get()
            save_json(DATA_DOSYASI, self.veri)
            self._rozet_ver("customizer"); self._xp_ver(20, "profil")
            win.destroy(); self.sayfa_degistir("profil"); self._profil_guncelle()
        ctk.CTkButton(sc, text="💾 Kaydet", height=44, fg_color=RENKLER["yesil"],
                      hover_color="#16A34A", command=kaydet).pack(fill="x", pady=15)

    def oyun_detay_goster(self, oid):
        self.secili_oyun = oid
        oyun = self.oyunlar[oid]
        # Scroll pozisyonunu kaydet
        try:
            self._scroll_kaydet(self.aktif_sayfa)
        except Exception:
            pass
        for w in self.icerik.winfo_children(): w.destroy()
        ctk.CTkButton(self.icerik, text="← Geri", width=80, fg_color="transparent",
                      hover_color=RENKLER["kart_hover"],
                      command=lambda: self.sayfa_degistir(self.aktif_sayfa)).grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        banner = ctk.CTkLabel(self.icerik, text="", height=220)
        banner.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        self.gorsel_yukle_guvenli(banner, oid, "detay_banner",
            oyun.get("banner_urls", oyun.get("kapak_urls", [])),
            (1080, 220), oyun["isim"], oyun["tur"], overlay=True)
        tr = ctk.CTkFrame(self.icerik, fg_color="transparent")
        tr.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        tr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tr, text=oyun["isim"], font=ctk.CTkFont(size=30, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=0, column=0, sticky="w")
        fav = self.veri["oyunlar"].get(oid, {}).get("favori", False)
        ctk.CTkButton(tr, text="❤️ Favori" if fav else "🤍 Favorile", width=140, height=34,
                      fg_color=RENKLER["yan"], hover_color=RENKLER["kart_hover"],
                      command=lambda: self.favori_degistir(oid, True)).grid(row=0, column=1, sticky="e")
        rg = toplam_ram_gb(); mr = oyun.get("min_ram", 2); uy = rg >= mr
        ctk.CTkLabel(self.icerik, text=f"{oyun['tur']} • {oyun.get('repo','')}",
                     font=ctk.CTkFont(size=12), text_color=RENKLER["soluk"]).grid(
            row=3, column=0, columnspan=4, sticky="w")
        ctk.CTkLabel(self.icerik,
                     text=f"{'✅ Uyumlu' if uy else '⚠️ RAM Yetersiz'} "
                          f"(Sizin: {rg:.1f} GB / Gerekli: {mr} GB)",
                     font=ctk.CTkFont(size=11),
                     text_color=RENKLER["yesil"] if uy else RENKLER["kirmizi"]).grid(
            row=4, column=0, columnspan=4, sticky="w", pady=(0, 15))
        ctk.CTkLabel(self.icerik, text="Açıklama", font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=RENKLER["metin"]).grid(row=5, column=0, columnspan=4, sticky="w")
        ctk.CTkLabel(self.icerik, text=oyun.get("aciklama", ""), wraplength=1000,
                     justify="left", font=ctk.CTkFont(size=13),
                     text_color=RENKLER["soluk"]).grid(row=6, column=0, columnspan=4,
                                                        sticky="w", pady=(0, 12))
        kurulu = self._kurulu_mu(oid, oyun)
        self.detay_bar = ctk.CTkProgressBar(self.icerik, height=10, progress_color=RENKLER["vurgu"])
        self.detay_bar.grid(row=9, column=0, columnspan=4, sticky="ew", pady=(5, 5)); self.detay_bar.set(0)
        self.detay_lbl = ctk.CTkLabel(self.icerik, text="Hazır", font=ctk.CTkFont(size=11),
                                       text_color=RENKLER["soluk"])
        self.detay_lbl.grid(row=10, column=0, columnspan=4, sticky="w", pady=(0, 10))
        br = ctk.CTkFrame(self.icerik, fg_color="transparent")
        br.grid(row=11, column=0, columnspan=4, sticky="ew"); br.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(br, text="▶ OYNA", height=48, font=ctk.CTkFont(size=16, weight="bold"),
                      fg_color=RENKLER["yesil"], hover_color="#16A34A",
                      command=lambda: self.oyna(oid),
                      state="normal" if kurulu else "disabled").grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(br, text="📥 İndir" if not kurulu else "🔄 Yeniden İndir", height=48,
                      font=ctk.CTkFont(size=16, weight="bold"), fg_color=RENKLER["vurgu"],
                      hover_color=RENKLER["vurgu_hover"],
                      command=lambda: self.indir(oid)).grid(row=0, column=1, padx=(8, 0), sticky="ew")
        if kurulu:
            ek = ctk.CTkFrame(self.icerik, fg_color="transparent")
            ek.grid(row=12, column=0, columnspan=4, sticky="ew", pady=(10, 15))
            ek.grid_columnconfigure((0,1,2,3), weight=1)
            for i, (t, cb) in enumerate([
                ("📂 Klasör Aç", lambda: self.klasor_ac(oid)),
                ("💾 Yedekle", lambda: self.yedekle(oid)),
                ("📦 Yedekten Yükle", lambda: self.yedekten_yukle(oid)),
                ("🖥️ Kısayol", lambda: self.kisayol(oid)),
            ]):
                ctk.CTkButton(ek, text=t, height=34, fg_color=RENKLER["yan"],
                              hover_color=RENKLER["kart_hover"], command=cb).grid(
                    row=0, column=i, padx=3, sticky="ew")
            ek2 = ctk.CTkFrame(self.icerik, fg_color="transparent")
            ek2.grid(row=13, column=0, columnspan=4, sticky="ew", pady=(0, 15))
            ek2.grid_columnconfigure((0,1), weight=1)
            ctk.CTkButton(ek2, text="🧩 Mod Yükle", height=34, fg_color=RENKLER["mor"],
                          hover_color="#7C3AED",
                          command=lambda: self.mod_yukle(oid)).grid(row=0, column=0, padx=(0,5), sticky="ew")
            ctk.CTkButton(ek2, text="🗑️ Kaldır", height=34, fg_color=RENKLER["kirmizi"],
                          hover_color="#DC2626",
                          command=lambda: self.oyun_kaldir(oid)).grid(row=0, column=1, padx=(5,0), sticky="ew")

    # ================================================================
    # FAVORİ DEĞİŞTİR — SCROLL KORUMALI
    # ================================================================
    def favori_degistir(self, oid, detail=False):
        v = self.veri["oyunlar"].setdefault(oid, {})
        v["favori"] = not v.get("favori", False)
        save_json(DATA_DOSYASI, self.veri)
        if detail and self.secili_oyun == oid:
            self.oyun_detay_goster(oid)
        else:
            # Mevcut scroll pozisyonunu kaydet
            try:
                saved_pos = self.icerik._parent_canvas.yview()[0]
            except Exception:
                saved_pos = 0.0
            # Sayfayı yeniden çiz (bu sayfa_degistir içinde otomatik
            # olarak kaydedilen konumu geri yüklemeye çalışır ama biz
            # yine de garantiye alalım)
            self.sayfa_degistir(self.aktif_sayfa)
            if saved_pos > 0.001:
                self.after(50, lambda p=saved_pos: self._scroll_geri_yukle(p))

    def indir(self, oid):
        self.indirme_yon.baslat(oid, self.oyunlar[oid])
        self._rozet_guncelle()
        if self.aktif_sayfa == "indirmeler": self._indirmeler()
    def detay_ilerleme(self, oid, y, h, i, t, e):
        if self.secili_oyun == oid and hasattr(self, "detay_bar"):
            try:
                self.detay_bar.set(y)
                et = f" • Kalan: {fmt_sure(e)}" if e > 0 else ""
                self.detay_lbl.configure(text=f"{fmt_bayt(i)}/{fmt_bayt(t)} • {h:.2f} MB/s • {y*100:.1f}%{et}")
            except Exception: pass
        if self.aktif_sayfa == "indirmeler":
            try: self._indirmeler()
            except Exception: pass
    def detay_durum_metni(self, oid, mesaj):
        if self.secili_oyun == oid and hasattr(self, "detay_lbl"):
            try: self.detay_lbl.configure(text=mesaj)
            except Exception: pass
    def indirme_basarili(self, oid, exe, asset):
        self.veri["oyunlar"].setdefault(oid, {})["exe_yolu"] = str(exe)
        self.veri["oyunlar"][oid]["asset"] = asset
        self.veri["indirme_sayaci"] = self.veri.get("indirme_sayaci", 0) + 1
        save_json(DATA_DOSYASI, self.veri)
        self._rozet_guncelle(); self._xp_ver(XP_ODULLERI["oyun_indir"], "oyun_indir")
        self._rozet_kontrol()
        if self.secili_oyun == oid: self.oyun_detay_goster(oid)
        else: self.sayfa_degistir(self.aktif_sayfa)
    def indirme_hatali(self, oid, hata):
        self._rozet_guncelle()
        isim = self.oyunlar.get(oid, {}).get("isim", oid)
        messagebox.showerror("İndirme Hatası", f"{isim}:\n{hata}")
    def _rozet_guncelle(self):
        n = len(self.indirme_yon.aktif)
        try:
            if n > 0: self.indirme_rozet.configure(text=str(n)); self.indirme_rozet.grid()
            else: self.indirme_rozet.grid_remove()
        except Exception: pass
    def oyna(self, oid):
        oyun = self.oyunlar[oid]
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
            self._xp_ver(XP_ODULLERI["oyun_baslat"], "oyun_baslat")
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
        save_json(DATA_DOSYASI, self.veri)
    def oyun_ekle(self):
        f = filedialog.askopenfilename(parent=self, title="EXE Seç",
                                        filetypes=[("Uygulamalar", "*.exe")])
        if not f: return
        self._oyun_ekle_otomatik(Path(f))
        self.sayfa_degistir("kutuphanem")
    def _oyun_ekle_otomatik(self, exe):
        isim = exe.stem; oid = isim.lower().replace(" ", "_").replace("-", "_"); s = 1
        while oid in self.oyunlar:
            oid = f"{isim.lower().replace(' ', '_')}_{s}"; s += 1
        yeni = {"isim": isim, "repo": "", "exe_adi": exe.name, "tur": "Araçlar",
                "aciklama": "Yerel olarak eklendi.", "sistem": "Bilinmiyor.",
                "min_ram": 0, "kapak_urls": [], "banner_urls": []}
        self.oyunlar[oid] = yeni; self.veri["eklenen_oyunlar"][oid] = yeni
        self.veri["oyunlar"].setdefault(oid, {})["exe_yolu"] = str(exe)
        save_json(DATA_DOSYASI, self.veri); self._rozet_kontrol()
    def klasor_ac(self, oid):
        exe = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        k = Path(exe).parent if exe and Path(exe).exists() else self.oyunlar_dizini / oid
        self._dizin_ac(k)
    def yedekle(self, oid):
        exe = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if not exe or not Path(exe).exists():
            messagebox.showerror("Hata", "Oyun klasörü yok."); return
        kaynak = Path(exe).parent
        try: self.yedek_dizini.mkdir(parents=True, exist_ok=True)
        except Exception as e: messagebox.showerror("Hata", str(e)); return
        hedef = self.yedek_dizini / f"{oid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        try:
            with zipfile.ZipFile(hedef, "w", zipfile.ZIP_DEFLATED) as zf:
                for p in kaynak.rglob("*"):
                    if p.is_file() and p.stat().st_size < 50*1024*1024:
                        try: zf.write(p, p.relative_to(kaynak))
                        except Exception: pass
            self._xp_ver(XP_ODULLERI["yedekle"], "yedek"); self._rozet_ver("safe_player")
            messagebox.showinfo("Başarılı", f"Yedek:\n{hedef}")
        except Exception as e: messagebox.showerror("Hata", str(e))
    def yedekten_yukle(self, oid):
        f = filedialog.askopenfilename(parent=self, initialdir=str(self.yedek_dizini),
                                        filetypes=[("ZIP", "*.zip")])
        if not f: return
        exe = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if not exe or not Path(exe).exists():
            messagebox.showerror("Hata", "Oyun klasörü yok."); return
        try:
            with zipfile.ZipFile(f, "r") as zf: zf.extractall(Path(exe).parent)
            messagebox.showinfo("Başarılı", "Geri yüklendi.")
        except Exception as e: messagebox.showerror("Hata", str(e))
    def mod_yukle(self, oid):
        f = filedialog.askopenfilename(parent=self, title="Mod dosyası")
        if not f: return
        hedef = MODS_DIR / oid; hedef.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(f, hedef / Path(f).name)
            messagebox.showinfo("Başarılı", f"Mod: {Path(f).name}")
        except Exception as e: messagebox.showerror("Hata", str(e))
    def kisayol(self, oid):
        exe = self.veri["oyunlar"].get(oid, {}).get("exe_yolu")
        if not exe or not Path(exe).exists():
            messagebox.showerror("Hata", "Oyun dosyası yok."); return
        if sys.platform != "win32":
            messagebox.showinfo("Bilgi", "Windows."); return
        try:
            masa = win_desktop_path()
            lnk = masa / f"{self.oyunlar[oid]['isim']}.lnk"
            ps = (f'$W=New-Object -ComObject WScript.Shell;$S=$W.CreateShortcut("{lnk}");'
                  f'$S.TargetPath="{exe}";$S.WorkingDirectory="{Path(exe).parent}";$S.Save()')
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True,
                           capture_output=True, timeout=15)
            messagebox.showinfo("Başarılı", f"Kısayol:\n{lnk}")
        except Exception as e: messagebox.showerror("Hata", str(e))

    KOTU = {"unins","uninstall","setup","installer","dxsetup","vcredist","vc_redist","vcrun",
            "dotnet","directx","dxwebsetup","dxupdate","crashhandler","crashreport",
            "unitycrashhandler","helper","repair","configure","updater","patcher","cleanup",
            "activation","activate","register","reinstall","redist","bootstrap","prereq",
            "prerequisites","easyanticheat","eac_","battleye","steam_api","steamclient",
            "codec","diagnostic","benchmark","config","uninstal","report","tool","cmd"}
    ATLA = {".git",".svn","node_modules","__pycache__","cache","temp","tmp","$recycle.bin",
            "system volume information","windows","system32","syswow64","microsoft","recovery"}
    def _tara(self, kok):
        adaylar = []
        for root, dirs, files in os.walk(kok):
            dirs[:] = [d for d in dirs if d.lower() not in self.ATLA]
            for f in files:
                if not f.lower().endswith(".exe"): continue
                if any(b in f[:-4].lower() for b in self.KOTU): continue
                p = Path(root) / f
                try:
                    if p.stat().st_size < 100 * 1024: continue
                except Exception: continue
                adaylar.append(p)
        gruplar = defaultdict(list)
        for e in adaylar: gruplar[e.parent].append(e)
        sonuc = []
        for exes in gruplar.values():
            exes.sort(key=lambda x: x.stat().st_size, reverse=True)
            sonuc.append(exes[0])
            for e in exes[1:]:
                try:
                    if e.stat().st_size > 100*1024*1024: sonuc.append(e)
                except Exception: pass
        return sonuc
    def klasor_tara(self):
        k = filedialog.askdirectory(parent=self, title="Oyun klasörü")
        if not k: return
        self.durum("Taranıyor...")
        threading.Thread(target=lambda: self.after(0, lambda: self._tarama_sonuc(self._tara(Path(k)))),
                          daemon=True).start()
    def hizli_tara(self):
        pf = os.environ.get("ProgramFiles", "C:/Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")
        adaylar = [Path(pf)/"Steam"/"steamapps"/"common", Path(pf86)/"Steam"/"steamapps"/"common",
                   Path(pf86)/"Epic Games", Path("C:/Games"), Path("D:/Games"), Path("D:/Oyunlar")]
        mevcut = [d for d in adaylar if d.exists()]
        if not mevcut:
            messagebox.showinfo("Sonuç", "Klasör bulunamadı."); return
        def run():
            tum = []
            for k in mevcut:
                try: tum.extend(self._tara(k))
                except Exception: pass
            self.after(0, lambda: self._tarama_sonuc(tum))
        threading.Thread(target=run, daemon=True).start()
    def _tarama_sonuc(self, adaylar):
        self._xp_ver(XP_ODULLERI["tarama"], "tarama"); self._rozet_ver("explorer")
        if not adaylar:
            messagebox.showinfo("Sonuç", "Oyun bulunamadı."); return
        mevcut = {str(Path(v.get("exe_yolu", "")).resolve()).lower()
                  for v in self.veri["oyunlar"].values() if v.get("exe_yolu")}
        yeniler = [a for a in adaylar if str(a.resolve()).lower() not in mevcut]
        if not yeniler:
            messagebox.showinfo("Sonuç", "Zaten kütüphanede."); return
        win = ctk.CTkToplevel(self); win.title("Bulunan Oyunlar"); win.geometry("750x600")
        win.configure(fg_color=RENKLER["arka"]); win.transient(self); win.grab_set()
        sc = ctk.CTkScrollableFrame(win, fg_color=RENKLER["kart"])
        sc.pack(fill="both", expand=True, padx=20, pady=10)
        secim = {}
        for exe in yeniler:
            try: b = fmt_bayt(exe.stat().st_size)
            except Exception: b = "?"
            v = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(sc, text=f"  {exe.stem} — {b}\n  {exe.parent}",
                            variable=v, font=ctk.CTkFont(size=12),
                            text_color=RENKLER["metin"], fg_color=RENKLER["vurgu"]).pack(
                anchor="w", padx=10, pady=6)
            secim[exe] = v
        def ekle():
            n = 0
            for exe, v in secim.items():
                if v.get(): self._oyun_ekle_otomatik(exe); n += 1
            win.destroy(); self.sayfa_degistir("kutuphanem")
        ctk.CTkButton(win, text="Seçilenleri Ekle", height=40, fg_color=RENKLER["yesil"],
                      command=ekle).pack(pady=15)


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ArdaLauncher.ZeroBug.8")
        except Exception: pass
    app = ArdaLauncher()
    app.mainloop()