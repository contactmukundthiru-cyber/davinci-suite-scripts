import re
from datetime import datetime
from typing import Any, Optional

from core.reports import ReportItem


_TIME_RE = re.compile(
    r"(?P<h>\d+):(\d{2}):(\d{2})(:(?P<f>\d{2}))?|(?P<m>\d+)m(?P<s>\d+)s|(?P<s_only>\d+)s"
)


def parse_timecode(text: str) -> Optional[str]:
    match = _TIME_RE.search(text)
    if not match:
        return None
    if match.group("h"):
        h = int(match.group("h"))
        m = int(match.group(2))
        s = int(match.group(3))
        f = match.group("f")
        if f is None:
            return f"{h:02d}:{m:02d}:{s:02d}:00"
        return f"{h:02d}:{m:02d}:{s:02d}:{int(f):02d}"
    if match.group("m"):
        m = int(match.group("m"))
        s = int(match.group("s"))
        return f"00:{m:02d}:{s:02d}:00"
    if match.group("s_only"):
        s = int(match.group("s_only"))
        return f"00:00:{s:02d}:00"
    return None


def now_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def item_warning(category: str, message: str, **kwargs: Any) -> ReportItem:
    return ReportItem(category=category, severity="warning", message=message, **kwargs)


def item_error(category: str, message: str, **kwargs: Any) -> ReportItem:
    return ReportItem(category=category, severity="error", message=message, **kwargs)


def item_info(category: str, message: str, **kwargs: Any) -> ReportItem:
    return ReportItem(category=category, severity="info", message=message, **kwargs)
