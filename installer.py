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

VERSION = "0.3.14"
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


def apply_update(zip_path, install_dir, is_current_dir=False):
    """Extract and apply update from zip file."""
    print_step("Applying update...")

    try:
        # Extract to temp location first
        temp_extract = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_extract)

        # Find the actual content directory (might be nested)
        content_dir = temp_extract
        subdirs = list(temp_extract.iterdir())
        if len(subdirs) == 1 and subdirs[0].is_dir():
            content_dir = subdirs[0]

        if is_current_dir:
            # For current directory, copy files individually (avoids locking issues)
            # Skip .venv and other runtime files
            skip_dirs = {'.venv', '__pycache__', '.git'}

            for item in content_dir.iterdir():
                if item.name in skip_dirs:
                    continue

                dest = install_dir / item.name
                try:
                    if item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
                except PermissionError:
                    # File is in use, skip it
                    print_warning(f"Skipped (in use): {item.name}")
                    continue

            print_success("Update applied! Please restart to see new version.")
        else:
            # For installed location, do full replacement
            backup_dir = install_dir.parent / f"{install_dir.name}_backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # Backup current installation
            if install_dir.exists():
                shutil.move(str(install_dir), str(backup_dir))

            # Copy new files
            shutil.copytree(content_dir, install_dir)

            # Restore venv if it existed
            venv_backup = backup_dir / ".venv"
            if venv_backup.exists():
                shutil.move(str(venv_backup), str(install_dir / ".venv"))

            # Clean up backup
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            print_success("Update applied successfully!")

        # Clean up temp
        shutil.rmtree(temp_extract)
        return True

    except Exception as e:
        print_error(f"Failed to apply update: {e}")
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

                    updated = False

                    # Update installed location if it exists
                    if install_dir.exists():
                        if apply_update(zip_path, install_dir, is_current_dir=False):
                            updated = True

                    # Also update the current folder if different from install_dir
                    # (handles case where user runs from download folder)
                    current_dir = BUNDLE_DIR
                    if current_dir.resolve() != install_dir.resolve() and current_dir.exists():
                        # Check if this looks like our package (has installer.py)
                        if (current_dir / "installer.py").exists():
                            print_step("Updating current folder...")
                            # Re-download since we already extracted once
                            if download_file(auto_url, zip_path, "Downloading for current folder"):
                                if apply_update(zip_path, current_dir, is_current_dir=True):
                                    updated = True

                    if updated:
                        # Ensure desktop shortcut exists after update
                        ensure_desktop_shortcut(install_dir)

                        print()
                        print("=" * 50)
                        print(f"{Colors.GREEN}  UPDATE SUCCESSFUL!{Colors.END}")
                        print("=" * 50)
                        print(f"\n  Updated to version {remote_version}")
                        print(f"\n  Installation: {install_dir}")
                        print("\n  Next steps:")
                        print("    1. Close this window")
                        print("    2. Re-open the installer to see new version")
                        print("    3. Or use the desktop shortcut to launch the UI")
                        print()
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
    python = get_python(venv_dir)

    # Use python -m pip instead of pip directly (fixes Windows upgrade issue)
    print_step("Upgrading pip...")
    subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "-q"], check=True)

    print_step("Installing dependencies...")
    req_file = install_dir / "requirements.txt"
    if req_file.exists():
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(req_file), "-q"], check=True)

    print_step("Installing package...")
    extras = "[ui]" if install_ui else ""
    subprocess.run([str(python), "-m", "pip", "install", "-e", f"{install_dir}{extras}", "-q"], check=True)

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


def create_desktop_shortcut_impl(install_dir, silent=False):
    """Create desktop shortcut (implementation).

    Args:
        install_dir: Installation directory
        silent: If True, don't print success messages (for updates)

    Returns:
        True if shortcut was created, False otherwise
    """
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path.home()

    if IS_WINDOWS:
        try:
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
            if not silent:
                print_success("Created desktop shortcut")
            return True
        except Exception as e:
            if not silent:
                print_warning(f"Could not create shortcut: {e}")
            return False

    elif IS_MACOS:
        try:
            # Create macOS shortcut with .command extension so it's double-clickable in Finder
            shortcut_path = desktop / "Resolve Production Suite.command"
            target = install_dir / "resolve-suite-ui"

            # Create a shell script wrapper that users can double-click
            shortcut_path.write_text(f"""#!/bin/bash
# Resolve Production Suite Launcher
cd "{install_dir}"
./resolve-suite-ui
""")
            shortcut_path.chmod(0o755)

            if not silent:
                print_success("Created desktop shortcut")
            return True
        except Exception as e:
            if not silent:
                print_warning(f"Could not create shortcut: {e}")
            return False

    elif IS_LINUX:
        try:
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
            if not silent:
                print_success("Created desktop shortcut")
            return True
        except Exception as e:
            if not silent:
                print_warning(f"Could not create shortcut: {e}")
            return False

    return False


def create_desktop_shortcut(install_dir):
    """Create desktop shortcut (with user prompt)."""
    if not prompt("Create desktop shortcut?"):
        return
    create_desktop_shortcut_impl(install_dir, silent=False)


