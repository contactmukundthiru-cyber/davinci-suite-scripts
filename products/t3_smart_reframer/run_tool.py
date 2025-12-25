import argparse
from pathlib import Path

from core.config import get_config, ensure_dirs
from core.fs import load_json
from core.logging import get_logger, setup_logging
from core.reports import Report
from resolve.resolve_api import ResolveConnectionError
from tools.base import build_context
from tools.t3_smart_reframer import SmartReframer
from tools.utils import item_error, now_stamp


def _save_report(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"t3_smart_reframer_{now_stamp()}"
    report.to_json(output_dir / f"{base}.json")
    report.to_csv(output_dir / f"{base}.csv")
    report.to_html(output_dir / f"{base}.html")


def main() -> None:
    parser = argparse.ArgumentParser(description="t3_smart_reframer")
    parser.add_argument("--options", help="Path to JSON options")
    parser.add_argument("--output", help="Report output directory")
    parser.add_argument("--dry-run", action="store_true", help="Run without changing Resolve")
    args = parser.parse_args()

    cfg = get_config()
    cfg.dry_run = args.dry_run
    ensure_dirs(cfg)
    setup_logging(cfg)
    logger = get_logger("standalone", tool_id="t3_smart_reframer")

    options = {}
    if args.options:
        options = load_json(Path(args.options))

    ctx = build_context(cfg, dry_run=args.dry_run)
    tool = SmartReframer(ctx)
    try:
        report = tool.run(options)
    except ResolveConnectionError as exc:
        report = Report(tool_id="t3_smart_reframer", title="t3_smart_reframer")
        report.add(item_error("resolve", str(exc)))

    out_dir = Path(args.output) if args.output else cfg.reports_dir
    _save_report(report, out_dir)
    logger.info("Report saved")


if __name__ == "__main__":
    main()
