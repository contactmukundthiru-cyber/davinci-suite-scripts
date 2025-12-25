#!/usr/bin/env python3
"""
Resolve Production Suite - Graphical Installer

A cross-platform GUI installer using Tkinter (bundled with Python).
No external dependencies required.

Usage:
    python installer_gui.py

On Windows, double-click this file or run:
    pythonw installer_gui.py
"""

import os
import platform
import subprocess
import sys
import threading
from pathlib import Path

# Tkinter import with fallback
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("Tkinter not found. Please install python3-tk:")
    print("  Ubuntu/Debian: sudo apt install python3-tk")
    print("  Fedora: sudo dnf install python3-tkinter")
    print("  macOS: brew install python-tk")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
VERSION = (SCRIPT_DIR / "VERSION").read_text().strip() if (SCRIPT_DIR / "VERSION").exists() else "0.2.0"
VENV_DIR = SCRIPT_DIR / ".venv"
MIN_PYTHON = (3, 9)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


# =============================================================================
# Installer Logic
# =============================================================================

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Resolve Production Suite v{VERSION} - Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Center window
        self.center_window()

        # Variables
        self.install_ui = tk.BooleanVar(value=True)
        self.install_analysis = tk.BooleanVar(value=False)
        self.dev_mode = tk.BooleanVar(value=False)
        self.resolve_path = tk.StringVar(value=self.detect_resolve())
        self.install_dir = tk.StringVar(value=str(SCRIPT_DIR))

        # Create pages
        self.pages = {}
        self.current_page = 0

        self.create_welcome_page()
        self.create_options_page()
        self.create_resolve_page()
        self.create_install_page()
        self.create_complete_page()

        self.show_page(0)

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (300)
        y = (self.root.winfo_screenheight() // 2) - (250)
        self.root.geometry(f"600x500+{x}+{y}")

    def detect_resolve(self) -> str:
        """Auto-detect Resolve scripting path."""
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

        # Check environment variable
        env_path = os.environ.get("RESOLVE_SCRIPT_API", "")
        if env_path and Path(env_path).exists():
            return env_path

        # Check common paths
        for p in paths:
            if Path(p).exists():
                return p

        return ""

    def create_header(self, parent, title, subtitle=""):
        """Create a consistent header for each page."""
        header = ttk.Frame(parent)
        header.pack(fill="x", padx=20, pady=(20, 10))

        ttk.Label(
            header,
            text=title,
            font=("Helvetica", 16, "bold")
        ).pack(anchor="w")

        if subtitle:
            ttk.Label(
                header,
                text=subtitle,
                font=("Helvetica", 10),
                foreground="gray"
            ).pack(anchor="w", pady=(5, 0))

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=20, pady=10)

    def create_nav_buttons(self, parent, back=True, next_text="Next", next_cmd=None):
        """Create navigation buttons at the bottom."""
        nav = ttk.Frame(parent)
        nav.pack(side="bottom", fill="x", padx=20, pady=20)

        ttk.Separator(parent, orient="horizontal").pack(side="bottom", fill="x", padx=20)

        if back:
            ttk.Button(
                nav,
                text="Back",
                command=lambda: self.show_page(self.current_page - 1)
            ).pack(side="left")

        ttk.Button(
            nav,
            text="Cancel",
            command=self.cancel
        ).pack(side="left", padx=(10, 0))

        if next_cmd:
            ttk.Button(
                nav,
                text=next_text,
                command=next_cmd
            ).pack(side="right")

    def create_welcome_page(self):
        """Page 0: Welcome screen."""
        page = ttk.Frame(self.root)
        self.pages[0] = page

        self.create_header(
            page,
            "Welcome to Resolve Production Suite",
            f"Version {VERSION} - Workflow Automation for DaVinci Resolve"
        )

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        ttk.Label(
            content,
            text="This installer will set up the Resolve Production Suite on your system.",
            wraplength=500
        ).pack(anchor="w", pady=(0, 20))

        ttk.Label(
            content,
            text="The suite includes 10 workflow automation tools:",
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w")

        tools = [
            "1. Revision Resolver - Asset swap across timelines",
            "2. Relink Across Projects - Brand kit rollout",
            "3. Smart Reframer - Constraint-based reframing",
            "4. Caption Layout Protector - Safe zone protection",
            "5. Feedback Compiler - Notes to markers",
            "6. Timeline Normalizer - Handoff preparation",
            "7. Component Graphics - Graphics registry",
            "8. Delivery Spec Enforcer - Output validation",
            "9. Change Impact Analyzer - Timeline diff",
            "10. Brand Drift Detector - Brand audit"
        ]

        tools_frame = ttk.Frame(content)
        tools_frame.pack(fill="x", pady=10)

        for tool in tools:
            ttk.Label(tools_frame, text=tool, font=("Helvetica", 9)).pack(anchor="w")

        ttk.Label(
            content,
            text="Click Next to continue.",
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(20, 0))

        self.create_nav_buttons(
            page,
            back=False,
            next_text="Next",
            next_cmd=lambda: self.show_page(1)
        )

    def create_options_page(self):
        """Page 1: Installation options."""
        page = ttk.Frame(self.root)
        self.pages[1] = page

        self.create_header(
            page,
            "Installation Options",
            "Choose which components to install"
        )

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        # UI option
        ui_frame = ttk.Frame(content)
        ui_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(
            ui_frame,
            text="Install Desktop UI (PySide6)",
            variable=self.install_ui
        ).pack(anchor="w")

        ttk.Label(
            ui_frame,
            text="Graphical interface for running tools. Adds ~150MB.",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor="w", padx=(25, 0))

        # Analysis option
        analysis_frame = ttk.Frame(content)
        analysis_frame.pack(fill="x", pady=15)

        ttk.Checkbutton(
            analysis_frame,
            text="Install Analysis Extras (OpenCV, NumPy)",
            variable=self.install_analysis
        ).pack(anchor="w")

        ttk.Label(
            analysis_frame,
            text="Required for face detection and saliency analysis in Smart Reframer.",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor="w", padx=(25, 0))

        # Dev mode option
        dev_frame = ttk.Frame(content)
        dev_frame.pack(fill="x", pady=15)

        ttk.Checkbutton(
            dev_frame,
            text="Developer Mode (editable install)",
            variable=self.dev_mode
        ).pack(anchor="w")

        ttk.Label(
            dev_frame,
            text="For developers who want to modify the source code.",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor="w", padx=(25, 0))

        self.create_nav_buttons(
            page,
            next_text="Next",
            next_cmd=lambda: self.show_page(2)
        )

    def create_resolve_page(self):
        """Page 2: Resolve path configuration."""
        page = ttk.Frame(self.root)
        self.pages[2] = page

        self.create_header(
            page,
            "DaVinci Resolve Configuration",
            "Configure the path to Resolve's scripting modules"
        )

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        if self.resolve_path.get():
            ttk.Label(
                content,
                text="DaVinci Resolve was detected automatically:",
                font=("Helvetica", 10)
            ).pack(anchor="w")
        else:
            ttk.Label(
                content,
                text="DaVinci Resolve was not detected. Please specify the path:",
                font=("Helvetica", 10),
                foreground="orange"
            ).pack(anchor="w")

        path_frame = ttk.Frame(content)
        path_frame.pack(fill="x", pady=15)

        ttk.Entry(
            path_frame,
            textvariable=self.resolve_path,
            width=50
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_resolve
        ).pack(side="right", padx=(10, 0))

        ttk.Label(
            content,
            text="Common locations:",
            font=("Helvetica", 9, "bold")
        ).pack(anchor="w", pady=(20, 5))

        locations = []
        if IS_LINUX:
            locations = ["/opt/resolve/Developer/Scripting/Modules"]
        elif IS_MACOS:
            locations = ["/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"]
        elif IS_WINDOWS:
            locations = [r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"]

        for loc in locations:
            ttk.Label(
                content,
                text=loc,
                font=("Helvetica", 9),
                foreground="gray"
            ).pack(anchor="w")

        ttk.Label(
            content,
            text="\nNote: You can leave this empty if Resolve is not installed yet.\nYou can set the RESOLVE_SCRIPT_API environment variable later.",
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(anchor="w", pady=(20, 0))

        self.create_nav_buttons(
            page,
            next_text="Install",
            next_cmd=self.start_install
        )

    def browse_resolve(self):
        """Open directory browser for Resolve path."""
        path = filedialog.askdirectory(
            title="Select Resolve Scripting Modules Directory"
        )
        if path:
            self.resolve_path.set(path)

    def create_install_page(self):
        """Page 3: Installation progress."""
        page = ttk.Frame(self.root)
        self.pages[3] = page

        self.create_header(
            page,
            "Installing...",
            "Please wait while the suite is being installed"
        )

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        self.progress = ttk.Progressbar(
            content,
            mode="determinate",
            length=400
        )
        self.progress.pack(pady=20)

        self.status_label = ttk.Label(
            content,
            text="Preparing installation...",
            font=("Helvetica", 10)
        )
        self.status_label.pack()

        # Log text area
        log_frame = ttk.Frame(content)
        log_frame.pack(fill="both", expand=True, pady=(20, 0))

        self.log_text = tk.Text(
            log_frame,
            height=10,
            width=60,
            font=("Courier", 9),
            state="disabled"
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def create_complete_page(self):
        """Page 4: Installation complete."""
        page = ttk.Frame(self.root)
        self.pages[4] = page

        self.create_header(
            page,
            "Installation Complete!",
            "Resolve Production Suite has been installed successfully"
        )

        content = ttk.Frame(page)
        content.pack(fill="both", expand=True, padx=40, pady=20)

        ttk.Label(
            content,
            text="The suite is now ready to use.",
            font=("Helvetica", 11)
        ).pack(anchor="w", pady=(0, 20))

        ttk.Label(
            content,
            text="Quick Start:",
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w")

        commands = [
            "",
            "List all tools:",
            "  resolve-suite list",
            "",
            "Run a tool:",
            "  resolve-suite run t1_revision_resolver --dry-run",
            "",
            "Check for updates:",
            "  resolve-suite update"
        ]

        if self.install_ui.get():
            commands.extend([
                "",
                "Launch Desktop UI:",
                "  resolve-suite-ui"
            ])

        for cmd in commands:
            ttk.Label(
                content,
                text=cmd,
                font=("Courier", 9) if cmd.startswith("  ") else ("Helvetica", 9)
            ).pack(anchor="w")

        # Close button
        nav = ttk.Frame(page)
        nav.pack(side="bottom", fill="x", padx=20, pady=20)
        ttk.Separator(page, orient="horizontal").pack(side="bottom", fill="x", padx=20)

        ttk.Button(
            nav,
            text="Finish",
            command=self.root.quit
        ).pack(side="right")

    def show_page(self, page_num):
        """Switch to a different page."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()

        # Show requested page
        self.current_page = page_num
        self.pages[page_num].pack(fill="both", expand=True)

    def log(self, message):
        """Add message to log."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update()

    def update_progress(self, value, status=""):
        """Update progress bar and status."""
        self.progress["value"] = value
        if status:
            self.status_label.config(text=status)
        self.root.update()

    def start_install(self):
        """Begin installation in background thread."""
        self.show_page(3)
        thread = threading.Thread(target=self.run_install, daemon=True)
        thread.start()

    def run_install(self):
        """Run the actual installation."""
        try:
            python = sys.executable

            # Step 1: Create virtual environment
            self.update_progress(10, "Creating virtual environment...")
            self.log("Creating virtual environment...")

            if VENV_DIR.exists():
                self.log("Virtual environment already exists, reusing...")
            else:
                result = subprocess.run(
                    [python, "-m", "venv", str(VENV_DIR)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise Exception(f"Failed to create venv: {result.stderr}")

            self.log("Virtual environment ready.")

            # Get pip path
            if IS_WINDOWS:
                pip = VENV_DIR / "Scripts" / "pip.exe"
                venv_python = VENV_DIR / "Scripts" / "python.exe"
            else:
                pip = VENV_DIR / "bin" / "pip"
                venv_python = VENV_DIR / "bin" / "python"

            # Step 2: Upgrade pip
            self.update_progress(20, "Upgrading pip...")
            self.log("Upgrading pip and setuptools...")

            result = subprocess.run(
                [str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"],
                capture_output=True,
                text=True
            )
            self.log("pip upgraded.")

            # Step 3: Install base dependencies
            self.update_progress(35, "Installing base dependencies...")
            self.log("Installing base dependencies...")

            req_file = SCRIPT_DIR / "requirements.txt"
            if req_file.exists():
                result = subprocess.run(
                    [str(pip), "install", "-r", str(req_file)],
                    capture_output=True,
                    text=True
                )

            # Step 4: Install package
            self.update_progress(50, "Installing Resolve Production Suite...")
            self.log("Installing main package...")

            extras = []
            if self.install_ui.get():
                extras.append("ui")
            if self.install_analysis.get():
                extras.append("analysis")

            install_spec = str(SCRIPT_DIR)
            if extras:
                install_spec += f"[{','.join(extras)}]"

            cmd = [str(pip), "install"]
            if self.dev_mode.get():
                cmd.append("-e")
            cmd.append(install_spec)

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"Warning: {result.stderr}")

            self.log("Package installed.")

            # Step 5: Create directories
            self.update_progress(70, "Creating data directories...")
            self.log("Creating data directories...")

            rps_home = Path.home() / ".rps"
            for subdir in ["logs", "reports", "presets", "packs"]:
                (rps_home / subdir).mkdir(parents=True, exist_ok=True)

            self.log(f"Created: {rps_home}")

            # Step 6: Create launcher scripts
            self.update_progress(85, "Creating launcher scripts...")
            self.log("Creating launcher scripts...")

            self.create_launchers()

            # Step 7: Set environment variable
            if self.resolve_path.get():
                self.log(f"Resolve path: {self.resolve_path.get()}")
                self.create_env_script()

            self.update_progress(100, "Installation complete!")
            self.log("\nInstallation completed successfully!")

            # Show complete page
            self.root.after(1000, lambda: self.show_page(4))

        except Exception as e:
            self.log(f"\nError: {e}")
            messagebox.showerror("Installation Error", str(e))

    def create_launchers(self):
        """Create launcher scripts."""
        if IS_WINDOWS:
            # Windows batch files
            venv_scripts = VENV_DIR / "Scripts"

            cli_launcher = SCRIPT_DIR / "resolve-suite.bat"
            cli_launcher.write_text(f"""@echo off
call "{venv_scripts}\\activate.bat"
python -m cli.main %*
""")
            self.log(f"Created: {cli_launcher}")

            if self.install_ui.get():
                ui_launcher = SCRIPT_DIR / "resolve-suite-ui.bat"
                ui_launcher.write_text(f"""@echo off
call "{venv_scripts}\\activate.bat"
pythonw -m ui.app %*
""")
                self.log(f"Created: {ui_launcher}")
        else:
            # Unix shell scripts
            venv_bin = VENV_DIR / "bin"

            cli_launcher = SCRIPT_DIR / "resolve-suite"
            cli_launcher.write_text(f"""#!/usr/bin/env bash
source "{venv_bin}/activate"
python -m cli.main "$@"
""")
            cli_launcher.chmod(0o755)
            self.log(f"Created: {cli_launcher}")

            if self.install_ui.get():
                ui_launcher = SCRIPT_DIR / "resolve-suite-ui"
                ui_launcher.write_text(f"""#!/usr/bin/env bash
source "{venv_bin}/activate"
python -m ui.app "$@"
""")
                ui_launcher.chmod(0o755)
                self.log(f"Created: {ui_launcher}")

    def create_env_script(self):
        """Create environment setup script."""
        resolve_path = self.resolve_path.get()

        if IS_WINDOWS:
            env_script = SCRIPT_DIR / "rps_env.bat"
            env_script.write_text(f"""@echo off
set RPS_HOME=%USERPROFILE%\\.rps
set RESOLVE_SCRIPT_API={resolve_path}
set PATH=%PATH%;{VENV_DIR}\\Scripts
""")
        else:
            env_script = SCRIPT_DIR / "rps_env.sh"
            env_script.write_text(f"""#!/usr/bin/env bash
export RPS_HOME="$HOME/.rps"
export RESOLVE_SCRIPT_API="{resolve_path}"
export PATH="$PATH:{VENV_DIR}/bin"
""")
            env_script.chmod(0o755)

        self.log(f"Created: {env_script}")

    def cancel(self):
        """Cancel installation."""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?"):
            self.root.quit()


# =============================================================================
# Main
# =============================================================================

def main():
    # Check Python version
    if sys.version_info < MIN_PYTHON:
        messagebox.showerror(
            "Python Version Error",
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.\n"
            f"You have Python {sys.version_info.major}.{sys.version_info.minor}"
        )
        sys.exit(1)

    root = tk.Tk()

    # Style
    style = ttk.Style()
    if IS_WINDOWS:
        style.theme_use("vista")
    elif IS_MACOS:
        style.theme_use("aqua")
    else:
        try:
            style.theme_use("clam")
        except:
            pass

    app = InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
