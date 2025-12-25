from __future__ import annotations

from typing import Any, Optional


def find_items_by_name(timeline: Any, name: str) -> list[Any]:
    items: list[Any] = []
    if not timeline:
        return items
    for track_type in ("video", "audio", "subtitle"):
        track_count = timeline.GetTrackCount(track_type) or 0
        for index in range(1, track_count + 1):
            for item in timeline.GetItemListInTrack(track_type, index) or []:
                try:
                    if item.GetName() == name:
                        items.append(item)
                except Exception:
                    continue
    return items


def timecode_to_frame(timeline: Any, timecode: str) -> Optional[int]:
    try:
        return timeline.TimecodeToFrame(timecode)
    except Exception:
        return None


def find_items_by_timecode(timeline: Any, timecode: str) -> list[Any]:
    items: list[Any] = []
    frame = timecode_to_frame(timeline, timecode)
    if frame is None:
        return items
    for track_type in ("video", "audio", "subtitle"):
        track_count = timeline.GetTrackCount(track_type) or 0
        for index in range(1, track_count + 1):
            for item in timeline.GetItemListInTrack(track_type, index) or []:
                try:
                    if item.GetStart() <= frame <= item.GetEnd():
                        items.append(item)
                except Exception:
                    continue
    return items


def list_track_names(timeline: Any, track_type: str) -> list[str]:
    names: list[str] = []
    if not timeline:
        return names
    track_count = timeline.GetTrackCount(track_type) or 0
    for index in range(1, track_count + 1):
        try:
            name = timeline.GetTrackName(track_type, index)
        except Exception:
            name = None
        if name:
            names.append(name)
    return names
