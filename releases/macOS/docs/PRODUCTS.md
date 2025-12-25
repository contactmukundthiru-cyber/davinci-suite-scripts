# Product Specifications

Detailed specifications for all 10 tools in the Resolve Production Suite.

---

## Tool 1: Revision Resolver

**ID:** `t1_revision_resolver`
**Category:** Asset Management
**Complexity:** High

### Purpose
Automatically swap old assets with new revisions across all timelines while preserving clip appearance (transforms, effects, timing).

### Key Features
- **Appearance Preservation:** Maintains clip position, scale, rotation, and effects
- **Token/Similarity Matching:** Intelligent asset matching using filename patterns or visual similarity
- **Aspect Ratio Handling:** Warns when new assets have different aspect ratios
- **Transform Warnings:** Flags clips where transforms cannot be safely applied
- **Batch Processing:** Process multiple replacements in a single run

### Use Cases
- Client sends updated logo/graphics - replace across 50+ timelines
- New color-corrected footage arrives - swap without losing edits
- Brand refresh - update all branded elements consistently

### Input Options
```json
{
  "mapping_pack_path": "/path/to/mapping_pack.json",
  "target_timelines": ["Timeline1", "Timeline2"],
  "match_strategy": "token",
  "preserve_transforms": true
}
```

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
**Category:** Asset Management
**Complexity:** High

### Purpose
Roll out brand kit updates across multiple projects simultaneously. Uses Tool 1's core engine for multi-project orchestration.

### Key Features
- **Multi-Project Support:** Update assets across 10, 50, or 100+ projects
- **Brand Kit Integration:** Works with brand packs for consistent rollouts
- **Orchestration Output:** Generates execution plan before applying
- **Rollback Metadata:** Records changes for potential rollback

### Use Cases
- Agency rebrand - update logo across all client projects
- Stock footage replacement - swap placeholder with licensed footage
- Template updates - refresh common elements across project library

### Input Options
```json
{
  "mapping_pack_path": "/path/to/mapping_pack.json",
  "target_projects": ["Project_A", "Project_B", "Project_C"],
  "dry_run": true
}
```

### Output Report
- Projects processed successfully
- Per-project clip replacement counts
- Cross-project consistency verification
- Orchestration execution log

---

## Tool 3: Smart Reframer

**ID:** `t3_smart_reframer`
**Category:** Format Conversion
**Complexity:** High
**Optional Dependencies:** OpenCV, NumPy (for face/saliency detection)

### Purpose
Intelligently reframe content for different aspect ratios (16:9 → 9:16, 1:1, 4:5) using constraint-based algorithms.

### Key Features
- **Face Detection:** Prioritize faces when cropping (requires OpenCV)
- **Saliency Analysis:** Identify important visual elements
- **Constraint-Based:** Define safe zones and priority regions
- **Guided Markers:** Places timeline markers where manual review is needed
- **Multiple Output Formats:** Generate multiple aspect ratios in one pass

### Use Cases
- Create vertical (9:16) cuts for TikTok/Reels from horizontal master
- Generate square (1:1) versions for Instagram feed
- Adapt TV spots for mobile-first platforms

### Input Options
```json
{
  "source_timeline": "Master_16x9",
  "target_formats": ["9:16", "1:1", "4:5"],
  "use_face_detection": true,
  "safe_zone_padding": 10
}
```

### Output Report
- Clips requiring manual reframe review (marked on timeline)
- Face detection confidence scores
- Saliency map analysis results
- Per-format reframe decisions

### Limitations
- Actual transforms must be applied manually (API limitation)
- Complex motion graphics may need manual adjustment
- Face detection accuracy depends on footage quality

---

## Tool 4: Caption Layout Protector

**ID:** `t4_caption_layout_protector`
**Category:** Quality Assurance
**Complexity:** Medium

### Purpose
Ensure captions and subtitles don't overlap with important visual elements or extend beyond safe zones.

### Key Features
- **Safe Zone Analysis:** Checks against broadcast-safe areas
- **Caption Position Verification:** Validates caption placement
- **Overlap Detection:** Identifies potential visual conflicts
- **SRT/VTT Support:** Works with common subtitle formats
- **Timeline Marker Placement:** Flags problem areas on timeline

### Use Cases
- Broadcast delivery compliance checking
- Social media caption safety verification
- Accessibility review for burned-in captions

### Input Options
```json
{
  "caption_file": "/path/to/captions.srt",
  "safe_zone_percentage": 10,
  "check_lower_third": true
}
```

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
**Category:** Workflow Automation
**Complexity:** Low

### Purpose
Convert client feedback notes into timeline markers and task lists for efficient revision tracking.

### Key Features
- **Natural Language Parsing:** Extracts timecodes from feedback text
- **Marker Generation:** Creates color-coded markers on timeline
- **Task List Export:** Generates actionable task lists
- **Status Tracking:** Track completion status across revisions
- **Multiple Input Formats:** Text files, Frame.io exports, spreadsheets

### Use Cases
- Parse client email feedback into actionable markers
- Import Frame.io comments to Resolve timeline
- Create revision checklist from review notes

### Input Options
```json
{
  "feedback_file": "/path/to/feedback.txt",
  "marker_color": "red",
  "create_task_list": true
}
```

### Output Report
- Feedback entries parsed
- Markers created with timecodes
- Task list with priority levels
- Unrecognized entries flagged for review

---

## Tool 6: Timeline Normalizer

**ID:** `t6_timeline_normalizer`
**Category:** Quality Assurance
**Complexity:** Medium

### Purpose
Prepare timelines for handoff by checking and normalizing technical specifications.

