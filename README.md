<div align="center">
  <h1>🚀 ARDA LAUNCHER v12.4</h1>
  <p>
    <strong>A modern, lightweight, and multi-language game launcher built with Python & CustomTkinter.</strong>
  </p>
</div>

---

## 📖 About

**ARDA LAUNCHER v12.4** is a sleek Windows desktop game hub designed to discover, download, and manage **115+ free-to-play and open-source games** from a single interface. Featuring direct GitHub release downloads with resume support, Steam library integration, daily rewards, and a zero-setup one-click Windows installer, it delivers a complete launcher experience without heavy background bloat.

---

## ✨ Key Features

* 🎮 **115+ Free Games Catalog:** Browse open-source GitHub releases, free-to-play Steam titles, and standalone web games in one place.
* ⬇️ **Smart Download Manager:** Multi-threaded HTTPS downloads from GitHub Releases with pause, resume (`Range` requests), cancel, and real-time speed tracking.
* 🔗 **Steam Integration:** Automatically detects your local Steam installation, checks installed games, and triggers one-click Steam installs (`steam://install/`).
* 🌍 **12 Languages Supported:** Auto-detects system language with full UI support for English, Türkçe, Deutsch, Français, Español, Italiano, Português, Русский, 中文, 日本語, 한국어, and العربية.
* 🎡 **Gamification & Cosmetic Shop:** Spin the Daily Wheel, complete daily tasks, earn 💎 credits, and unlock profile banners.
* ⚡ **Built-in Utilities:** Includes a safe Game Booster, Windows startup toggle, desktop shortcut generator, JSON data backup/restore, and SHA-256 verified auto-updates.
* 🛠️ **Developer Console:** Built-in authenticated developer workspace with Windows DPAPI token encryption for managing repository files and atomic branch syncing.

---

## 📥 Quick Installation (All-in-One)

You don't need to install Python or any dependencies manually. The installer script handles everything automatically:

1. Download **`ArdaLauncherInstaller.bat`** from this repository.
2. Double-click **`ArdaLauncherInstaller.bat`**.
3. The installer will automatically:
   * Check for **Python 3.10+** and install **Python 3.13** silently if it is missing.
   * Install all required packages (`customtkinter`, `Pillow`, `requests`, `psutil`).
   * Download the latest `ArdaLauncher.pyw` into `%LOCALAPPDATA%\ArdaLauncher` and verify its **SHA-256** checksum.
   * Launch **ARDA LAUNCHER** automatically when finished.

> 💡 **Tip:** You can also run `ArdaLauncherInstaller.bat` anytime to update your existing installation to the latest version.

---

## 📂 Repository Structure

* `ArdaLauncherInstaller.bat` – All-in-one automatic Windows installer and updater.
* `ArdaLauncher.pyw` – Main console-free GUI application.
* `version.json` – Release metadata and SHA-256 verification hash.
* `GITHUB_RELEASE_NOTES_EN.txt` – Version changelog and release details.

---

## 💻 System Requirements

* **OS:** Windows 10 / Windows 11 (64-bit)
* **Internet Connection:** Required for automatic setup, game downloads, and updates

---

## 📝 Release Notes & Feedback

* Check [`GITHUB_RELEASE_NOTES_EN.txt`](GITHUB_RELEASE_NOTES_EN.txt) for full version history.
* Found a bug or have a suggestion? Open an [Issue](https://github.com) or use the in-app **Report / Suggest** button.
