from typing import Any

from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class TimelineNormalizer(BaseTool):
    tool_id = "t6_timeline_normalizer"
    title = "Timeline Normalizer for Handoff"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        project = self.ctx.resolve.get_project()
        timeline = self.ctx.resolve.get_current_timeline()
        if not project or not timeline:
            report.add(item_error("resolve", "Project or timeline unavailable"))
            return report

        if not timeline.GetName():
            report.add(item_warning("timeline", "Timeline has no name"))

        target_fps = options.get("fps")
        target_res = options.get("resolution")
        settings = timeline.GetSetting() if hasattr(timeline, "GetSetting") else {}

        if target_fps and settings.get("timelineFrameRate") != str(target_fps):
            report.add(item_warning("fps", f"Timeline fps mismatch: {settings.get('timelineFrameRate')} != {target_fps}"))
        if target_res:
            res = f"{settings.get('timelineResolutionWidth')}x{settings.get('timelineResolutionHeight')}"
            if res != target_res:
                report.add(item_warning("resolution", f"Timeline resolution mismatch: {res} != {target_res}"))

        track_count = timeline.GetTrackCount("video") or 0
        clip_names: dict[str, int] = {}
        for idx in range(1, track_count + 1):
            try:
                name = timeline.GetTrackName("video", idx)
            except Exception:
                name = None
            if not name:
                report.add(item_warning("track", f"Video track {idx} has no name"))
            for item in timeline.GetItemListInTrack("video", idx) or []:
                try:
                    clip_name = item.GetName()
                except Exception:
                    clip_name = None
                if clip_name:
                    clip_names[clip_name] = clip_names.get(clip_name, 0) + 1
                try:
                    enabled = item.GetClipEnabled()
                except Exception:
                    enabled = True
                if not enabled:
                    report.add(item_warning("clip", f"Disabled clip: {clip_name or 'unknown'}"))

        for clip_name, count in clip_names.items():
            if count > 1:
                report.add(item_warning("duplicate", f"Duplicate clip name: {clip_name} (x{count})"))

        audio_tracks = timeline.GetTrackCount("audio") or 0
        for idx in range(1, audio_tracks + 1):
            try:
                enabled = timeline.GetIsTrackEnabled("audio", idx)
            except Exception:
                enabled = True
            if not enabled:
                report.add(item_warning("audio", f"Audio track {idx} is muted"))

        offline = _find_offline_media(self.ctx.resolve.get_media_pool())
        for clip in offline:
            report.add(item_error("media", f"Offline media: {clip}"))

        report.add(item_info("summary", "Normalization analysis complete"))
        report.summary = {"offline_media": len(offline)}
        return report


def _find_offline_media(media_pool: Any) -> list[str]:
    offline: list[str] = []
    if not media_pool:
        return offline
    try:
        root = media_pool.GetRootFolder()
        clips = root.GetClipList() or []
    except Exception:
        clips = []
    for clip in clips:
        try:
            props = clip.GetClipProperty() or {}
            if props.get("Offline") == "1":
                offline.append(props.get("File Name") or props.get("Clip Name") or "Unknown")
        except Exception:
            continue
    return offline