### Key Features
- **FPS Verification:** Ensure consistent frame rate
- **Resolution Checks:** Validate timeline resolution settings
- **Disabled Clip Detection:** Find and report disabled clips
- **Duplicate Name Detection:** Identify naming conflicts
- **Muted Track Reporting:** Flag muted audio/video tracks
- **Clean-up Recommendations:** Suggest timeline optimizations

### Use Cases
- Pre-delivery QC check
- Multi-editor project consolidation
- Archive preparation

### Input Options
```json
{
  "expected_fps": 24,
  "expected_resolution": "1920x1080",
  "check_disabled_clips": true,
  "check_muted_tracks": true
}
```

### Output Report
- FPS/resolution mismatches
- List of disabled clips with timecodes
- Duplicate clip names
- Muted track inventory
- Normalization recommendations

---

## Tool 7: Component Graphics System

**ID:** `t7_component_graphics`
**Category:** Asset Management
**Complexity:** Medium

### Purpose
Manage reusable graphics as components with a registry system for consistent usage across projects.

### Key Features
- **Graphics Registry:** Catalog of approved graphic elements
- **Usage Tracking:** Track where components are used
- **Version Control:** Manage graphic versions
- **Consistency Checking:** Verify correct component usage
- **Template Management:** Organize graphics by category/type

### Use Cases
- Maintain brand-approved lower thirds library
- Track logo usage across projects
- Ensure graphics consistency for series/episodes

### Input Options
```json
{
  "registry_path": "/path/to/graphics_registry.json",
  "scan_for_unregistered": true,
  "check_version_consistency": true
}
```

### Output Report
- Registered components found
- Unregistered graphics detected
- Version mismatches
- Usage frequency statistics

---

## Tool 8: Delivery Spec Enforcer

**ID:** `t8_delivery_spec_enforcer`
**Category:** Quality Assurance
**Complexity:** High

### Purpose
Validate render settings and deliverables against platform-specific requirements.

### Key Features
- **Platform Presets:** YouTube, Vimeo, broadcast, streaming specs
- **Codec Validation:** Verify codec compatibility
- **Bitrate Checking:** Ensure adequate quality levels
- **Duration Validation:** Check against platform limits
- **Naming Convention Enforcement:** Validate filename patterns
- **Manifest Generation:** Create delivery checklists

### Use Cases
- Pre-render validation for broadcast delivery
- Social media export verification
- Client deliverable QC

### Input Options
```json
{
  "delivery_pack_path": "/path/to/delivery_pack.json",
  "target_platform": "youtube",
  "check_naming": true
}
```

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
**Category:** Version Control
**Complexity:** High

### Purpose
Compare timeline versions to understand what changed and assess revision impact.

### Key Features
- **Marker Diff:** Compare markers between versions
- **Clip Change Detection:** Identify added/removed/modified clips
- **Timing Analysis:** Track duration changes
- **Visual Comparison:** Optional frame-by-frame comparison (via ffprobe)
- **Change Summary:** Executive summary of revisions

### Use Cases
- Review changes between v1 and v2 of an edit
- Audit revisions before client approval
- Document change history for archives

### Input Options
```json
{
  "baseline_timeline": "Edit_v1",
  "comparison_timeline": "Edit_v2",
  "compare_markers": true,
  "visual_diff": false
}
```

### Output Report
- Added/removed clips with timecodes
- Marker changes
- Duration delta
- Visual difference frames (if enabled)
- Change impact assessment

---

## Tool 10: Brand Drift Detector

**ID:** `t10_brand_drift_detector`
**Category:** Quality Assurance
**Complexity:** Medium

### Purpose
Audit projects for brand guideline compliance and detect unauthorized deviations.

### Key Features
- **Color Compliance:** Check against brand color palette
- **Font Verification:** Detect unauthorized typefaces
- **Logo Usage Audit:** Verify correct logo versions
- **Token Drift Detection:** Find off-brand naming/terminology
- **Missing Asset Detection:** Identify required elements that are absent

### Use Cases
- Agency brand compliance review
- Franchise/multi-location consistency audit
- Pre-delivery brand check

### Input Options
```json
{
  "brand_pack_path": "/path/to/brand_pack.json",
  "check_colors": true,
  "check_fonts": true,
  "check_logos": true
}
```

### Output Report
- Brand compliance score
- Color deviations with hex values
- Unauthorized fonts detected
- Logo version mismatches
- Missing required elements

---

## Pack Formats

### Mapping Pack (Tools 1, 2)
Defines asset replacements:
```json
{
  "schema_version": "1.0",
  "mappings": [
    {
      "old_asset": "logo_v1.png",
      "new_asset": "logo_v2.png",
      "match_strategy": "filename"
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
    "secondary": "#333333"
  },
  "fonts": ["Helvetica Neue", "Arial"],
  "logos": ["approved_logo_v3.png"]
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
    "max_bitrate": "50Mbps"
  },
  "naming_pattern": "{project}_{date}_{version}"
}
```

---

## Common Features (All Tools)

### Report Formats
All tools generate reports in three formats:
- **JSON:** Machine-readable, complete data
- **CSV:** Spreadsheet-compatible
- **HTML:** Human-readable with styling

### Dry Run Mode
All tools support `--dry-run` to preview changes without modifying anything.

### Transaction Logging
All operations are logged with transaction IDs for audit trails.

### Preset System
Save and load tool configurations via the preset system.

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.9 or later |
| DaVinci Resolve | Studio or Free (with scripting enabled) |
| OS | Linux (primary), Windows, macOS |
| RAM | 8GB minimum, 16GB recommended |
| Disk | 500MB for installation |

### Optional Dependencies
| Package | Required For |
|---------|--------------|
| PySide6 | Desktop UI |
| OpenCV | Face detection (Tool 3) |
| NumPy | Saliency analysis (Tool 3) |
| ffprobe | Visual comparison (Tool 9) |
