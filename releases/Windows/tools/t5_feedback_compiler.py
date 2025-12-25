from pathlib import Path
from typing import Any

from core.fs import load_json, load_text, save_json
from core.reports import Report, ReportItem
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning, parse_timecode


_KEYWORDS = {
    "audio": "Orange",
    "sound": "Orange",
    "music": "Orange",
    "caption": "Yellow",
    "text": "Yellow",
    "color": "Purple",
    "grade": "Purple",
    "crop": "Green",
    "reframe": "Green",
}


def _color_for_note(note: str) -> str:
    lower = note.lower()
    for key, color in _KEYWORDS.items():
        if key in lower:
            return color
    return "Blue"


class FeedbackCompiler(BaseTool):
    tool_id = "t5_feedback_compiler"
    title = "Feedback -> Marker -> Task Compiler"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        notes_path = options.get("notes_path")
        if not notes_path:
            report.add(item_error("config", "notes_path is required"))
            return report
        notes_text = load_text(Path(notes_path))
        timeline = self.ctx.resolve.get_current_timeline()
        if not timeline:
            report.add(item_error("resolve", "No active timeline"))
            return report
        status_lookup = _load_task_status(options.get("tasks_input"))

        tasks: list[dict[str, Any]] = []
        for line in [line.strip() for line in notes_text.splitlines() if line.strip()]:
            timecode = parse_timecode(line)
            if not timecode:
                report.add(item_warning("parse", f"No timecode found: {line}"))
                continue
            note = line
            frame = timeline.TimecodeToFrame(timecode) if hasattr(timeline, "TimecodeToFrame") else None
            color = _color_for_note(note)
            if frame is not None:
                self.ctx.resolve.add_marker(timeline, frame, color, "Feedback", note)
            status = status_lookup.get((timecode, note), "todo")
            tasks.append({
                "timecode": timecode,
                "note": note,
                "status": status,
                "category": color.lower(),
            })
            report.add(ReportItem(category="feedback", severity="info", message=note, timecode=timecode))

        export_path = options.get("tasks_output")
        if export_path:
            save_json(Path(export_path), {"tasks": tasks})
            report.add(item_info("export", f"Exported tasks to {export_path}"))
        report.summary = {"tasks": len(tasks)}
        return report


def _load_task_status(path: Any) -> dict[tuple[str, str], str]:
    if not path:
        return {}
    try:
        data = load_json(Path(path))
    except Exception:
        return {}
    lookup: dict[tuple[str, str], str] = {}
    for task in data.get("tasks", []):
        timecode = task.get("timecode")
        note = task.get("note")
        status = task.get("status", "todo")
        if timecode and note:
            lookup[(timecode, note)] = status
    return lookup
