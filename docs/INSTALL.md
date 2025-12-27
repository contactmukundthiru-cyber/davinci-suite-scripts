# Installation Guide

## Quick Installation

### Windows

1. Download `ResolveProductionSuite-Windows.zip`
2. Extract the folder
3. Double-click `CLICK_ME_FIRST.bat`
4. Select "Install" from the menu
5. Done! A desktop shortcut is created.

### macOS

1. Download `ResolveProductionSuite-macOS.zip`
2. Extract the folder
3. Double-click `DOUBLE_CLICK_ME.command`
4. If you see "unidentified developer": Right-click > Open > Open
5. Select "Install" from the menu
6. Done! A desktop shortcut is created.

## Using the Tools

1. **Open DaVinci Resolve first** (must be running!)
2. Double-click the desktop shortcut
3. Click "Connect Resolve"
4. Select your project and timeline
5. Choose a tool and click "Run Tool"

The app **auto-detects Resolve** - no configuration needed.

## Updating

1. Run the installer (CLICK_ME_FIRST.bat or DOUBLE_CLICK_ME.command)
2. Select "Check for Updates"
3. Updates download and apply automatically

## Uninstalling

1. Run the installer
2. Select "Uninstall"
3. Choose whether to keep or remove user data

## Desktop Shortcut Missing?

Recreate it with:

```bash
# Windows (in Command Prompt)
resolve-suite.bat shortcut

# macOS (in Terminal)
./resolve-suite shortcut
```

## File Locations

| What | Windows | macOS |
|------|---------|-------|
| Program | `%LOCALAPPDATA%\ResolveProductionSuite` | `~/.local/share/resolve-production-suite` |
| Reports | `%USERPROFILE%\.rps\reports` | `~/.rps/reports` |
| Presets | `%USERPROFILE%\.rps\presets` | `~/.rps/presets` |

## Troubleshooting

**"Resolve not connected"**
→ Make sure DaVinci Resolve is running first

**"Windows protected your PC"**
→ Click "More info" then "Run anyway"

**"unidentified developer" (macOS)**
→ Right-click > Open > Open

**Nothing happens when double-clicking**
→ Right-click > "Run as administrator"

## System Requirements

- Windows 10/11 or macOS 10.15+
- DaVinci Resolve (Free or Studio)
- Python 3.9+ (auto-installed)
- 8GB RAM, 500MB disk space
