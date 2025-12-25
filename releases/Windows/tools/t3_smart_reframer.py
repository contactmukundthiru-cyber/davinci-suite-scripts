from pathlib import Path
from typing import Any

from core.packs import load_brand_pack
from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class SmartReframer(BaseTool):
    tool_id = "t3_smart_reframer"
    title = "Constraint-Based Smart Reframer"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        project = self.ctx.resolve.get_project()
        if not project:
            report.add(item_error("resolve", "No active project"))
            return report
        timeline = project.GetCurrentTimeline()
        if not timeline:
            report.add(item_error("resolve", "No active timeline"))
            return report

        formats = options.get("formats", ["9x16", "4x5", "1x1"])
        brand_pack = options.get("brand_pack_path")
        layout_constraints: dict[str, Any] = {}
        if brand_pack:
            brand_pack_path = Path(brand_pack)
            data = load_brand_pack(brand_pack_path, self.ctx.cfg)
            layout_constraints = data.get("layout_constraints", {})

        for fmt in formats:
            new_name = f"{timeline.GetName()}_{fmt}"
            dup = self.ctx.resolve.duplicate_timeline(timeline, new_name)
            if not dup:
                report.add(item_warning("timeline", f"Failed to duplicate timeline for {fmt}"))
                continue
            report.add(item_info("timeline", f"Created variant {new_name}"))
            constraints = layout_constraints.get(fmt, {})
            _add_reframe_markers(self.ctx, dup, fmt, constraints, options)
            report.add(item_warning(
                "reframe",
                f"Manual review required for {fmt}; Resolve API cannot auto-apply all transforms",
                timeline=new_name,
                data={"constraints": constraints},
            ))

        report.summary = {"variants": len(formats)}
        return report


def _add_reframe_markers(ctx: Any, timeline: Any, fmt: str, constraints: dict[str, Any], options: dict[str, Any]) -> None:
    add_markers = bool(options.get("add_markers", True))
    if not add_markers or not timeline:
        return
    anchor_track = int(options.get("anchor_track", 1))
    try:
        items = timeline.GetItemListInTrack("video", anchor_track) or []
    except Exception:
        items = []
    note_base = f"Reframe review for {fmt}"
    if constraints:
        note_base += f" | constraints: {constraints}"
    for item in items:
        try:
            frame = item.GetStart()
        except Exception:
            frame = None
        if frame is None:
            continue
        ctx.resolve.add_marker(timeline, frame, "Yellow", "Reframe", note_base)
