import csv
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from core.fs import atomic_write, ensure_dir


@dataclass
class ReportItem:
    category: str
    severity: str
    message: str
    timeline: Optional[str] = None
    clip: Optional[str] = None
    timecode: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Report:
    tool_id: str
    title: str
    items: list[ReportItem] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: dict[str, Any] = field(default_factory=dict)

    def add(self, item: ReportItem) -> None:
        self.items.append(item)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "title": self.title,
            "created_at": self.created_at,
            "summary": self.summary,
            "items": [asdict(item) for item in self.items],
        }

    def to_json(self, path: Path) -> None:
        ensure_dir(path.parent)
        atomic_write(path, json.dumps(self.to_dict(), indent=2, ensure_ascii=True))

    def to_csv(self, path: Path) -> None:
        ensure_dir(path.parent)
        rows = [asdict(item) for item in self.items]
        if not rows:
            atomic_write(path, "")
            return
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def to_html(self, path: Path) -> None:
        ensure_dir(path.parent)
        html_lines = [
            "<html><head><meta charset='utf-8'>",
            f"<title>{self.title}</title>",
            "</head><body>",
            f"<h1>{self.title}</h1>",
            f"<p>Generated: {self.created_at}</p>",
            "<table border='1' cellspacing='0' cellpadding='4'>",
            "<tr><th>Severity</th><th>Category</th><th>Message</th><th>Timeline</th><th>Clip</th><th>Timecode</th></tr>",
        ]
        for item in self.items:
            html_lines.append(
                "<tr>"
                f"<td>{item.severity}</td>"
                f"<td>{item.category}</td>"
                f"<td>{item.message}</td>"
                f"<td>{item.timeline or ''}</td>"
                f"<td>{item.clip or ''}</td>"
                f"<td>{item.timecode or ''}</td>"
                "</tr>"
            )
        html_lines.extend(["</table>", "</body></html>"])
        atomic_write(path, "\n".join(html_lines))


def merge_reports(reports: Iterable[Report], title: str) -> Report:
    report_list = list(reports)
    merged = Report(tool_id="aggregate", title=title)
    for report in report_list:
        for item in report.items:
            merged.items.append(item)
    merged.summary = {"reports": len(report_list)}
    return merged
