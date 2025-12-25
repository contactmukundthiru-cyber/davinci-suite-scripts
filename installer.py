#!/usr/bin/env python3
"""
Resolve Production Suite - Universal Installer

A cross-platform installer that works in console mode.
No external dependencies required - works with any Python 3.9+

For standalone distribution, build with:
    pip install pyinstaller
    pyinstaller --onefile --console --name=ResolveProductionSuite-Setup installer.py
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
import webbrowser
import zipfile
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

VERSION = "0.3.0"
MIN_PYTHON = (3, 9)
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# GitHub repository for updates
GITHUB_USER = "contactmukundthiru-cyber"
GITHUB_REPO = "davinci-suite-scripts"

# Update check URLs
VERSION_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
GUMROAD_URL = "https://mukundthiru.gumroad.com/l/resolve-production-suite"

# When running as PyInstaller bundle, get the temp extraction directory
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    INSTALL_SOURCE = BUNDLE_DIR
else:
    BUNDLE_DIR = Path(__file__).parent.resolve()
    INSTALL_SOURCE = BUNDLE_DIR


# =============================================================================
# Console Helpers
# =============================================================================

class Colors:
    if IS_WINDOWS:
        # Enable ANSI on Windows
        os.system('')

    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def clear_screen():
    os.system('cls' if IS_WINDOWS else 'clear')


def print_header():
    clear_screen()
    print(f"{Colors.CYAN}")
    print("=" * 60)
    print("      RESOLVE PRODUCTION SUITE INSTALLER")
    print(f"              Version {VERSION}")
    print("=" * 60)
    print(f"{Colors.END}")
    print()


def print_step(msg):
    print(f"{Colors.BLUE}[*]{Colors.END} {msg}")


def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}[!]{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}[X]{Colors.END} {msg}")


def prompt(msg, default="y"):
    hint = "[Y/n]" if default.lower() == "y" else "[y/N]"
    response = input(f"{msg} {hint}: ").strip().lower()
    if not response:
        response = default.lower()
    return response == "y"


def prompt_choice(msg, options):
    print(f"\n{msg}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print()
    while True:
        try:
            choice = int(input("Enter choice: "))
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def wait_for_key():
    if IS_WINDOWS:
        os.system('pause')
    else:
        input("\nPress Enter to continue...")


# =============================================================================
# Updater
# =============================================================================

def parse_version(version_str):
    """Parse version string into comparable tuple."""
    try:
        clean = version_str.strip().split("-")[0]
        return tuple(int(p) for p in clean.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_update_info():
    """Get update information from GitHub."""
    # Try version.json first (faster, simpler)
    try:
        req = urllib.request.Request(
            VERSION_CHECK_URL,
            headers={"User-Agent": "ResolveProductionSuite-Installer"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                "version": data.get("version", "0.0.0"),
                "changelog": data.get("changelog", ""),
                "download_url": data.get("download_url"),
                "windows_url": data.get("windows_url"),
                "macos_url": data.get("macos_url"),
            }
    except Exception:
        pass

    # Fallback to GitHub Releases API
    try:
        req = urllib.request.Request(
            RELEASES_API_URL,
            headers={"User-Agent": "ResolveProductionSuite-Installer"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            version = data.get("tag_name", "0.0.0").lstrip("v")
            changelog = data.get("body", "")

            # Find platform-specific download
            assets = data.get("assets", [])
            windows_url = None
            macos_url = None
            for asset in assets:
                name = asset.get("name", "").lower()
                url = asset.get("browser_download_url")
                if "windows" in name:
                    windows_url = url
                elif "macos" in name or "mac" in name:
                    macos_url = url

            return {
                "version": version,
                "changelog": changelog,
                "download_url": data.get("html_url"),
                "windows_url": windows_url,
                "macos_url": macos_url,
            }
    except Exception:
        return None


def check_for_updates():
    """Check if updates are available."""
    print_step("Checking for updates...")

    info = get_update_info()
    if not info:
        print_warning("Could not check for updates (no internet connection)")
        return False, None, None

    remote_version = info["version"]
    local = parse_version(VERSION)
    remote = parse_version(remote_version)

    if remote > local:
        print()
        print(f"{Colors.YELLOW}Update available!{Colors.END}")
        print(f"  Current version: {VERSION}")
        print(f"  Latest version:  {remote_version}")
        if info.get("changelog"):
            print(f"\nChangelog:\n{info['changelog'][:500]}")
        print()
        return True, remote_version, info
    else:
        print_success(f"You have the latest version ({VERSION})")
        return False, remote_version, info


def download_file(url, dest_path, desc="Downloading"):
    """Download a file with progress indication."""
    print_step(f"{desc}...")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ResolveProductionSuite-Installer"})
        with urllib.request.urlopen(req, timeout=60) as response:
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            block_size = 8192

            with open(dest_path, 'wb') as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded * 100 / total)
                        print(f"\r  Progress: {pct}% ({downloaded // 1024}KB / {total // 1024}KB)", end="", flush=True)

            print()  # New line after progress
            print_success("Download complete!")
            return True
    except Exception as e:
        print_error(f"Download failed: {e}")
        return False


def apply_update(zip_path, install_dir):
    """Extract and apply update from zip file."""
    print_step("Applying update...")

    try:
        # Create backup of current installation
        backup_dir = install_dir.parent / f"{install_dir.name}_backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        # Extract to temp location first
        temp_extract = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_extract)

        # Find the actual content directory (might be nested)
        content_dir = temp_extract
        subdirs = list(temp_extract.iterdir())
        if len(subdirs) == 1 and subdirs[0].is_dir():
            content_dir = subdirs[0]

        # Backup current installation
        if install_dir.exists():
            shutil.move(str(install_dir), str(backup_dir))

        # Copy new files
        shutil.copytree(content_dir, install_dir)

        # Restore venv if it existed
        venv_backup = backup_dir / ".venv"
        if venv_backup.exists():
            shutil.move(str(venv_backup), str(install_dir / ".venv"))

        # Clean up
        shutil.rmtree(temp_extract)
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        print_success("Update applied successfully!")
        return True

    except Exception as e:
        print_error(f"Failed to apply update: {e}")
        # Try to restore backup
        if backup_dir.exists() and not install_dir.exists():
            shutil.move(str(backup_dir), str(install_dir))
            print_warning("Restored from backup")
        return False


def run_updater():
    """Run the updater interface."""
    print_header()
    print("UPDATE CHECKER\n")

    update_available, remote_version, info = check_for_updates()

    if not update_available:
        print("\nNo updates available.")
        wait_for_key()
        return

    # Determine which download URL to use
    if IS_WINDOWS:
        auto_url = info.get("windows_url")
        platform_name = "Windows"
    elif IS_MACOS:
        auto_url = info.get("macos_url")
        platform_name = "macOS"
    else:
        auto_url = None
        platform_name = "your platform"

    print("\nUpdate options:")
    print("  1. Auto-update (download and install automatically)")
    print("  2. Open download page in browser")
    print("  3. Cancel")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        if auto_url:
            # Auto-download and install
            with tempfile.TemporaryDirectory() as tmp:
                zip_path = Path(tmp) / f"update-{remote_version}.zip"
                if download_file(auto_url, zip_path, f"Downloading {platform_name} update"):
                    # Find existing installation
                    if IS_WINDOWS:
                        install_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ResolveProductionSuite"
                    else:
                        install_dir = Path.home() / ".local" / "share" / "resolve-production-suite"

                    if install_dir.exists():
                        if apply_update(zip_path, install_dir):
                            print()
                            print(f"{Colors.GREEN}Updated to version {remote_version}!{Colors.END}")
                            print("\nPlease restart the application to use the new version.")
                    else:
                        print_warning("No existing installation found.")
                        print("Please run the full installation instead.")
        else:
            print_warning(f"Auto-update not available for {platform_name}")
            print("Opening download page instead...")
            webbrowser.open(info.get("download_url", GUMROAD_URL))

    elif choice == "2":
        url = info.get("download_url", GUMROAD_URL)
        print_step("Opening download page...")
        webbrowser.open(url)
        print_success("Download page opened in browser")

    wait_for_key()


# =============================================================================
# Installation Logic
# =============================================================================

def get_install_dir():
    """Get the installation directory."""
    if IS_WINDOWS:
        default = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ResolveProductionSuite"
    else:
        default = Path.home() / ".local" / "share" / "resolve-production-suite"

    print(f"\nInstallation directory: {default}")
    if prompt("Use this location?"):
        return default

    custom = input("Enter custom path: ").strip()
    return Path(custom) if custom else default


def get_data_dir():
    """Get the data directory for logs, reports, etc."""
    return Path.home() / ".rps"


def detect_resolve():
    """Detect DaVinci Resolve installation."""
    paths = []

    if IS_LINUX:
        paths = [
            "/opt/resolve/Developer/Scripting/Modules",
            "/opt/blackmagic/DaVinci Resolve/Developer/Scripting/Modules"
        ]
    elif IS_MACOS:
        paths = [
            "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
        ]
    elif IS_WINDOWS:
        paths = [
            r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting\Modules"
        ]

    # Check environment variable first
    env_path = os.environ.get("RESOLVE_SCRIPT_API", "")
    if env_path and Path(env_path).exists():
        return env_path

    # Check common paths
    for p in paths:
        if Path(p).exists():
            return p

    return None


def copy_files(src_dir, dest_dir):
    """Copy installation files."""
    dirs_to_copy = ["core", "resolve", "tools", "cli", "ui", "schemas", "presets", "scripts", "sample_data", "docs"]
    files_to_copy = ["VERSION", "README.md", "LICENSE", "requirements.txt", "pyproject.toml"]

    dest_dir.mkdir(parents=True, exist_ok=True)

    for d in dirs_to_copy:
        src = src_dir / d
        if src.exists():
            dest = dest_dir / d
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            print_success(f"Copied {d}/")

    for f in files_to_copy:
        src = src_dir / f
        if src.exists():
            shutil.copy2(src, dest_dir / f)
            print_success(f"Copied {f}")


def create_venv(install_dir):
    """Create virtual environment."""
    venv_dir = install_dir / ".venv"

    if venv_dir.exists():
        if prompt("Virtual environment exists. Recreate?", "n"):
            shutil.rmtree(venv_dir)
        else:
            return venv_dir

    print_step("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    print_success("Virtual environment created")

    return venv_dir


def get_pip(venv_dir):
    """Get pip executable path."""
    if IS_WINDOWS:
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def get_python(venv_dir):
    """Get python executable path."""
    if IS_WINDOWS:
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def install_dependencies(venv_dir, install_dir, install_ui=True):
    """Install Python dependencies."""
    pip = get_pip(venv_dir)

    print_step("Upgrading pip...")
    subprocess.run([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel", "-q"], check=True)

    print_step("Installing dependencies...")
    req_file = install_dir / "requirements.txt"
    if req_file.exists():
        subprocess.run([str(pip), "install", "-r", str(req_file), "-q"], check=True)

    print_step("Installing package...")
    extras = "[ui]" if install_ui else ""
    subprocess.run([str(pip), "install", "-e", f"{install_dir}{extras}", "-q"], check=True)

    print_success("Dependencies installed")


def create_data_dirs():
    """Create data directories."""
    data_dir = get_data_dir()
    for subdir in ["logs", "reports", "presets", "packs"]:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    print_success(f"Created data directory: {data_dir}")


def create_launchers(install_dir, venv_dir, resolve_path=None):
    """Create launcher scripts."""
    if IS_WINDOWS:
        # Windows batch files
        scripts_dir = venv_dir / "Scripts"

        cli_bat = install_dir / "resolve-suite.bat"
        cli_bat.write_text(f"""@echo off
