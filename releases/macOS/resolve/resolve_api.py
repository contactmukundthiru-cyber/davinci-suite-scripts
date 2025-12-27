import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from core.config import Config, resolve_script_paths
from core.logging import get_logger


@dataclass
class ResolveObjects:
    resolve: Any
    project_manager: Any
    project: Any
    media_pool: Any
    timeline: Any


class ResolveConnectionError(RuntimeError):
    pass


class ResolveApp:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.logger = get_logger("resolve.api")
        self.objects: Optional[ResolveObjects] = None

    def _inject_paths(self) -> None:
        for path in resolve_script_paths(self.cfg):
            if str(path) not in sys.path:
                sys.path.append(str(path))

    def connect(self) -> ResolveObjects:
        self._inject_paths()
        module_name = os.environ.get("RESOLVE_SCRIPT_MODULE", "DaVinciResolveScript")
        try:
            script = importlib.import_module(module_name)
        except Exception as exc:
            raise ResolveConnectionError(
                "Cannot find DaVinci Resolve. Please ensure:\n"
                "  1. DaVinci Resolve is installed\n"
                "  2. Resolve is running BEFORE clicking Connect\n"
                "  3. In Resolve: Preferences → System → General → Enable 'External scripting using'"
            ) from exc
        resolve = script.scriptapp("Resolve")
        if resolve is None:
            raise ResolveConnectionError(
                "DaVinci Resolve is not responding. Please:\n"
                "  1. Make sure Resolve is open and running\n"
                "  2. Open a project in Resolve first\n"
                "  3. Try clicking Connect again"
            )
        project_manager = resolve.GetProjectManager()
        project = project_manager.GetCurrentProject() if project_manager else None
        media_pool = project.GetMediaPool() if project else None
        timeline = project.GetCurrentTimeline() if project else None
        self.objects = ResolveObjects(resolve=resolve, project_manager=project_manager,
                                      project=project, media_pool=media_pool, timeline=timeline)
        return self.objects

    def require(self) -> ResolveObjects:
        if self.objects is None:
            return self.connect()
        return self.objects

    def get_project_manager(self) -> Any:
        return self.require().project_manager

    def get_project(self) -> Any:
        return self.require().project

    def get_media_pool(self) -> Any:
        return self.require().media_pool

    def get_current_timeline(self) -> Any:
        return self.require().timeline

    def refresh(self) -> ResolveObjects:
        objs = self.require()
        project_manager = objs.project_manager
        project = project_manager.GetCurrentProject() if project_manager else None
        media_pool = project.GetMediaPool() if project else None
        timeline = project.GetCurrentTimeline() if project else None
        self.objects = ResolveObjects(resolve=objs.resolve, project_manager=project_manager,
                                      project=project, media_pool=media_pool, timeline=timeline)
        return self.objects

    def list_projects(self) -> list[str]:
        pm = self.get_project_manager()
        if not pm:
            return []
        try:
            if hasattr(pm, "GetProjectList"):
                return pm.GetProjectList() or []
            if hasattr(pm, "GetProjectsInCurrentFolder"):
                return pm.GetProjectsInCurrentFolder() or []
        except Exception:
            return []
        return []

    def load_project(self, name: str) -> Any:
        pm = self.get_project_manager()
        if not pm:
            return None
        try:
            project = pm.LoadProject(name)
        except Exception:
            return None
        if project:
            self.refresh()
        return project

    def list_timelines(self) -> list[Any]:
        project = self.get_project()
        if not project:
            return []
        timeline_count = project.GetTimelineCount() or 0
        return [project.GetTimelineByIndex(i + 1) for i in range(timeline_count)]

    def list_timeline_names(self) -> list[str]:
        names: list[str] = []
        for timeline in self.list_timelines():
            try:
                name = timeline.GetName()
            except Exception:
                name = None
            if name:
                names.append(name)
        return names

    def find_timeline(self, name: str) -> Optional[Any]:
        for timeline in self.list_timelines():
            if timeline and timeline.GetName() == name:
                return timeline
        return None

    def duplicate_timeline(self, timeline: Any, new_name: str) -> Optional[Any]:
        project = self.get_project()
        if not project:
            return None
        try:
            return project.DuplicateTimeline(timeline, new_name)
        except Exception:
            self.logger.warning("Timeline duplication failed; API may not support duplicate.")
            return None

    def set_current_timeline(self, timeline: Any) -> bool:
        project = self.get_project()
        if not project or not timeline:
            return False
        try:
            ok = project.SetCurrentTimeline(timeline)
        except Exception:
            return False
        self.refresh()
        return bool(ok)

    def get_timeline_items(self, timeline: Any, track_type: str, track_index: int) -> list[Any]:
        try:
            return timeline.GetItemListInTrack(track_type, track_index) or []
        except Exception:
            return []

    def add_marker(self, timeline: Any, frame_id: int, color: str, name: str, note: str) -> bool:
        try:
            return bool(timeline.AddMarker(frame_id, color, name, note, 1))
        except Exception:
            return False

    def get_markers(self, timeline: Any) -> dict:
        try:
            return timeline.GetMarkers() or {}
        except Exception:
            return {}

    def set_clip_color(self, item: Any, color: str) -> bool:
        try:
            return bool(item.SetClipColor(color))
        except Exception:
            return False

    def relink_media(self, media_pool_item: Any, new_paths: list[str]) -> bool:
        try:
            return bool(media_pool_item.ReplaceClip(new_paths[0])) if new_paths else False
        except Exception:
            return False

    def export_project(self, path: str) -> bool:
        pm = self.get_project_manager()
        project = self.get_project()
        try:
            return bool(pm.ExportProject(project.GetName(), path))
        except Exception:
            return False

    def import_project(self, path: str) -> Optional[Any]:
        pm = self.get_project_manager()
        try:
            return pm.ImportProject(path)
        except Exception:
            return None
