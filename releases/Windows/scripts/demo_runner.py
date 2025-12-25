import json
from pathlib import Path

from core.config import get_config, ensure_dirs
from core.logging import setup_logging, get_logger
from core.reports import Report
from tools.base import build_context
from tools.registry import TOOL_REGISTRY
from tools.utils import item_error, now_stamp
from resolve.resolve_api import ResolveConnectionError


DEMO_OPTIONS = {
    "t1_revision_resolver": {"mapping_pack_path": "presets/mapping_pack.example.json", "scope": "current_timeline"},
    "t2_relink_across_projects": {"mapping_pack_path": "presets/mapping_pack.example.json", "projects": []},
    "t3_smart_reframer": {"formats": ["9x16", "4x5"], "brand_pack_path": "presets/brand_pack.example.json"},
    "t4_caption_layout_protector": {"srt_path": "sample_data/captions.srt", "add_markers": True},
    "t5_feedback_compiler": {"notes_path": "sample_data/feedback.txt", "tasks_output": "sample_data/tasks.json"},
    "t6_timeline_normalizer": {"fps": 30, "resolution": "1920x1080"},
    "t7_component_graphics": {"components": ["logo_bug", "lower_third"], "registry_output": "sample_data/component_registry.json"},
    "t8_delivery_spec_enforcer": {"delivery_pack_path": "presets/delivery_pack.example.json", "platform": "instagram_reel", "manifest_output": "sample_data/manifest.json"},
    "t9_change_impact_analyzer": {"baseline_timeline": "Base", "compare_timeline": "Base_REV"},
    "t10_brand_drift_detector": {"brand_pack_path": "presets/brand_pack.example.json"}
}


def _save_report(report: Report, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"{report.tool_id}_{now_stamp()}"
    report.to_json(output_dir / f"{base}.json")
    report.to_csv(output_dir / f"{base}.csv")
    report.to_html(output_dir / f"{base}.html")


def main() -> None:
    cfg = get_config()
    ensure_dirs(cfg)
    setup_logging(cfg)
    logger = get_logger("demo")

    ctx = build_context(cfg, dry_run=True)
    for tool_id, options in DEMO_OPTIONS.items():
        tool_cls = TOOL_REGISTRY[tool_id]
        tool = tool_cls(ctx)
        logger.info(f"Running demo for {tool_id}")
        try:
            report = tool.run(options)
        except ResolveConnectionError as exc:
            report = Report(tool_id=tool_id, title=tool_id)
            report.add(item_error("resolve", str(exc)))
        _save_report(report, cfg.reports_dir)

    logger.info("Demo run complete")
    print(json.dumps({"reports_dir": str(cfg.reports_dir)}, indent=2))


if __name__ == "__main__":
    main()