call "{scripts_dir}\\activate.bat"
python -m cli.main %*
""")
        print_success(f"Created: {cli_bat}")

        ui_bat = install_dir / "resolve-suite-ui.bat"
        ui_bat.write_text(f"""@echo off
call "{scripts_dir}\\activate.bat"
pythonw -m ui.app %*
""")
        print_success(f"Created: {ui_bat}")

        # Environment setup
        env_bat = install_dir / "rps_env.bat"
        content = f"""@echo off
set RPS_HOME=%USERPROFILE%\\.rps
set PATH=%PATH%;{scripts_dir}
"""
        if resolve_path:
            content += f'set RESOLVE_SCRIPT_API={resolve_path}\n'
        env_bat.write_text(content)

    else:
        # Unix shell scripts
        bin_dir = venv_dir / "bin"

        cli_sh = install_dir / "resolve-suite"
        cli_sh.write_text(f"""#!/usr/bin/env bash
source "{bin_dir}/activate"
python -m cli.main "$@"
""")
        cli_sh.chmod(0o755)
        print_success(f"Created: {cli_sh}")

        ui_sh = install_dir / "resolve-suite-ui"
        ui_sh.write_text(f"""#!/usr/bin/env bash
source "{bin_dir}/activate"
python -m ui.app "$@"
""")
        ui_sh.chmod(0o755)
        print_success(f"Created: {ui_sh}")

        # Environment setup
        env_sh = install_dir / "rps_env.sh"
        content = f"""#!/usr/bin/env bash
