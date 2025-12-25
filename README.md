# Resolve Production Suite

Commercial-grade, Linux-first production tools for DaVinci Resolve Studio/Free. This v2 suite focuses on revision speed, consistency, and deliverable correctness for high-volume agencies and editors.

## Highlights
- 10 workflow insurance tools with unified reports, presets, and pack formats.
- Linux-first (Windows/macOS supported where feasible).
- External UI v2 (PySide6) plus CLI automation, presets, and report viewer.
- Deterministic reporting, dry-run support, centralized logging.

## Tools
1. Revision Resolver (appearance-preserving asset swap)
2. Relink Across Projects (brand kit rollout)
3. Constraint-Based Smart Reframer
4. Caption-Aware Layout Protector
5. Feedback -> Marker -> Task Compiler
6. Timeline Normalizer for Handoff
7. Component-Style Graphics System
8. Delivery Spec Enforcer
9. Change-Impact Analyzer
10. Project Audit & Brand Drift Detector

## Resolve API Limits (Honest Notes)
- Clip transforms and Fusion graphs are not fully scriptable. Where transforms cannot be safely applied, the tools generate guided fix lists and markers.
- Subtitle geometry is not accessible. Caption-safe uses safe zone heuristics.
- Some render settings are unavailable. Delivery tool generates a manifest/checklist instead of auto-applying unsupported settings.

## Repo Layout
- `core/`: shared engine (config, logging, reports, schema validation)
- `resolve/`: Resolve scripting wrapper + limitations
- `tools/`: the 10 tool modules
- `ui/`: PySide6 UI app
- `schemas/`: JSON schemas for Mapping/Brand/Delivery packs
- `presets/`: example packs
- `scripts/`: demo runner + sample pack generator
- `docs/`: installation and usage

## Installation

### Standalone Installer (Recommended)
Download and run the installer for your platform - no Python required:
- **Windows:** `ResolveProductionSuite-Setup.exe`
- **macOS:** `ResolveProductionSuite-Setup`
- **Linux:** `ResolveProductionSuite-Setup`

Just double-click and follow the prompts!

### From Source (Developers)
```bash
# Linux/macOS
./install.sh

# Windows PowerShell
.\install.ps1
```

### Build Standalone Installer
To build the standalone installer yourself:
```bash
pip install pyinstaller
python build.py
# Output: dist/ResolveProductionSuite-Setup.exe (Windows)
#         dist/ResolveProductionSuite-Setup (macOS/Linux)
```

## Documentation
- [docs/INSTALL.md](docs/INSTALL.md) - Detailed installation guide
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Quick start guide
- [docs/V2_DESIGN.md](docs/V2_DESIGN.md) - V2 design notes
- [docs/STANDALONE_SCRIPTS.md](docs/STANDALONE_SCRIPTS.md) - Standalone script documentation

Each tool also has a standalone bundle under `products/` with its own README and packaging files.

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Support
- Email: contactmukundthiru@gmail.com
- Open an issue on GitHub for bugs or feature requests
- Contributions welcome via pull requests
