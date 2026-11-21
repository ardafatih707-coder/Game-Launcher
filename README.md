<div align="center">
  <h1>🚀 ArdaLauncher</h1>
  <p>
    <strong>A fast, lightweight, and auto-installing game launcher built with Python.</strong>
  </p>
</div>

---

## 📖 About

**ArdaLauncher** is a lightweight and user-friendly game launcher developed with Python (`.pyw`) to help you easily manage and launch your games from a single hub. With its one-click installer script and version tracking system, it ensures your setup stays clean and up to date.

## ✨ Features

* ⚡ **One-Click Auto Installation:** Effortlessly set up required dependencies using `ArdaLauncherInstaller.bat`.
* 🔄 **Smart Version Tracking:** Automatically monitors updates via the `version.json` configuration.
* 🖥️ **Console-Free Execution:** Runs with the `.pyw` extension so the interface opens directly without a background command prompt window.
* 🎮 **Fast & Lightweight:** Provides instant access to your games without draining system resources.

## 📂 File Structure

* `ArdaLauncher.pyw` – Main launcher interface and executable script.
* `ArdaLauncherInstaller.bat` – Windows batch script that automatically installs dependencies and sets up the environment.
* `version.json` – Configuration file storing current version metadata.
* `GITHUB_RELEASE_NOTES_EN.txt` – Release notes and changelog.

## 📥 Installation & Usage

### 1. Quick Setup (Recommended)
1. Download or clone this repository:
   ```bash
   git clone https://github.com
   ```
2. Double-click **`ArdaLauncherInstaller.bat`** inside the folder to run the setup.
3. Once completed, launch **`ArdaLauncher.pyw`** to start the application.

### 2. Manual Run
If you already have Python installed, you can start it directly via terminal:
```bash
cd Game-Launcher
pythonw ArdaLauncher.pyw
```

## 💻 Requirements

* **Operating System:** Windows 10 / 11
* **Software:** Python 3.8 or higher *(The installer script handles missing dependencies)*

## 📝 Release Notes

Check out [`GITHUB_RELEASE_NOTES_EN.txt`](GITHUB_RELEASE_NOTES_EN.txt) in this repository or visit the [Releases](https://github.com) page for the latest updates and changes.

## 🤝 Contributing

Feel free to open an [Issue](https://github.com) for bug reports and feature requests, or submit a Pull Request.