export RPS_HOME="$HOME/.rps"
export PATH="$PATH:{bin_dir}"
"""
        if resolve_path:
            content += f'export RESOLVE_SCRIPT_API="{resolve_path}"\n'
        env_sh.write_text(content)
        env_sh.chmod(0o755)


def add_to_path(install_dir):
    """Add to system PATH (Windows only for now)."""
    if not IS_WINDOWS:
        return

    if not prompt("Add to system PATH?"):
        return

    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                path_value, _ = winreg.QueryValueEx(key, "Path")
            except WindowsError:
                path_value = ""

            install_str = str(install_dir)
            if install_str not in path_value:
                new_path = f"{path_value};{install_str}" if path_value else install_str
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                print_success("Added to PATH")
    except Exception as e:
        print_warning(f"Could not update PATH: {e}")


def create_desktop_shortcut(install_dir):
    """Create desktop shortcut."""
    if not prompt("Create desktop shortcut?"):
        return

    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home()

    if IS_WINDOWS:
        try:
            import winreg
            # Use PowerShell to create shortcut
            shortcut_path = desktop / "Resolve Production Suite.lnk"
            target = install_dir / "resolve-suite-ui.bat"
            ps_cmd = f'''
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("{shortcut_path}")
$s.TargetPath = "{target}"
$s.WorkingDirectory = "{install_dir}"
$s.Description = "Resolve Production Suite"
$s.Save()
'''
            subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
            print_success(f"Created desktop shortcut")
        except Exception as e:
            print_warning(f"Could not create shortcut: {e}")

    elif IS_LINUX:
        shortcut = desktop / "resolve-production-suite.desktop"
        shortcut.write_text(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Resolve Production Suite
Exec={install_dir}/resolve-suite-ui
Terminal=false
Categories=AudioVideo;Video;
""")
        shortcut.chmod(0o755)
        print_success("Created desktop shortcut")


