# User Guide - Resolve Production Suite

Complete documentation for all 10 workflow automation tools.

**Version:** 0.3.8

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Tool 1: Revision Resolver](#tool-1-revision-resolver)
3. [Tool 2: Relink Across Projects](#tool-2-relink-across-projects)
4. [Tool 3: Smart Reframer](#tool-3-smart-reframer)
5. [Tool 4: Caption Layout Protector](#tool-4-caption-layout-protector)
6. [Tool 5: Feedback Compiler](#tool-5-feedback-compiler)
7. [Tool 6: Timeline Normalizer](#tool-6-timeline-normalizer)
8. [Tool 7: Component Graphics](#tool-7-component-graphics)
9. [Tool 8: Delivery Spec Enforcer](#tool-8-delivery-spec-enforcer)
10. [Tool 9: Change Impact Analyzer](#tool-9-change-impact-analyzer)
11. [Tool 10: Brand Drift Detector](#tool-10-brand-drift-detector)
12. [Common Features](#common-features)
13. [Pack Formats](#pack-formats)

---

## Getting Started

### Prerequisites

- DaVinci Resolve (Free or Studio) must be running
- Scripting must be enabled in Resolve preferences
- Suite installed via the installer

### Running Tools

**Command Line:**
```bash
resolve-suite list                              # List all tools
resolve-suite run <tool_id> --options file.json # Run with options
resolve-suite run <tool_id> --dry-run           # Preview without changes
```

**GUI Application:**
```bash
resolve-suite-ui                                # Open the GUI
```

---

## Tool 1: Revision Resolver

**ID:** `t1_revision_resolver`
**Purpose:** Swap old assets with new revisions across all timelines while preserving clip appearance.

### What It Does

When you receive updated assets (new logo, color-corrected footage, revised graphics), this tool:
- Finds all instances of the old asset across your timelines
- Replaces them with the new version
- Preserves clip position, scale, rotation, and effects
- Warns you about aspect ratio mismatches
- Creates markers for clips that need manual attention

### When to Use It

- Client sends an updated logo - replace across 50+ timelines
- New color-corrected footage arrives - swap without losing edits
- Brand refresh - update all branded elements consistently

### Options

```json
{
  "mapping_pack_path": "/path/to/mapping_pack.json",
  "target_timelines": ["Timeline1", "Timeline2"],
  "match_strategy": "token",
  "preserve_transforms": true,
  "dry_run": false
}
```

| Option | Type | Description |
|--------|------|-------------|
| `mapping_pack_path` | string | Path to the mapping pack (defines old → new asset pairs) |
| `target_timelines` | array | List of timeline names to process (empty = all) |
| `match_strategy` | string | How to match assets: `token` (filename) or `similarity` |
| `preserve_transforms` | bool | Keep clip transforms when replacing |
| `dry_run` | bool | Preview changes without applying |

### Output Report

- Clips processed / skipped / failed
- Transform compatibility warnings
- Aspect ratio mismatch alerts
- Manual intervention markers (for unsupported transforms)

### Limitations

- Fusion compositions are not fully scriptable (markers placed for manual review)
- Complex nested timelines may require manual verification

---

## Tool 2: Relink Across Projects

**ID:** `t2_relink_across_projects`
**Purpose:** Roll out brand kit updates across multiple projects simultaneously.

### What It Does

An extension of Tool 1 that works across entire projects:
- Scans multiple projects in your database
- Applies asset replacements consistently across all of them
- Generates a detailed orchestration report
- Records rollback metadata

### When to Use It

- Agency rebrand - update logo across all client projects
- Stock footage replacement - swap placeholder with licensed footage
- Template updates - refresh common elements across project library

### Options

```json
{
  "mapping_pack_path": "/path/to/mapping_pack.json",
  "target_projects": ["Project_A", "Project_B", "Project_C"],
  "dry_run": true
}
```

| Option | Type | Description |
|--------|------|-------------|
| `mapping_pack_path` | string | Path to the mapping pack |
| `target_projects` | array | Project names to process (empty = all) |
| `dry_run` | bool | Preview changes without applying |

### Output Report

- Projects processed successfully
- Per-project clip replacement counts
- Cross-project consistency verification
- Orchestration execution log

---

## Tool 3: Smart Reframer

**ID:** `t3_smart_reframer`
**Purpose:** Intelligently reframe content for different aspect ratios.

### What It Does

Converts your 16:9 master into vertical (9:16), square (1:1), or other formats:
- Detects faces and prioritizes them when cropping
- Analyzes visual saliency (important elements)
- Defines safe zones and priority regions
- Places markers where manual review is needed
- Can generate multiple formats in one pass

### When to Use It

- Create vertical (9:16) cuts for TikTok/Reels from horizontal master
- Generate square (1:1) versions for Instagram feed
- Adapt TV spots for mobile-first platforms

### Options

```json
{
  "source_timeline": "Master_16x9",
  "target_formats": ["9:16", "1:1", "4:5"],
  "use_face_detection": true,
  "safe_zone_padding": 10,
  "dry_run": false
}
```

| Option | Type | Description |
|--------|------|-------------|
| `source_timeline` | string | Name of the source timeline |
| `target_formats` | array | Aspect ratios to generate |
| `use_face_detection` | bool | Prioritize faces (requires Studio) |
| `safe_zone_padding` | int | Padding percentage for safe zones |
| `dry_run` | bool | Preview without creating new timelines |

### Output Report

- Clips requiring manual reframe review (marked on timeline)
- Face detection confidence scores
- Saliency map analysis results
- Per-format reframe decisions

### Limitations

- Actual transforms must be applied manually (API limitation)
- Face detection requires DaVinci Resolve Studio
- Complex motion graphics may need manual adjustment

---

## Tool 4: Caption Layout Protector

**ID:** `t4_caption_layout_protector`
**Purpose:** Ensure captions don't overlap with important visual elements.

### What It Does

Validates your captions and subtitles:
- Checks if captions are within broadcast-safe areas
- Detects potential overlaps with graphics and lower thirds
- Identifies timing conflicts
- Suggests repositioning where needed
- Works with SRT and VTT subtitle files

### When to Use It

- Broadcast delivery compliance checking
- Social media caption safety verification
- Accessibility review for burned-in captions

### Options

```json
{
  "caption_file": "/path/to/captions.srt",
  "safe_zone_percentage": 10,
  "check_lower_third": true,
  "dry_run": false
}
```

| Option | Type | Description |
|--------|------|-------------|
| `caption_file` | string | Path to SRT or VTT file |
| `safe_zone_percentage` | int | Safe zone margin (default 10%) |
| `check_lower_third` | bool | Check for lower third conflicts |
| `dry_run` | bool | Preview without marking timeline |

### Output Report

- Caption entries outside safe zones
- Potential overlap with graphics/lower thirds
- Timing conflicts with on-screen text
- Recommendations for repositioning

### Limitations

- Subtitle geometry not accessible via API (uses heuristics)
- Burn-in position estimated from metadata

---

## Tool 5: Feedback Compiler

**ID:** `t5_feedback_compiler`
**Purpose:** Convert client feedback into timeline markers and task lists.

### What It Does

Takes client feedback notes and:
- Extracts timecodes from natural language text
- Creates color-coded markers on the timeline
- Generates actionable task lists
- Tracks completion status across revisions
- Supports text files, Frame.io exports, spreadsheets

### When to Use It

- Parse client email feedback into actionable markers
- Import Frame.io comments to Resolve timeline
- Create revision checklist from review notes

### Options

```json
{
  "feedback_file": "/path/to/feedback.txt",
  "marker_color": "red",
  "create_task_list": true,
  "output_format": "json"
}
```

| Option | Type | Description |
|--------|------|-------------|
| `feedback_file` | string | Path to feedback file |
| `marker_color` | string | Color for markers (red, blue, green, etc.) |
| `create_task_list` | bool | Generate task list output |
| `output_format` | string | Report format: json, csv, html |

### Feedback File Format

The tool understands natural language feedback:

```
00:15 - The logo appears too early, please delay by 2 seconds
At 1:30, the music is too loud during the voiceover
2:45-3:00 needs to be cut entirely
Around the 4 minute mark, add a transition
```

### Output Report

- Feedback entries parsed
- Markers created with timecodes
- Task list with priority levels
- Unrecognized entries flagged for review

---

## Tool 6: Timeline Normalizer

**ID:** `t6_timeline_normalizer`
**Purpose:** Check and normalize technical specifications for project handoff.

### What It Does

Prepares timelines for handoff by checking:
- Frame rate consistency
- Resolution settings
- Disabled clips (finds hidden problems)
- Duplicate clip names
- Muted audio/video tracks
- Provides clean-up recommendations

### When to Use It

- Pre-delivery QC check
- Multi-editor project consolidation
- Archive preparation
- Before sending to colorist or sound editor

### Options

```json
{
  "expected_fps": 24,
  "expected_resolution": "1920x1080",
  "check_disabled_clips": true,
  "check_muted_tracks": true,
  "check_duplicate_names": true
}
```

| Option | Type | Description |
|--------|------|-------------|
| `expected_fps` | number | Expected frame rate |
| `expected_resolution` | string | Expected resolution (e.g., "1920x1080") |
| `check_disabled_clips` | bool | Find disabled clips |
| `check_muted_tracks` | bool | Report muted tracks |
| `check_duplicate_names` | bool | Find duplicate clip names |

### Output Report

- FPS/resolution mismatches
- List of disabled clips with timecodes
- Duplicate clip names
- Muted track inventory
- Normalization recommendations

---

## Tool 7: Component Graphics

**ID:** `t7_component_graphics`
**Purpose:** Manage reusable graphics with a registry system.

### What It Does

Treats graphics as reusable components:
- Maintains a catalog of approved graphic elements
- Tracks where components are used across projects
- Manages versions of graphics
- Verifies correct component usage
- Organizes graphics by category/type

### When to Use It

- Maintain brand-approved lower thirds library
- Track logo usage across projects
- Ensure graphics consistency for series/episodes

### Options

```json
{
  "registry_path": "/path/to/graphics_registry.json",
  "scan_for_unregistered": true,
  "check_version_consistency": true
}
```

| Option | Type | Description |
|--------|------|-------------|
| `registry_path` | string | Path to graphics registry JSON |
| `scan_for_unregistered` | bool | Find graphics not in registry |
| `check_version_consistency` | bool | Verify version matches |

### Output Report

- Registered components found
- Unregistered graphics detected
- Version mismatches
- Usage frequency statistics

---

## Tool 8: Delivery Spec Enforcer

**ID:** `t8_delivery_spec_enforcer`
**Purpose:** Validate render settings against platform requirements.

### What It Does

Ensures your deliverables meet platform specs:
- Checks against YouTube, Vimeo, broadcast specs
- Validates codec compatibility
- Verifies bitrate is adequate
- Checks duration against platform limits
- Enforces naming conventions
- Generates delivery checklists

### When to Use It

- Pre-render validation for broadcast delivery
- Social media export verification
- Client deliverable QC

### Options

```json
{
  "delivery_pack_path": "/path/to/delivery_pack.json",
  "target_platform": "youtube",
  "check_naming": true,
  "expected_duration": "00:30:00"
}
```

| Option | Type | Description |
|--------|------|-------------|
| `delivery_pack_path` | string | Path to delivery specs pack |
| `target_platform` | string | Platform: youtube, vimeo, broadcast, etc. |
| `check_naming` | bool | Validate filename patterns |
| `expected_duration` | string | Expected duration (optional) |

### Built-in Platforms

- YouTube (various quality presets)
- Vimeo
- Instagram (feed, stories, reels)
- TikTok
- Broadcast (various standards)
- Custom (via delivery pack)

### Output Report

- Spec compliance status
- Settings that need adjustment
- Naming convention violations
- Generated delivery manifest/checklist

### Limitations

- Some render settings not accessible via API
- Generates checklist for manual verification when needed

---

## Tool 9: Change Impact Analyzer

**ID:** `t9_change_impact_analyzer`
**Purpose:** Compare timeline versions to understand what changed.

### What It Does

Compares two versions of a timeline:
- Identifies added/removed/modified clips
- Compares markers between versions
- Analyzes duration changes
- Optional frame-by-frame visual comparison
- Generates executive summary of revisions

### When to Use It

- Review changes between v1 and v2 of an edit
- Audit revisions before client approval
- Document change history for archives

### Options

```json
{
  "baseline_timeline": "Edit_v1",
  "comparison_timeline": "Edit_v2",
  "compare_markers": true,
  "visual_diff": false,
  "generate_summary": true
}
```

| Option | Type | Description |
|--------|------|-------------|
| `baseline_timeline` | string | Original timeline name |
| `comparison_timeline` | string | Modified timeline name |
| `compare_markers` | bool | Include marker comparison |
| `visual_diff` | bool | Generate frame comparisons (slow) |
| `generate_summary` | bool | Create executive summary |

### Output Report

- Added/removed clips with timecodes
- Marker changes
- Duration delta
- Visual difference frames (if enabled)
- Change impact assessment

---

## Tool 10: Brand Drift Detector

**ID:** `t10_brand_drift_detector`
**Purpose:** Audit projects for brand guideline compliance.

### What It Does

Scans your project for brand violations:
- Checks colors against approved palette
- Detects unauthorized typefaces
- Verifies correct logo versions are used
- Finds off-brand naming/terminology
- Identifies missing required elements

### When to Use It

- Agency brand compliance review
- Franchise/multi-location consistency audit
- Pre-delivery brand check

### Options

```json
{
  "brand_pack_path": "/path/to/brand_pack.json",
  "check_colors": true,
  "check_fonts": true,
  "check_logos": true,
  "check_terminology": true
}
```

| Option | Type | Description |
|--------|------|-------------|
| `brand_pack_path` | string | Path to brand guidelines pack |
| `check_colors` | bool | Verify color compliance |
| `check_fonts` | bool | Check for unauthorized fonts |
| `check_logos` | bool | Verify logo versions |
| `check_terminology` | bool | Check naming conventions |

### Output Report

- Brand compliance score
- Color deviations with hex values
- Unauthorized fonts detected
- Logo version mismatches
- Missing required elements

---

## Common Features

All tools share these capabilities:

### Dry Run Mode

Preview changes without modifying anything:
```bash
resolve-suite run <tool_id> --dry-run
```

### Report Formats

All tools generate reports in three formats:
- **JSON** - Machine-readable, complete data
- **CSV** - Spreadsheet-compatible
- **HTML** - Human-readable with styling

Reports are saved to `~/.rps/reports/` by default.

### Transaction Logging

All operations are logged with transaction IDs for audit trails.

### Preset System

Save and load tool configurations:
```bash
resolve-suite preset save <tool_id> my_preset
resolve-suite preset load <tool_id> my_preset
```

Presets are stored in `~/.rps/presets/<tool_id>/`.

---

## Pack Formats

### Mapping Pack (Tools 1, 2)

Defines asset replacement mappings:

```json
{
  "schema_version": "1.0",
  "mappings": [
    {
      "old_asset": "logo_v1.png",
      "new_asset": "logo_v2.png",
      "match_strategy": "filename"
    },
    {
      "old_asset": "placeholder_footage.mp4",
      "new_asset": "licensed_footage.mp4",
      "match_strategy": "token"
    }
  ]
}
```

### Brand Pack (Tools 3, 10)

Defines brand guidelines:

```json
{
  "schema_version": "1.0",
  "colors": {
    "primary": "#FF5500",
    "secondary": "#333333",
    "accent": "#00AAFF"
  },
  "fonts": ["Helvetica Neue", "Arial", "Open Sans"],
  "logos": ["approved_logo_v3.png", "logo_white.png"],
  "terminology": {
    "product_name": "Acme Widget",
    "company_name": "Acme Corp"
  }
}
```

### Delivery Pack (Tool 8)

Defines output specifications:

```json
{
  "schema_version": "1.0",
  "platform": "youtube",
  "specs": {
    "codec": "h264",
    "resolution": "1920x1080",
    "fps": 30,
    "max_bitrate": "50Mbps",
    "audio_codec": "aac",
    "audio_bitrate": "320kbps"
  },
  "naming_pattern": "{project}_{date}_{version}",
  "required_elements": ["logo_intro", "end_card"]
}
```

---

## Getting Help

- **Email:** contactmukundthiru@gmail.com
- **GitHub:** https://github.com/contactmukundthiru-cyber/davinci-suite-scripts/issues
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
