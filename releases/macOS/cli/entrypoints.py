import argparse
from pathlib import Path

from core.config import get_config, ensure_dirs
from core.fs import load_json
from core.logging import get_logger, setup_logging
from core.reports import Report
from resolve.resolve_api import ResolveConnectionError
from tools.base import build_context
from tools.registry import TOOL_REGISTRY
from tools.utils import item_error, now_stamp


def _save_report(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{report.tool_id}_{now_stamp()}"
    report.to_json(output_dir / f"{base}.json")
    report.to_csv(output_dir / f"{base}.csv")
    report.to_html(output_dir / f"{base}.html")


def _run_tool(tool_id: str) -> None:
    parser = argparse.ArgumentParser(description=f"Resolve Production Suite - {tool_id}")
    parser.add_argument("--options", help="Path to JSON options")
    parser.add_argument("--output", help="Report output directory")
    parser.add_argument("--dry-run", action="store_true", help="Run without changing Resolve")
    args = parser.parse_args()

    cfg = get_config()
    cfg.dry_run = args.dry_run
    ensure_dirs(cfg)
    setup_logging(cfg)
    logger = get_logger("cli", tool_id=tool_id)

    if tool_id not in TOOL_REGISTRY:
        raise SystemExit(f"Unknown tool_id: {tool_id}")

    options = {}
    if args.options:
        options = load_json(Path(args.options))

    ctx = build_context(cfg, dry_run=args.dry_run)
    ctx.logger = get_logger("tool", tool_id=tool_id, tx_id=ctx.transaction.transaction_id)
    tool_cls = TOOL_REGISTRY[tool_id]
    tool = tool_cls(ctx)
    try:
        report = tool.run(options)
    except ResolveConnectionError as exc:
        report = Report(tool_id=tool_id, title=tool_id)
        report.add(item_error("resolve", str(exc)))

    out_dir = Path(args.output) if args.output else cfg.reports_dir
    _save_report(report, out_dir)
    logger.info("Report saved", extra={"rps_tool_id": tool_id})


def t1_revision_resolver() -> None:
    _run_tool("t1_revision_resolver")


def t2_relink_across_projects() -> None:
    _run_tool("t2_relink_across_projects")


def t3_smart_reframer() -> None:
    _run_tool("t3_smart_reframer")


def t4_caption_layout_protector() -> None:
    _run_tool("t4_caption_layout_protector")


def t5_feedback_compiler() -> None:
    _run_tool("t5_feedback_compiler")


def t6_timeline_normalizer() -> None:
    _run_tool("t6_timeline_normalizer")


def t7_component_graphics() -> None:
    _run_tool("t7_component_graphics")


def t8_delivery_spec_enforcer() -> None:
    _run_tool("t8_delivery_spec_enforcer")


def t9_change_impact_analyzer() -> None:
    _run_tool("t9_change_impact_analyzer")


def t10_brand_drift_detector() -> None:
    _run_tool("t10_brand_drift_detector")
