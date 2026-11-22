<div align="center">

# ⚡ Arda Launcher

**Discover, download, organize and launch free games from one place.**

A Windows desktop game launcher for Steam, GitHub and official game websites.

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D4?logo=windows&logoColor=white)](https://github.com/ardafatih707-coder/Game-Launcher)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Stars](https://img.shields.io/github/stars/ardafatih707-coder/Game-Launcher?style=flat&logo=github)](https://github.com/ardafatih707-coder/Game-Launcher/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/ardafatih707-coder/Game-Launcher?logo=git&logoColor=white)](https://github.com/ardafatih707-coder/Game-Launcher/commits/main)

[📥 Download ZIP](https://github.com/ardafatih707-coder/Game-Launcher/archive/refs/heads/main.zip) ·
[🐛 Report a Bug](https://github.com/ardafatih707-coder/Game-Launcher/issues)

</div>

---

## 📖 About

**Arda Launcher** is a single-file Python application (`ArdaLauncher.pyw`). It presents a catalogue of more than 100 free games in a modern dark interface. Add games to your library, mark favorites, group them into collections, and launch them with one click.

The interface is built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). No server is required, and your data stays on your computer.

## ✨ Features

### 🎮 Game catalogue
- Free games distributed through Steam, GitHub and official websites
- Search, filter and sort by name, genre and source (Steam / GitHub / Official Site)
- Steam cover art is downloaded automatically, with a generated local fallback if none is available
- Random game picker and a detailed game window

### 📚 Library and organization
- **Library**, **Favorites** and **Wishlist**
- **Collections:** group your games into your own lists
- Per-game **notes** and a launch counter
- Link your own `.exe` / `.lnk` file to a game and start it directly
- **Activity** page with your local event history

### ⬇️ Download manager
- Downloads open-source games from GitHub Releases and picks the Windows-compatible file
- Pause, resume and cancel; interrupted downloads continue where they stopped
- Bulk actions: pause all, resume all, cancel all, retry failed
- Files are verified with SHA-256 when the publisher provides a checksum
- Downloads only from HTTPS and trusted GitHub addresses
- For Steam games, installation is handed over to Steam (`steam://install/`), and installed games can be launched from the launcher

### 👥 Social and profile
- Profile with username, tag, title, bio, avatar and banner theme
- Achievements, tasks, a daily wheel and a cosmetic shop (in-app credits)
- Optional **friends system:** send, accept and decline requests with player codes (requires your own Firebase Realtime Database project)

### 🌍 Languages
Türkçe, English, Deutsch, Français, Español, Italiano, Português, Русский, 中文, 日本語, 한국어 and العربية.

The language is selected automatically from your Windows country/region setting. No location access is requested. You can also change it manually in Settings.

### 🛠 Maintenance and settings
- Move the data folder to another location (copied and verified)
- JSON backup and restore, library export to CSV
- Diagnostics scan, error log and cleanup of incomplete downloads
- Start with Windows and create a desktop shortcut
- Theme (dark / light / system), card size, sound and notification settings
- **Full uninstall** option that requires a typed confirmation phrase

### 🔔 Update notifications
On startup and every 6 hours, the launcher reads this repository's public `version.json` file. If a newer version is available, it shows a notification in your selected language.

## 📥 Installation

No installer is needed. Download the project from GitHub and extract it with WinRAR.

**1. Install Python**

Download Python 3.10 or newer from [python.org](https://www.python.org/downloads/). During setup, check **Add python.exe to PATH**.

**2. Download the project**

On this page, click the green **`<> Code`** button, then click **Download ZIP**.
You can also [download it directly](https://github.com/ardafatih707-coder/Game-Launcher/archive/refs/heads/main.zip).

**3. Extract it with WinRAR**

Right-click the downloaded `Game-Launcher-main.zip`, then choose **WinRAR → Extract to "Game-Launcher-main\"**.

**4. Install the required packages**

Open the extracted folder. Click the address bar in File Explorer, type `cmd` and press Enter. Then run:

```bash
python -m pip install customtkinter Pillow requests psutil
```

**5. Start the launcher**

Double-click `ArdaLauncher.pyw`.

If nothing opens, run this in the same Command Prompt window to see the error message:

```bash
python ArdaLauncher.pyw
```

> 💡 **Tip:** After the first start, open **Settings → Maintenance → Create Shortcut** to add an **Arda Launcher** shortcut to your desktop.

### Updating

Download the latest ZIP again with **Code → Download ZIP** and extract it over the old folder with WinRAR. Your library, favorites and settings are stored separately (see [Data location](#-data-location)), so they are kept.

### Using Git instead

```bash
git clone https://github.com/ardafatih707-coder/Game-Launcher.git
cd Game-Launcher
python -m pip install customtkinter Pillow requests psutil
python ArdaLauncher.pyw
```

## 💻 Requirements

| Requirement | Details |
|---|---|
| Operating system | Windows 10 / 11 |
| Python | 3.10 or newer |
| Packages | `customtkinter`, `Pillow`, `requests`, `psutil` |
| Internet | For cover art, downloads and update checks |
| Steam | Only for Steam games (optional) |

## ⌨️ Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl` + `K` | Focus the search box |
| `Ctrl` + `L` | Open Library |
| `Ctrl` + `F` | Open Favorites |
| `Ctrl` + `J` | Open Activity |
| `Ctrl` + `Shift` + `R` | Random game |
| `F5` | Refresh the page |

## 🔒 Privacy and security

- Your profile, library, favorites, notes and settings are stored **only on your computer**.
- Stored secrets (for example the friends-service session) are encrypted with **Windows DPAPI**.
- Downloads use HTTPS and trusted GitHub addresses only. File names and archive paths pass through safety checks.
- Backups do not contain tokens or session credentials.
- If you do not use the friends system, no online account is created.

## 🗂 Data location

By default, your data is stored in `%LOCALAPPDATA%\ArdaLauncher`. You can move it to another location in **Settings → Directory & Storage**.

## 🤝 Feedback and contributing

For bug reports, suggestions or new game requests, use the [Issues](https://github.com/ardafatih707-coder/Game-Launcher/issues) page. The **Report / Suggest** button inside the launcher also opens the feedback form.

To contribute, fork the repository and open a pull request.

## ⚠️ Disclaimer

Arda Launcher is an independent project. It is not affiliated with Valve/Steam or with the publishers of the listed games. Game names and images belong to their respective owners. Steam games are obtained through Steam, open-source games from their own GitHub repositories, and the rest from their official websites.
