LIMITATIONS = {
    "clip_transform": "Resolve scripting cannot reliably read/modify all clip transforms on every page. Use guided manual adjustment when warnings appear.",
    "fusion_graph": "Fusion node graphs are not fully accessible; component propagation uses naming conventions and manual verification.",
    "subtitle_geometry": "Subtitle bounding boxes are not exposed; caption-safe calculations use heuristic safe zones.",
    "render_settings": "Some render settings may be locked or unavailable via scripting; use generated manifests and checklists.",
    "ui_navigation": "Programmatic selection/jump is limited; reports include timecode and clip name for manual navigation.",
}


def get_limitations() -> dict[str, str]:
    return dict(LIMITATIONS)