def ensure_desktop_shortcut(install_dir):
    """Ensure desktop shortcut exists (creates if missing, silent)."""
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        return

    # Check if shortcut already exists
    if IS_WINDOWS:
        shortcut_path = desktop / "Resolve Production Suite.lnk"
    elif IS_MACOS:
        shortcut_path = desktop / "Resolve Production Suite.command"
    elif IS_LINUX:
        shortcut_path = desktop / "resolve-production-suite.desktop"
    else:
        return

    if not shortcut_path.exists():
        print_step("Creating desktop shortcut...")
        if create_desktop_shortcut_impl(install_dir, silent=True):
            print_success("Desktop shortcut created")


# =============================================================================
# Main Installation Flow
# =============================================================================

def run_installation():
    """Run the installation process."""
    print_header()
    print("INSTALLATION\n")

    # Use default install directory (simpler)
    install_dir = get_install_path()
    print(f"  Install location: {install_dir}")
    print(f"  Data directory:   {get_data_dir()}")
    print()

    # Always install UI (most users want it)
    install_ui = True
    print_success("Will install Desktop UI (recommended)")

    # Auto-detect Resolve
    resolve_path = detect_resolve()
    if resolve_path:
        print_success(f"Detected Resolve: {resolve_path}")
    else:
        print_warning("DaVinci Resolve not detected (you can install Resolve later)")

    print()
    if not prompt("Ready to install?"):
        print("Installation cancelled.")
        wait_for_key()
        return

    # Install with progress tracking
    print_header()
    print("INSTALLING...\n")
    print("This may take a few minutes. Please wait.\n")

    steps_total = 6
    step_num = 0

    def progress(msg):
        nonlocal step_num
        step_num += 1
        print(f"[{step_num}/{steps_total}] {msg}")

    try:
        progress("Copying files...")
        try:
            copy_files(INSTALL_SOURCE, install_dir)
        except PermissionError as e:
            print_error("Permission denied while copying files.")
            print("\nTry one of these:")
            if IS_WINDOWS:
                print("  1. Run the installer as Administrator")
                print("  2. Close any programs using the install folder")
            else:
                print("  1. Check you have write permission to ~/.local/share/")
                print("  2. Close any programs using the install folder")
            wait_for_key()
            return
        except Exception as e:
            print_error(f"Failed to copy files: {e}")
            wait_for_key()
            return

        progress("Creating virtual environment...")
        try:
            venv_dir = create_venv(install_dir)
        except Exception as e:
            print_error(f"Failed to create virtual environment: {e}")
            print("\nMake sure you have Python 3.9+ with venv support:")
            if IS_LINUX:
                print("  sudo apt install python3-venv")
            wait_for_key()
            return

        progress("Installing dependencies (this takes a while)...")
        try:
            install_dependencies(venv_dir, install_dir, install_ui)
        except subprocess.CalledProcessError as e:
            print_error("Failed to install dependencies.")
            print("\nPossible solutions:")
            print("  1. Check your internet connection")
            print("  2. Try running the installer again")
            if IS_LINUX:
                print("  3. Install pip: sudo apt install python3-pip")
            wait_for_key()
            return
        except Exception as e:
            print_error(f"Dependency installation error: {e}")
            wait_for_key()
            return

        progress("Setting up data directories...")
        create_data_dirs()

        progress("Creating launcher scripts...")
        create_launchers(install_dir, venv_dir, resolve_path)

        progress("Creating desktop shortcut...")
        create_desktop_shortcut_impl(install_dir, silent=False)

        # Success
        print()
        print("=" * 55)
        print(f"{Colors.GREEN}  INSTALLATION COMPLETE!{Colors.END}")
        print("=" * 55)
        print()
        print(f"  {Colors.CYAN}GET STARTED:{Colors.END}")
        print()
        print("    1. Open DaVinci Resolve")
        print("    2. Double-click 'Resolve Production Suite' on your Desktop")
        print("    3. Click 'Connect' to connect to Resolve")
        print("    4. Select a tool and run it!")
        print()
        print(f"  {Colors.CYAN}SHORTCUT MISSING?{Colors.END}")
        print("    Run this installer again and choose 'Create Desktop Shortcut'")
        print()
        print(f"  {Colors.CYAN}DOCUMENTATION:{Colors.END}")
        print(f"    {install_dir / 'docs'}")
        print()

    except KeyboardInterrupt:
        print("\n\nInstallation cancelled.")
        return
    except Exception as e:
        print()
        print_error(f"Installation failed unexpectedly: {e}")
        print()
        print("Please report this error at:")
        print("  https://github.com/contactmukundthiru-cyber/davinci-suite-scripts/issues")
        print()
        print("Include the error message above when reporting.")
        import traceback
        traceback.print_exc()
        wait_for_key()
        return

    wait_for_key()


# =============================================================================
# Uninstall
# =============================================================================

