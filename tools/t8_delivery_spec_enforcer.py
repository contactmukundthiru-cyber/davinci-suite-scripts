from pathlib import Path
from typing import Any, Optional

from core.fs import save_json
from core.packs import load_delivery_pack
from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class DeliverySpecEnforcer(BaseTool):
    tool_id = "t8_delivery_spec_enforcer"
    title = "Delivery Spec Enforcer"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        pack_path = options.get("delivery_pack_path")
        if not pack_path:
            report.add(item_error("config", "delivery_pack_path is required"))
            return report
        pack_path = Path(pack_path)
        pack = load_delivery_pack(pack_path, self.ctx.cfg)

        project = self.ctx.resolve.get_project()
        timeline = self.ctx.resolve.get_current_timeline()
        if not project or not timeline:
            report.add(item_error("resolve", "Project/timeline unavailable"))
            return report
        settings = timeline.GetSetting() if hasattr(timeline, "GetSetting") else {}

        platform = options.get("platform")
        if platform not in pack.get("platforms", {}):
            report.add(item_error("config", f"Platform not defined in pack: {platform}"))
            return report
        spec = pack["platforms"][platform]
        report.add(item_warning(
            "render",
            "Resolve scripting may not expose all render settings; validate render page manually."
        ))

        expected_res = spec.get("resolution")
        expected_fps = spec.get("fps")
        duration_limit = spec.get("duration_limit")
        current_res = f"{settings.get('timelineResolutionWidth')}x{settings.get('timelineResolutionHeight')}"
        if expected_res and current_res != expected_res:
            report.add(item_warning("resolution", f"Timeline resolution {current_res} != {expected_res}"))
        if expected_fps and settings.get("timelineFrameRate") != str(expected_fps):
            report.add(item_warning("fps", f"Timeline fps {settings.get('timelineFrameRate')} != {expected_fps}"))
        if duration_limit:
            duration = _timeline_duration_seconds(timeline, settings.get("timelineFrameRate"))
            if duration and duration > duration_limit:
                report.add(item_warning("duration", f"Timeline duration {duration:.2f}s exceeds {duration_limit}s"))

        output_name = options.get("output_name")
        naming_tokens = spec.get("naming_tokens", [])
        if output_name and naming_tokens:
            missing = [token for token in naming_tokens if token not in output_name]
            if missing:
                report.add(item_warning("naming", f"Missing naming tokens: {', '.join(missing)}"))

        manifest = {
            "platform": platform,
            "spec": spec,
            "timeline": timeline.GetName(),
            "status": "needs_review" if report.items else "ok",
        }
        output_path = options.get("manifest_output")
        if output_path:
            save_json(Path(output_path), manifest)
            report.add(item_info("export", f"Saved manifest to {output_path}"))

        report.summary = {"platform": platform}
        return report


def _timeline_duration_seconds(timeline: Any, fps_value: Any) -> Optional[float]:
    try:
        start = timeline.GetStartFrame()
        end = timeline.GetEndFrame()
    except Exception:
        return None
    try:
        fps = float(fps_value) if fps_value else None
    except Exception:
        fps = None
    if fps and end is not None and start is not None:
        return max(0, (end - start) / fps)
    return None
