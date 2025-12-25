# Test Plan

## Objectives
- Validate deterministic reports and schema validation
- Ensure safe dry-run behavior
- Confirm Resolve connection handling and failure modes

## Unit Tests (Proposed)
- `core.similarity` Levenshtein + matching thresholds
- `core.fs` atomic writes
- `core.jsonschema` schema validation
- `tools.utils.parse_timecode` parsing coverage

## Integration Tests (Manual)
- Connect to Resolve with active project
- Run each tool with sample options
- Verify reports written to `~/.rps/reports`
- UI: connect, select project/timeline, run tool, open report

## Regression Checklist
- Tools run in dry-run with no Resolve changes
- Schema validation fails on malformed packs
- Reports include `tool_id`, `created_at`, `summary`, `items`

## Optional Dependencies
- If OpenCV/ffmpeg/ffprobe are installed, validate optional analysis paths (not required for core functionality).
