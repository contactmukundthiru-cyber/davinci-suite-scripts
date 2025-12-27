import argparse
import platform
import subprocess
import sys
from pathlib import Path

from core.config import get_config, ensure_dirs
from core.fs import load_json
from core.logging import get_logger, setup_logging
from core.reports import Report
from tools.base import build_context
from tools.registry import TOOL_REGISTRY
from tools.utils import item_error, now_stamp
from resolve.resolve_api import ResolveConnectionError

SCRIPT_DIR = Path(__file__).parent.parent
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def create_desktop_shortcut() -> bool:
    """Create desktop shortcut for the GUI application."""
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        print(f"Desktop folder not found: {desktop}")
        return False

    install_dir = SCRIPT_DIR

    if IS_WINDOWS:
        try:
            shortcut_path = desktop / "Resolve Production Suite.lnk"
            target = install_dir / "resolve-suite-ui.bat"

            if not target.exists():
                print(f"UI launcher not found: {target}")
                print("Please run the full installation first.")
                return False

            ps_cmd = f'''
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("{shortcut_path}")
$s.TargetPath = "{target}"
$s.WorkingDirectory = "{install_dir}"
$s.Description = "Resolve Production Suite"
$s.Save()
'''
            subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
            print(f"Created desktop shortcut: {shortcut_path}")
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False

    elif IS_MACOS:
        try:
            shortcut_path = desktop / "Resolve Production Suite.command"
            target = install_dir / "resolve-suite-ui"

            if not target.exists():
                print(f"UI launcher not found: {target}")
                print("Please run the full installation first.")
                return False

            shortcut_path.write_text(f"""#!/bin/bash
# Resolve Production Suite Launcher
cd "{install_dir}"
./resolve-suite-ui
""")
            shortcut_path.chmod(0o755)
            print(f"Created desktop shortcut: {shortcut_path}")
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False

    elif IS_LINUX:
        try:
            shortcut_path = desktop / "resolve-production-suite.desktop"
            target = install_dir / "resolve-suite-ui"

            if not target.exists():
                print(f"UI launcher not found: {target}")
                print("Please run the full installation first.")
                return False

            shortcut_path.write_text(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Resolve Production Suite
Exec={install_dir}/resolve-suite-ui
Terminal=false
Categories=AudioVideo;Video;
""")
            shortcut_path.chmod(0o755)
            print(f"Created desktop shortcut: {shortcut_path}")
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False

    print("Unsupported platform for desktop shortcuts")
    return False


def _save_report(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{report.tool_id}_{now_stamp()}"
    report.to_json(output_dir / f"{base}.json")
    report.to_csv(output_dir / f"{base}.csv")
    report.to_html(output_dir / f"{base}.html")


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve Production Suite")
    parser.add_argument("--dry-run", action="store_true", help="Run without changing Resolve")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List available tools")
    sub.add_parser("version", help="Show version")
    sub.add_parser("shortcut", help="Create desktop shortcut for the GUI app")
    update_parser = sub.add_parser("update", help="Check for updates")
    update_parser.add_argument("--download", "-d", action="store_true", help="Open download page")

    run_parser = sub.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool_id", help="Tool identifier")
    run_parser.add_argument("--options", help="Path to JSON options")
    run_parser.add_argument("--output", help="Report output directory")

    args = parser.parse_args()

    cfg = get_config()
    cfg.dry_run = args.dry_run
    ensure_dirs(cfg)
    setup_logging(cfg)
    logger = get_logger("cli")

    if args.command == "list":
        for tool_id in TOOL_REGISTRY.keys():
            print(tool_id)
        return

    if args.command == "version":
        version_file = SCRIPT_DIR / "VERSION"
        version = version_file.read_text().strip() if version_file.exists() else "unknown"
        print(f"Resolve Production Suite v{version}")
        return

    if args.command == "shortcut":
        success = create_desktop_shortcut()
        if success:
            print("\nYou can now double-click the shortcut on your Desktop to launch the GUI.")
            print("Remember: DaVinci Resolve must be running before using the tools!")
        sys.exit(0 if success else 1)

    if args.command == "update":
        update_script = SCRIPT_DIR / "scripts" / "update_checker.py"
        if update_script.exists():
            cmd = [sys.executable, str(update_script)]
            if args.download:
                cmd.append("--download")
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        else:
            print("Update checker not found")
            return

    if args.command == "run":
        if args.tool_id not in TOOL_REGISTRY:
            raise SystemExit(f"Unknown tool_id: {args.tool_id}")
        options = {}
        if args.options:
            options = load_json(Path(args.options))
        ctx = build_context(cfg, dry_run=args.dry_run)
        ctx.logger = get_logger("tool", tool_id=args.tool_id, tx_id=ctx.transaction.transaction_id)
        tool_cls = TOOL_REGISTRY[args.tool_id]
        tool = tool_cls(ctx)
        try:
            report = tool.run(options)
        except ResolveConnectionError as exc:
            report = Report(tool_id=args.tool_id, title=args.tool_id)
            report.add(item_error("resolve", str(exc)))
        out_dir = Path(args.output) if args.output else cfg.reports_dir
        _save_report(report, out_dir)
        logger.info("Report saved", extra={"rps_tool_id": args.tool_id})
        return

    parser.print_help()


if __name__ == "__main__":
    main()
