import re
from pathlib import Path
from typing import Any

from core.fs import load_text
from core.reports import Report, ReportItem
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


_SRT_TIME_RE = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})")


def _parse_srt(text: str) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    blocks = text.split("\n\n")
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        time_match = _SRT_TIME_RE.search(lines[1]) if lines[0].isdigit() else _SRT_TIME_RE.search(lines[0])
        if not time_match:
            continue
        start, end = time_match.group(1), time_match.group(2)
        text_lines = lines[2:] if lines[0].isdigit() else lines[1:]
        caption = " ".join(text_lines)
        entries.append((start, end, caption))
    return entries


def _srt_to_timecode(timecode: str) -> str:
    parts = timecode.replace(",", ":").split(":")
    if len(parts) < 4:
        return timecode
    return f"{parts[0]}:{parts[1]}:{parts[2]}:00"


class CaptionLayoutProtector(BaseTool):
    tool_id = "t4_caption_layout_protector"
    title = "Caption-Aware Layout Protector"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        srt_path = options.get("srt_path")
        if not srt_path:
            report.add(item_error("config", "srt_path is required"))
            return report
        srt_path = Path(srt_path)
        if not srt_path.exists():
            report.add(item_error("config", f"SRT not found: {srt_path}"))
            return report
        entries = _parse_srt(load_text(srt_path))
        report.add(item_info("captions", f"Parsed {len(entries)} caption entries"))

        timeline = self.ctx.resolve.get_current_timeline()
        if not timeline:
            report.add(item_warning("resolve", "No active timeline; cannot add markers"))
            return report
        safe_zone = options.get("safe_zone", {"top": 0.1, "bottom": 0.2, "left": 0.05, "right": 0.05})
        add_markers = bool(options.get("add_markers", True))
        for start, end, caption in entries:
            if add_markers:
                frame = timeline.TimecodeToFrame(_srt_to_timecode(start)) if hasattr(timeline, "TimecodeToFrame") else None
                if frame is not None:
                    ok = self.ctx.resolve.add_marker(timeline, frame, "Blue", "Caption Safe", caption)
                    if not ok:
                        report.add(item_warning("marker", f"Failed to add caption marker at {start}"))
            report.add(ReportItem(
                category="caption_safe",
                severity="info",
                message=caption,
                timecode=_srt_to_timecode(start),
                data={"safe_zone": safe_zone, "start": start, "end": end},
            ))
        report.summary = {"captions": len(entries), "safe_zone": safe_zone}
        return report