def run_uninstall():
    """Uninstall Resolve Production Suite."""
    print_header()
    print("UNINSTALL\n")

    # Find installation directory
    if IS_WINDOWS:
        install_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ResolveProductionSuite"
    else:
        install_dir = Path.home() / ".local" / "share" / "resolve-production-suite"

    data_dir = get_data_dir()

    # Check if installed
    if not install_dir.exists():
        print_warning("Resolve Production Suite is not installed.")
        print(f"  Expected location: {install_dir}")
        wait_for_key()
        return

    print(f"Installation found: {install_dir}")
    print(f"Data directory: {data_dir}")
    print()

    if not prompt("Are you sure you want to uninstall?", "n"):
        print("Uninstall cancelled.")
        wait_for_key()
        return

    remove_data = prompt("Also remove user data (logs, reports, presets)?", "n")

    print()
    print_step("Uninstalling...")

    try:
        # Remove desktop shortcut
        desktop = Path.home() / "Desktop"
        if IS_WINDOWS:
            shortcut = desktop / "Resolve Production Suite.lnk"
            if shortcut.exists():
                shortcut.unlink()
                print_success("Removed desktop shortcut")
        elif IS_MACOS:
            shortcut = desktop / "Resolve Production Suite.command"
            if shortcut.exists():
                shortcut.unlink()
                print_success("Removed desktop shortcut")
        elif IS_LINUX:
            shortcut = desktop / "resolve-production-suite.desktop"
            if shortcut.exists():
                shortcut.unlink()
                print_success("Removed desktop shortcut")

        # Remove from PATH on Windows
        if IS_WINDOWS:
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        path_value, _ = winreg.QueryValueEx(key, "Path")
                        install_str = str(install_dir)
                        if install_str in path_value:
                            # Remove our path
                            paths = [p for p in path_value.split(";") if p and p != install_str]
                            new_path = ";".join(paths)
                            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                            print_success("Removed from PATH")
                    except WindowsError:
                        pass
            except Exception:
                pass

        # Remove installation directory
        if install_dir.exists():
            shutil.rmtree(install_dir)
            print_success(f"Removed: {install_dir}")

        # Remove data directory if requested
        if remove_data and data_dir.exists():
            shutil.rmtree(data_dir)
            print_success(f"Removed: {data_dir}")

        print()
        print(f"{Colors.GREEN}Uninstall complete!{Colors.END}")
        print("\nResolve Production Suite has been removed from your system.")

    except Exception as e:
        print_error(f"Uninstall failed: {e}")
        import traceback
        traceback.print_exc()

    wait_for_key()


def is_installed():
    """Check if the suite is already installed."""
    if IS_WINDOWS:
        install_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ResolveProductionSuite"
    else:
        install_dir = Path.home() / ".local" / "share" / "resolve-production-suite"
    return install_dir.exists()


def get_install_path():
    """Get the default installation path."""
    if IS_WINDOWS:
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ResolveProductionSuite"
    else:
        return Path.home() / ".local" / "share" / "resolve-production-suite"


def run_create_shortcut():
    """Create desktop shortcut as a standalone action."""
    print_header()
    print("CREATE DESKTOP SHORTCUT\n")

    install_dir = get_install_path()

    if not install_dir.exists():
        print_error("Resolve Production Suite is not installed.")
        print(f"  Expected location: {install_dir}")
        print("\nPlease install first, then create a shortcut.")
        wait_for_key()
        return

    print(f"Installation found: {install_dir}")
    print()

    if create_desktop_shortcut_impl(install_dir, silent=False):
        print()
        print(f"{Colors.GREEN}Desktop shortcut created successfully!{Colors.END}")
        print("\nYou can now double-click the shortcut on your Desktop")
        print("to launch Resolve Production Suite.")
    else:
        print()
        print_error("Failed to create desktop shortcut.")
        print("\nYou can manually create a shortcut to:")
        if IS_WINDOWS:
            print(f"  {install_dir / 'resolve-suite-ui.bat'}")
        else:
            print(f"  {install_dir / 'resolve-suite-ui'}")

    wait_for_key()


def main():
    """Main entry point with menu."""
    print_header()

    # Check Python version
    if sys.version_info < MIN_PYTHON:
        print_error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required.")
        print_error(f"You have Python {sys.version_info.major}.{sys.version_info.minor}")
        print()
        print("Please install Python 3.9 or newer:")
        if IS_WINDOWS:
            print("  https://www.python.org/downloads/windows/")
        elif IS_MACOS:
            print("  https://www.python.org/downloads/macos/")
        else:
            print("  sudo apt install python3.9  (Ubuntu/Debian)")
            print("  sudo dnf install python39   (Fedora)")
        wait_for_key()
        sys.exit(1)

    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

    already_installed = is_installed()

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
        if already_installed:
            print("  1. Reinstall / Repair")
            print("  2. Check for Updates")
            print("  3. Create Desktop Shortcut")
            print("  4. Uninstall")
            print("  5. Exit")
        else:
            print("  1. Install (First Time Setup)")
            print("  2. Check for Updates")
            print("  3. Create Desktop Shortcut")
            print("  4. Uninstall")
            print("  5. Exit")
        print()

        try:
            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                run_installation()
                break
            elif choice == "2":
                run_updater()
            elif choice == "3":
                run_create_shortcut()
            elif choice == "4":
                run_uninstall()
                break
            elif choice == "5":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
