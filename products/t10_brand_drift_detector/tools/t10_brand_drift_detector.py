from pathlib import Path
from typing import Any

from core.packs import load_brand_pack
from core.reports import Report
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class BrandDriftDetector(BaseTool):
    tool_id = "t10_brand_drift_detector"
    title = "Project Audit & Brand Drift Detector"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        pack_path = options.get("brand_pack_path")
        if not pack_path:
            report.add(item_error("config", "brand_pack_path is required"))
            return report
        pack_path = Path(pack_path)
        pack = load_brand_pack(pack_path, self.ctx.cfg)

        media_pool = self.ctx.resolve.get_media_pool()
        if not media_pool:
            report.add(item_error("resolve", "Media pool unavailable"))
            return report

        canonical = set(pack.get("canonical_assets", []))
        fonts = set(pack.get("fonts", []))
        colors = set(pack.get("color_palette", []))
        brand_tokens = set(pack.get("brand_tokens", []))

        clips = _collect_media_items(media_pool)
        clip_names = []
        for clip in clips:
            name = clip.get("File Name") or clip.get("Clip Name") or ""
            clip_names.append(name)
            if canonical and name and name not in canonical:
                report.add(item_warning("asset", f"Non-canonical asset: {name}"))
            if brand_tokens and name:
                lowered = name.lower()
                if any(token.lower() in lowered for token in brand_tokens) and name not in canonical:
                    report.add(item_warning("brand_token", f"Potential off-brand asset: {name}"))

        missing_canonical = [asset for asset in canonical if asset not in clip_names]
        for asset in missing_canonical:
            report.add(item_warning("asset", f"Missing canonical asset: {asset}"))

        if not fonts:
            report.add(item_warning("fonts", "No fonts defined in brand pack"))
        else:
            report.add(item_info("fonts", "Font drift requires manual verification via text generators"))

        if colors:
            report.add(item_info("colors", "Color drift uses LUT/node naming heuristics; manual check required"))

        report.summary = {"assets_scanned": len(clips), "missing_canonical": len(missing_canonical)}
        return report


def _collect_media_items(media_pool: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    try:
        root = media_pool.GetRootFolder()
        clips = root.GetClipList() or []
    except Exception:
        clips = []
    for clip in clips:
        try:
            items.append(clip.GetClipProperty() or {})
        except Exception:
            continue
    return items
