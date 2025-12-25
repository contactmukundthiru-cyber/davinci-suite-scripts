# Installation Guide

## Quick Installation (Recommended)

### Windows

1. Download `ResolveProductionSuite-Windows.zip`
2. Extract the folder to a location of your choice
3. Open the extracted folder
4. Double-click `CLICK_ME_FIRST.bat`
5. Select option 1 (Install)
6. Follow the on-screen prompts

The installer will:
- Automatically download and install Python if needed
- Install all required dependencies
- Create a desktop shortcut
- Add the tools to your system PATH

### macOS

1. Download `ResolveProductionSuite-macOS.zip`
2. Extract the folder to a location of your choice
3. Open the extracted folder
4. Double-click `DOUBLE_CLICK_ME.command`
5. If you see "unidentified developer" warning, right-click > Open > Open
6. Select option 1 (Install)
7. Follow the on-screen prompts

The installer will:
- Use Homebrew Python if available, otherwise download from python.org
- Install all required dependencies
- Create a desktop alias
- Add the tools to your system PATH

## Enabling DaVinci Resolve Scripting

For the tools to communicate with DaVinci Resolve, you need to enable scripting:

### Windows

The Resolve scripting modules are typically located at:
```
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules
```

Set the environment variable (optional, installer may handle this):
1. Open System Properties > Environment Variables
2. Add new system variable:
   - Name: `RESOLVE_SCRIPT_API`
   - Value: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules`

### macOS

The Resolve scripting modules are typically located at:
```
/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules
```

Add to your shell profile (~/.zshrc or ~/.bash_profile):
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
```

## Updating

To update to the latest version:

1. Run the installer (CLICK_ME_FIRST.bat or DOUBLE_CLICK_ME.command)
2. Select option 2 (Check for Updates)
3. The update will be downloaded and applied automatically

You don't need to re-download the zip file - the updater handles everything.

## Uninstalling

To remove the suite:

1. Run the installer
2. Select option 3 (Uninstall)
3. Choose whether to keep or remove user data

This will:
- Remove the installed program files
- Remove desktop shortcuts
- Remove PATH entries
- Optionally remove user data and settings

## Installation Locations

| Platform | Default Install Location |
|----------|-------------------------|
| Windows | `%LOCALAPPDATA%\ResolveProductionSuite` |
| macOS | `~/Library/Application Support/ResolveProductionSuite` |

User data (presets, logs, reports) is stored separately:

| Platform | User Data Location |
|----------|-------------------|
| Windows | `%USERPROFILE%\.rps` |
| macOS | `~/.rps` |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `RESOLVE_SCRIPT_API` | Path to Resolve scripting modules |
| `RPS_HOME` | Suite data home (default: `~/.rps`) |
| `RPS_LOGS` | Custom log path |
| `RPS_REPORTS` | Custom report path |
| `RPS_PRESETS` | Custom presets path |

## Troubleshooting

### Windows

**"Windows protected your PC" warning**
- Click "More info" then "Run anyway"

**Nothing happens when double-clicking**
- Right-click the file and select "Run as administrator"

**Python not found after installation**
- Close the window and run CLICK_ME_FIRST.bat again

### macOS

**"unidentified developer" warning**
- Right-click > Open > Open
- Or: System Preferences > Security & Privacy > Open Anyway

**"permission denied" error**
- Open Terminal and run: `chmod +x DOUBLE_CLICK_ME.command`

### General

**Resolve connection fails**
- Make sure DaVinci Resolve is running
- Verify scripting is enabled in Resolve preferences
- Check that `RESOLVE_SCRIPT_API` points to the correct location

## System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 or macOS 10.15+ |
| Python | 3.9+ (auto-installed by installer) |
| DaVinci Resolve | Studio or Free with scripting enabled |
| RAM | 8GB minimum, 16GB recommended |
| Disk | 500MB for installation |

## Resolve Free vs Studio

The tools work with both Resolve Free and Studio. However, some optional features require Studio:
- Face detection in Smart Reframer (requires Studio's Neural Engine access)
- Certain codec settings in Delivery Spec Enforcer

All core functionality works with Resolve Free.
