import os
from pathlib import Path
from typing import Any, Optional

from core.packs import load_mapping_pack
from core.reports import Report
from core.similarity import best_match, normalize, similarity_ratio, tokenize
from tools.base import BaseTool
from tools.utils import item_error, item_info, item_warning


class RevisionResolver(BaseTool):
    tool_id = "t1_revision_resolver"
    title = "Revision Resolver"

    def run(self, options: dict[str, Any]) -> Report:
        report = Report(tool_id=self.tool_id, title=self.title)
        mapping_path = options.get("mapping_pack_path")
        if not mapping_path:
            report.add(item_error("config", "mapping_pack_path is required"))
            return report
        mapping_path = Path(mapping_path)
        if not mapping_path.exists():
            report.add(item_error("config", f"Mapping pack not found: {mapping_path}"))
            return report
        mapping = load_mapping_pack(mapping_path, self.ctx.cfg)

        project = self.ctx.resolve.get_project()
        media_pool = self.ctx.resolve.get_media_pool()
        if not project or not media_pool:
            report.add(item_error("resolve", "Resolve project/media pool unavailable"))
            return report

        scope = options.get("scope", "current_timeline")
        if scope not in ("current_timeline", "all_timelines", "selected_bins", "selected_clips"):
            report.add(item_warning("scope", f"Unknown scope: {scope}, defaulting to current_timeline"))
            scope = "current_timeline"
        if scope != "current_timeline":
            report.add(item_warning(
                "scope",
                f"Scope {scope} requested; Resolve API limits automated selection. Running on media pool items only."
            ))
        duplicate = bool(options.get("duplicate_timeline", True))
        if duplicate:
            timeline = project.GetCurrentTimeline()
            if timeline:
                name = timeline.GetName() + "_REV"
                dup = self.ctx.resolve.duplicate_timeline(timeline, name)
                if dup:
                    project.SetCurrentTimeline(dup)
                    report.add(item_info("timeline", f"Duplicated timeline to {name}"))
                else:
                    report.add(item_warning("timeline", "Timeline duplication failed; continuing on current timeline"))

        replacement_index = _build_replacement_index(mapping)
        media_items = _collect_media_items(media_pool)
        if not media_items:
            report.add(item_warning("resolve", "No media pool items found"))
            return report

        for item in media_items:
            props = _clip_props(item)
            name = props.get("File Name") or props.get("Clip Name") or ""
            if not name:
                continue
            target, rule = _map_target(name, mapping, replacement_index)
            if not target:
                continue
            if _has_transform(props):
                report.add(item_warning(
                    "appearance",
                    f"Clip may have transforms; verify framing after relink: {name}",
                    clip=name,
                    data={"transform_fields": _transform_fields(props)},
                ))
            expected_res = rule.get("expected_resolution") if rule else None
            clip_res = _extract_resolution(props)
            if expected_res and clip_res and expected_res != clip_res:
                report.add(item_warning(
                    "resolution",
                    f"Clip resolution {clip_res} differs from expected {expected_res}",
                    clip=name,
                ))
            expected_aspect = rule.get("expected_aspect") if rule else None
            if expected_aspect and clip_res:
                aspect = _aspect_ratio_from_resolution(clip_res)
                if aspect and abs(aspect - expected_aspect) > mapping.get("aspect_tolerance", 0.05):
                    report.add(item_warning(
                        "aspect",
                        f"Clip aspect {aspect:.2f} differs from expected {expected_aspect}",
                        clip=name,
                    ))
            if self.ctx.transaction.dry_run:
                report.add(item_info("swap", f"Dry run: relink {name} -> {target}"))
                self.ctx.transaction.record({"action": "relink", "clip": name, "target": target, "dry_run": True})
                continue
            ok = self.ctx.resolve.relink_media(item, [target])
            if ok:
                report.add(item_info("swap", f"Relinked {name} -> {target}"))
                self.ctx.transaction.record({"action": "relink", "clip": name, "target": target, "dry_run": False})
            else:
                report.add(item_error("swap", f"Failed to relink {name} -> {target}"))

        report.summary = {"items_scanned": len(media_items)}
        return report


def _collect_media_items(media_pool: Any) -> list[Any]:
    try:
        root = media_pool.GetRootFolder()
        return root.GetClipList() or []
    except Exception:
        return []


def _clip_props(item: Any) -> dict[str, Any]:
    try:
        return item.GetClipProperty() or {}
    except Exception:
        return {}


def _has_transform(props: dict[str, Any]) -> bool:
    for key in props.keys():
        lowered = key.lower()
        if "zoom" in lowered or "pan" in lowered or "position" in lowered:
            return True
    return False


def _build_replacement_index(mapping: dict[str, Any]) -> dict[str, str]:
    index: dict[str, str] = {}
    roots = mapping.get("root_folders", [])
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                index[normalize(filename)] = str(Path(dirpath) / filename)
    return index


def _map_target(name: str, mapping: dict[str, Any], index: dict[str, str]) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    rules = mapping.get("rules", [])
    normalized = normalize(name)
    for rule in rules:
        source = normalize(rule.get("source", ""))
        strategy = rule.get("strategy", "exact")
        if source and source == normalized and strategy in ("", "exact"):
            return rule.get("target"), rule
        if strategy == "regex":
            import re

            if re.search(rule.get("source", ""), name, flags=re.IGNORECASE):
                return rule.get("target"), rule
        if strategy == "token":
            if _tokens_match(source, normalized):
                return rule.get("target"), rule
        if strategy == "similarity":
            threshold = rule.get("similarity_threshold", mapping.get("similarity_threshold", 0.9))
            if similarity_ratio(source, normalized) >= threshold:
                return rule.get("target"), rule
    if normalized in index:
        return index[normalized], {}
    best = best_match(name, index.keys())
    if best and best.score >= mapping.get("similarity_threshold", 0.9):
        return index[best.candidate], {}
    return None, None


def _tokens_match(source: str, target: str) -> bool:
    source_tokens = set(tokenize(source))
    target_tokens = set(tokenize(target))
    if not source_tokens:
        return False
    return source_tokens.issubset(target_tokens)


def _transform_fields(props: dict[str, Any]) -> dict[str, Any]:
    fields = {}
    for key, value in props.items():
        lowered = key.lower()
        if "zoom" in lowered or "pan" in lowered or "position" in lowered or "rotation" in lowered:
            fields[key] = value
    return fields


def _extract_resolution(props: dict[str, Any]) -> Optional[str]:
    for key in ("Resolution", "Clip Resolution", "Source Resolution"):
        value = props.get(key)
        if value and "x" in value:
            return value
    return None


def _aspect_ratio_from_resolution(resolution: str) -> Optional[float]:
    try:
        width, height = resolution.lower().split("x", 1)
        return int(width) / int(height)
    except Exception:
        return None
