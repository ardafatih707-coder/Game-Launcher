# ⚡ ARDA LAUNCHER

**ARDA LAUNCHER** is a modern Windows game launcher that brings together 105+ free and open-source games in a single interface, featuring Steam integration and direct GitHub download support.

---

## 🛠️ Installation and Running

### Option 1: Automatic Installation (If Python is NOT Installed - Recommended)
If you do not have Python or the required libraries installed on your PC, you can set everything up automatically with one click:

1. Download the **`ArdaLauncherInstaller.bat`** file from this repository.
2. Double-click the downloaded **`ArdaLauncherInstaller.bat`** file to run it.
3. The installer wizard will automatically:
   * Install a compatible Python version on your system,
   * Install all required Python dependencies (`customtkinter`, `Pillow`, `requests`, `psutil`),
   * Download the latest launcher file, verify its SHA-256 checksum, and launch the application automatically.

### Option 2: Direct Launch (If Python is Already Installed)
If you already have **Python 3.10 or newer** installed on your PC:

1. Download the **`ArdaLauncher.pyw`** file from this repository.
2. If the required packages are not installed yet, run the following command once in Command Prompt (CMD):
   ```bash
   pip install customtkinter Pillow requests psutil
   ```
3. Double-click **`ArdaLauncher.pyw`** to start the launcher directly.

---

## ✨ Key Features

* **Extensive Game Catalog:** 105+ free games across FPS, RPG, Strategy, MMO, Racing, Co-op, and Open Source genres.
* **Multi-Source Support:**
  * **GitHub Integration:** Downloads and manages the latest releases of open-source games directly from GitHub (with pause, resume, and partial download recovery support).
  * **Steam Synchronization:** Automatically detects installed Steam games and triggers installations directly through Steam.
* **Gamification & Profile Customization:**
  * **Daily Spin & Tasks:** Earn credits by completing daily login, download, and library milestones.
  * **Cosmetic Shop & Profile:** Spend your credits on cosmetic items; customize your username, tag, avatar, and banner theme.
* **Advanced Storage & Data Management:**
  * Safely migrate your game data, cover art, and settings to another drive or folder with full integrity verification.
  * One-click JSON backup, cache clearing, and desktop shortcut creation.
* **Performance & System Utilities:**
  * **Game Booster:** Safely terminates unnecessary background processes to improve gaming performance.
  * **Multi-Language Support:** Supports 12 languages including English and Turkish (automatically detects your system language).
  * **Theme Options:** Dark, Light, and System themes with adjustable game card sizes.

---

## ⌨️ Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + K` | Focus the game search bar |

---

## 🤝 Feedback & Bug Reports

You can share your suggestions or report issues using the **"Report / Suggest"** button inside the app or via [this form](https://google.com).
