from pathlib import Path
from typing import Any

from core.fs import save_json
from core.packs import load_mapping_pack
from core.reports import Report
from tools.base import BaseTool
from tools.t1_revision_resolver import RevisionResolver
from tools.utils import item_error, item_info, item_warning


class RelinkAcrossProjects(BaseTool):
    tool_id = "t2_relink_across_projects"
    title = "Relink Across Projects"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        mapping_path = options.get("mapping_pack_path")
        projects = options.get("projects", [])
        if not mapping_path:
            report.add(item_error("config", "mapping_pack_path is required"))
            return report
        if not projects:
            report.add(item_warning("config", "No projects provided; run on current project only"))

        mapping_path = Path(mapping_path)
        _ = load_mapping_pack(mapping_path, self.ctx.cfg)

        pm = self.ctx.resolve.get_project_manager()
        if not pm:
            report.add(item_error("resolve", "Project manager unavailable"))
            return report

        current_project = self.ctx.resolve.get_project()
        if not projects:
            projects = [current_project.GetName()] if current_project else []

        orchestration: list[dict[str, Any]] = []
        for project_name in projects:
            project = pm.LoadProject(project_name)
            if not project:
                report.add(item_error("project", f"Unable to load {project_name}"))
                orchestration.append({"project": project_name, "status": "failed"})
                continue
            resolver = RevisionResolver(self.ctx)
            report.add(item_info("project", f"Applying mapping pack to {project_name}"))
            tool_report = resolver.run({"mapping_pack_path": str(mapping_path)})
            report.items.extend(tool_report.items)
            orchestration.append({"project": project_name, "status": "ok", "items": len(tool_report.items)})

        output_path = options.get("orchestration_output")
        if output_path:
            save_json(Path(output_path), {"projects": orchestration})
            report.add(item_info("export", f"Saved orchestration report to {output_path}"))

        report.summary = {"projects": len(projects), "processed": len(orchestration)}
        return report
