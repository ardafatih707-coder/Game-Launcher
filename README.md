# 🚀 ARDA LAUNCHER

**ARDA LAUNCHER** is a modern, fast, lightweight, and feature-rich open-source **Desktop Game Launcher & Library Manager** for Windows. Built with Python and CustomTkinter, it combines sleek dark-mode aesthetics with a smart GitHub release downloader, automatic local game scanner, save backup manager, and deep player profile customization.

---

## ✨ Key Features

### 🎮 Store & Smart Download Engine
- **Curated Free & Open-Source Catalog:** Browse and install 14+ popular open-source PC games (*Mindustry, OpenRA, SuperTuxKart, Endless Sky, The Battle for Wesnoth, Shattered Pixel Dungeon, OpenTTD, Warzone 2100, Cataclysm: DDA, Tales of Maj'Eyal, Unciv, Veloren, 0 A.D., DDNet*).
- **Zero-Broken-Link GitHub Resolver:** Automatically fetches the latest Windows release archive directly from official GitHub repositories—never suffers from outdated or dead download links.
- **Pause, Resume & Speed Limiter:** Full HTTP Range support allows pausing and resuming downloads anytime, with real-time download speed (`MB/s`), progress bar, ETA, and optional bandwidth throttling.
- **Auto-Extraction:** Automatically extracts `.zip` and `.7z` archives and detects the main game executable.

### 📚 Library & Game Management Tools
- **Smart Folder Scanner:** Automatically scans your drives or existing game folders (Steam, Epic Games, custom folders), filters out uninstallers/redistributables, and imports your installed games in one click.
- **Playtime & Activity Tracker:** Tracks total playtime and daily gaming statistics automatically while you play.
- **Save Game Backup & Restore:** One-click `.zip` backup and restoration for your game files.
- **Mod & Addon Loader:** Easily import custom mods and plugins per game.
- **Game Booster Mode:** Launches games with High CPU Priority (`HIGH_PRIORITY_CLASS`) and optionally minimizes the launcher.
- **System Compatibility Check:** Automatically checks your system RAM against game requirements.

### 👤 Player Profile & Customization
- **Custom Identity:** Upload a custom avatar and profile banner, choose from 5 glowing neon avatar frames, and set your custom player title, bio, and online status.
- **XP, Leveling & Achievements:** Earn XP by installing games, playing, backing up saves, and scanning folders to level up and unlock achievement badges.
- **Live Theme Engine:** Switch accent colors on the fly (*Galaxy Purple, Electric Blue, Emerald Green, Cyber Purple, Flame Orange, Ruby Red, Gold*).

### 🔄 Built-in Self Auto-Updater
- Automatically checks for new versions on startup and updates itself in one click without requiring manual re-downloads.

---

## ⚡ Quick Installation (Recommended — One-Click Setup)

You do **not** need to install Python or any dependencies manually. The automated installer handles everything for you:

1. Click on **[`ArdaLauncher_Installer.bat`](https://githubusercontent.com)** in this repository (or download it directly).
2. Double-click **`ArdaLauncher_Installer.bat`**.
3. The installer will automatically:
   - Check for Python 3.12+ (and install it silently via Windows `winget` if missing).
   - Install all required libraries (`customtkinter`, `requests`, `pillow`, `psutil`, `py7zr`).
   - Download the latest **`launcher.pyw`** into `%LOCALAPPDATA%\ArdaLauncher`.
   - Launch **ARDA LAUNCHER** and create a custom neon **Desktop Shortcut**.

---

## 🛠️ Manual Installation (For Advanced Users)

If you already have **Python 3.10+** installed on Windows:

1. Download **`launcher.pyw`** from this repository.
2. Open Command Prompt / PowerShell and install the required packages:
   ```bash
   pip install customtkinter requests pillow psutil py7zr
   ```
3. Double-click **`launcher.pyw`** to run the application without a console window.

---

## 💻 System Requirements
- **OS:** Windows 10 / Windows 11 (64-bit)
- **Python:** Python 3.10 or newer (automatically installed by `ArdaLauncher_Installer.bat`)
- **Storage:** ~50 MB for the launcher + space for your downloaded games
- **Internet:** Required for downloading games, cover art, and automatic updates

---

## 🤝 Contributing & Feedback
Found a bug or want to suggest a new open-source game for the catalog? Feel free to open an **Issue** in this repository!
