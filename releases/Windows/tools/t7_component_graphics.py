from pathlib import Path
from typing import Any

from core.fs import save_json
from tools.utils import now_stamp
from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class ComponentGraphicsSystem(BaseTool):
    tool_id = "t7_component_graphics"
    title = "Component-Style Graphics System"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        project = self.ctx.resolve.get_project()
        media_pool = self.ctx.resolve.get_media_pool()
        if not project or not media_pool:
            report.add(item_error("resolve", "Project/media pool unavailable"))
            return report

        components = options.get("components", [])
        if not components:
            report.add(item_warning("config", "No components specified"))

        registry: dict[str, Any] = {}
        for comp in components:
            found = _find_media_by_name(media_pool, comp)
            if not found:
                report.add(item_warning("component", f"Component not found: {comp}"))
                continue
            registry[comp] = {"count": len(found)}
            report.add(item_info("component", f"Found {len(found)} instances for {comp}"))

        updates = options.get("component_updates", [])
        for update in updates:
            name = update.get("name")
            new_path = update.get("new_path")
            if not name or not new_path:
                report.add(item_warning("component", "Invalid component update entry"))
                continue
            found = _find_media_by_name(media_pool, name)
            if not found:
                report.add(item_warning("component", f"No component found for update: {name}"))
                continue
            if self.ctx.transaction.dry_run:
                report.add(item_info("component", f"Dry run: update {name} -> {new_path}"))
                continue
            ok = self.ctx.resolve.relink_media(found[0], [new_path])
            if ok:
                report.add(item_info("component", f"Updated component {name} -> {new_path}"))
            else:
                report.add(item_warning("component", f"Failed to update component {name}"))

        output_path = options.get("registry_output")
        if output_path:
            save_json(Path(output_path), {"components": registry, "version": options.get("version", "v2"), "stamp": now_stamp()})
            report.add(item_info("export", f"Saved registry to {output_path}"))

        report.summary = {"components": len(registry)}
        return report


def _find_media_by_name(media_pool: Any, name: str) -> list[Any]:
    results: list[Any] = []
    try:
        root = media_pool.GetRootFolder()
        clips = root.GetClipList() or []
    except Exception:
        clips = []
    for clip in clips:
        try:
            props = clip.GetClipProperty() or {}
            if props.get("Clip Name") == name or props.get("File Name") == name:
                results.append(clip)
        except Exception:
            continue
    return results
