import os
import shutil
import subprocess
from typing import Any, Optional

from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class ChangeImpactAnalyzer(BaseTool):
    tool_id = "t9_change_impact_analyzer"
    title = "Change-Impact Analyzer"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        project = self.ctx.resolve.get_project()
        if not project:
            report.add(item_error("resolve", "No active project"))
            return report

        base_name = options.get("baseline_timeline")
        compare_name = options.get("compare_timeline")
        if not base_name or not compare_name:
            report.add(item_error("config", "baseline_timeline and compare_timeline are required"))
            return report

        base = self.ctx.resolve.find_timeline(base_name)
        comp = self.ctx.resolve.find_timeline(compare_name)
        if not base or not comp:
            report.add(item_error("resolve", "Unable to locate timelines"))
            return report

        base_items = _collect_items(base)
        comp_items = _collect_items(comp)
        base_markers = self.ctx.resolve.get_markers(base)
        comp_markers = self.ctx.resolve.get_markers(comp)

        base_set = {(item["name"], item["start"], item["end"]) for item in base_items}
        comp_set = {(item["name"], item["start"], item["end"]) for item in comp_items}

        added = comp_set - base_set
        removed = base_set - comp_set

        for name, start, end in added:
            report.add(item_info("change", f"Added clip: {name}", timecode=str(start)))
        for name, start, end in removed:
            report.add(item_warning("change", f"Removed clip: {name}", timecode=str(start)))

        marker_changes = _diff_markers(base_markers, comp_markers)
        for change in marker_changes:
            report.add(item_info("marker", change))

        base_render = options.get("baseline_render")
        compare_render = options.get("compare_render")
        if base_render and compare_render:
            render_report = _compare_renders(base_render, compare_render)
            for item in render_report:
                report.add(item_warning("render", item))

        report.summary = {"added": len(added), "removed": len(removed), "marker_changes": len(marker_changes)}
        return report


def _collect_items(timeline: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    track_count = timeline.GetTrackCount("video") or 0
    for idx in range(1, track_count + 1):
        for item in timeline.GetItemListInTrack("video", idx) or []:
            try:
                items.append({
                    "name": item.GetName(),
                    "start": item.GetStart(),
                    "end": item.GetEnd(),
                    "track": idx,
                })
            except Exception:
                continue
    return items


def _diff_markers(base_markers: dict, comp_markers: dict) -> list[str]:
    changes: list[str] = []
    base_keys = set(base_markers.keys())
    comp_keys = set(comp_markers.keys())
    for frame in sorted(comp_keys - base_keys):
        marker = comp_markers.get(frame, {})
        changes.append(f"Marker added at {frame}: {marker.get('name', '')}")
    for frame in sorted(base_keys - comp_keys):
        marker = base_markers.get(frame, {})
        changes.append(f"Marker removed at {frame}: {marker.get('name', '')}")
    return changes


def _compare_renders(base_path: str, compare_path: str) -> list[str]:
    items: list[str] = []
    if not os.path.exists(base_path) or not os.path.exists(compare_path):
        return ["Render path(s) missing for comparison"]
    base_size = os.path.getsize(base_path)
    compare_size = os.path.getsize(compare_path)
    if base_size != compare_size:
        items.append(f"File size differs: {base_size} vs {compare_size}")
    duration_base = _probe_duration(base_path)
    duration_comp = _probe_duration(compare_path)
    if duration_base and duration_comp and abs(duration_base - duration_comp) > 0.01:
        items.append(f"Render duration differs: {duration_base:.2f}s vs {duration_comp:.2f}s")
    return items


def _probe_duration(path: str) -> Optional[float]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True,
            text=True,
            check=False,
        )
        return float(result.stdout.strip()) if result.stdout.strip() else None
    except Exception:
        return None
