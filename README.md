# Resolve Production Suite

Professional workflow automation tools for DaVinci Resolve Studio/Free. This suite focuses on revision speed, consistency, and deliverable correctness for high-volume agencies and editors.

**Current Version:** 0.3.3

## Quick Start

### Windows
1. Download `ResolveProductionSuite-Windows.zip`
2. Extract the folder
3. Double-click `CLICK_ME_FIRST.bat`
4. Follow the on-screen menu

### macOS
1. Download `ResolveProductionSuite-macOS.zip`
2. Extract the folder
3. Double-click `DOUBLE_CLICK_ME.command`
4. Follow the on-screen menu

The installer will automatically download Python if needed and set everything up for you.

## What's Included

10 workflow automation tools for DaVinci Resolve:

| # | Tool | What It Does |
|---|------|--------------|
| 1 | **Revision Resolver** | Swap old assets with new versions while preserving clip appearance (transforms, effects, timing) |
| 2 | **Relink Across Projects** | Roll out brand kit updates across multiple projects simultaneously |
| 3 | **Smart Reframer** | Intelligently reframe content for different aspect ratios (16:9 → 9:16, 1:1, 4:5) |
| 4 | **Caption Layout Protector** | Ensure captions don't overlap with important visual elements |
| 5 | **Feedback Compiler** | Convert client feedback notes into timeline markers and task lists |
| 6 | **Timeline Normalizer** | Check and normalize technical specs for project handoff |
| 7 | **Component Graphics** | Manage reusable graphics with a registry system |
| 8 | **Delivery Spec Enforcer** | Validate render settings against platform requirements |
| 9 | **Change Impact Analyzer** | Compare timeline versions to understand what changed |
| 10 | **Brand Drift Detector** | Audit projects for brand guideline compliance |

## Features

- **Automatic Updates**: Check for updates directly from the app
- **Easy Installation**: One-click installer handles Python and dependencies
- **Uninstall Support**: Clean removal via the installer menu
- **Detailed Reports**: All tools generate JSON, CSV, and HTML reports
- **Dry Run Mode**: Preview changes before applying them
- **Preset System**: Save and load tool configurations

## Documentation

- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - Complete tool documentation
- [docs/PRODUCTS.md](docs/PRODUCTS.md) - Detailed specifications for each tool
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues and solutions

## System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 or macOS 10.15+ |
| Python | 3.9 or later (auto-installed) |
| DaVinci Resolve | Studio or Free (with scripting enabled) |
| RAM | 8GB minimum, 16GB recommended |
| Disk | 500MB for installation |

## Resolve API Notes

- Clip transforms and Fusion graphs are not fully scriptable. Where transforms cannot be safely applied, the tools generate guided fix lists and markers.
- Subtitle geometry is not accessible. Caption-safe uses safe zone heuristics.
- Some render settings are unavailable. Delivery tool generates a manifest/checklist instead of auto-applying unsupported settings.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Support

- Email: contactmukundthiru@gmail.com
- GitHub: https://github.com/contactmukundthiru-cyber/davinci-suite-scripts/issues