# =============================================================================
# Main Installation Flow
# =============================================================================

def run_installation():
    """Run the installation process."""
    print_header()
    print("INSTALLATION OPTIONS\n")

    install_dir = get_install_dir()
    install_ui = prompt("\nInstall desktop UI (PySide6)?")

    # Detect Resolve
    resolve_path = detect_resolve()
    if resolve_path:
        print_success(f"Detected Resolve: {resolve_path}")
    else:
        print_warning("DaVinci Resolve not detected")
        custom = input("Enter Resolve scripting path (or press Enter to skip): ").strip()
        if custom and Path(custom).exists():
            resolve_path = custom

    # Confirm
    print_header()
    print("INSTALLATION SUMMARY\n")
    print(f"  Install to:    {install_dir}")
    print(f"  Data directory: {get_data_dir()}")
    print(f"  Desktop UI:    {'Yes' if install_ui else 'No'}")
    print(f"  Resolve path:  {resolve_path or 'Not configured'}")
    print()

    if not prompt("Proceed with installation?"):
        print("Installation cancelled.")
        sys.exit(0)

    # Install
    print_header()
    print("INSTALLING...\n")

    try:
        print_step("Copying files...")
        copy_files(INSTALL_SOURCE, install_dir)

        venv_dir = create_venv(install_dir)
        install_dependencies(venv_dir, install_dir, install_ui)
        create_data_dirs()

        print_step("Creating launcher scripts...")
        create_launchers(install_dir, venv_dir, resolve_path)

        add_to_path(install_dir)
        create_desktop_shortcut(install_dir)

        # Success
        print_header()
        print(f"{Colors.GREEN}INSTALLATION COMPLETE!{Colors.END}\n")
        print("Quick Start:")
        print(f"  1. Open a new terminal")
        print(f"  2. Navigate to: {install_dir}")
        if IS_WINDOWS:
            print(f"  3. Run: resolve-suite.bat list")
            if install_ui:
                print(f"  4. Or launch: resolve-suite-ui.bat")
        else:
            print(f"  3. Run: ./resolve-suite list")
            if install_ui:
                print(f"  4. Or launch: ./resolve-suite-ui")
        print()
        print(f"Documentation: {install_dir / 'docs'}")
        print(f"Reports saved to: {get_data_dir() / 'reports'}")

    except Exception as e:
        print_error(f"Installation failed: {e}")
        import traceback
        traceback.print_exc()
        wait_for_key()
        sys.exit(1)

    wait_for_key()


def main():
    """Main entry point with menu."""
    print_header()

    # Check Python version
    if sys.version_info < MIN_PYTHON:
        print_error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required.")
        print_error(f"You have Python {sys.version_info.major}.{sys.version_info.minor}")
        wait_for_key()
        sys.exit(1)

    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

    print("""
    RESOLVE PRODUCTION SUITE
    10 Workflow Automation Tools for DaVinci Resolve

    Tools included:
      1. Revision Resolver      6. Timeline Normalizer
      2. Relink Across Projects 7. Component Graphics
      3. Smart Reframer         8. Delivery Spec Enforcer
      4. Caption Layout         9. Change Impact Analyzer
      5. Feedback Compiler     10. Brand Drift Detector
""")

    while True:
        print("\nWhat would you like to do?\n")
        print("  1. Install Resolve Production Suite")
        print("  2. Check for Updates")
        print("  3. Exit")
        print()

        try:
            choice = input("Enter choice (1-3): ").strip()

            if choice == "1":
                run_installation()
                break
            elif choice == "2":
                run_updater()
            elif choice == "3":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
