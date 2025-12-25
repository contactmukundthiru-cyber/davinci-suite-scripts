# V2 Design

## Goals
- Make every tool operable in a production environment with reliable reports
- Provide a UI that orchestrates Resolve projects, presets, and report review
- Preserve honest API limitations and guide manual interventions clearly

## Major Additions
- Resolve connection status, project/timeline selection, and refresh controls
- Preset system backed by `~/.rps/presets/<tool_id>`
- Report viewer with severity filtering and JSON import
- Pack helpers for mapping/brand/delivery schemas
- Standalone script entrypoints for each tool

## Tool Enhancements (V2)
- T1: token/similarity strategy support, transform warnings, aspect checks
- T2: orchestration output for multi-project relinks
- T3: guided markers for manual reframe review per format
- T4: caption safe-zone metadata in reports
- T5: task reimport for status carry-over
- T6: extra lint checks (disabled clips, duplicate names, muted tracks)
- T8: duration and naming token validation
- T9: marker diffs + optional render comparisons via ffprobe
- T10: brand token drift and missing canonical asset detection

## Known Limits (Still True)
- Clip transforms and Fusion graphs are not fully scriptable
- Subtitle geometry is not exposed in the API
- Render settings are partially locked via scripting
