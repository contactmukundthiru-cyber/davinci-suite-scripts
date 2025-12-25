# Quick Start Guide

Get up and running with the Resolve Production Suite in 5 minutes.

## Step 1: Install

### Windows
1. Extract the zip file
2. Double-click `CLICK_ME_FIRST.bat`
3. Select option 1 (Install)

### macOS
1. Extract the zip file
2. Double-click `DOUBLE_CLICK_ME.command`
3. Select option 1 (Install)

## Step 2: Open DaVinci Resolve

Make sure DaVinci Resolve is running before using the tools. The tools communicate with Resolve via its scripting API.

## Step 3: Run Your First Tool

After installation, you can run tools from the command line:

```bash
# List all available tools
resolve-suite list

# Run a specific tool with dry-run mode (preview changes)
resolve-suite run t1_revision_resolver --dry-run

# Run a tool with options file
resolve-suite run t6_timeline_normalizer --options /path/to/options.json
```

Or use the desktop shortcut to open the GUI application.

## Quick Examples

### Example 1: Check Timeline Technical Specs

Run the Timeline Normalizer to verify your timeline meets delivery requirements:

```bash
resolve-suite run t6_timeline_normalizer --dry-run
```

This will report:
- Frame rate verification
- Resolution check
- Disabled clips
- Muted tracks
- Duplicate clip names

### Example 2: Create Markers from Feedback

Have client feedback in a text file? Convert it to timeline markers:

```bash
resolve-suite run t5_feedback_compiler --options feedback_options.json
```

Where `feedback_options.json` contains:
```json
{
  "feedback_file": "/path/to/client_feedback.txt",
  "marker_color": "red",
  "create_task_list": true
}
```

### Example 3: Audit Brand Compliance

Check if your project follows brand guidelines:

```bash
resolve-suite run t10_brand_drift_detector --options brand_options.json
```

## Tool Options Files

Each tool accepts a JSON options file. Example structure:

```json
{
  "dry_run": true,
  "option1": "value1",
  "option2": "value2"
}
```

See [PRODUCTS.md](PRODUCTS.md) for complete option specifications for each tool.

## Finding Reports

All tool reports are saved to:

| Platform | Report Location |
|----------|----------------|
| Windows | `%USERPROFILE%\.rps\reports` |
| macOS | `~/.rps/reports` |

Reports are available in JSON, CSV, and HTML formats.

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for detailed tool documentation
- Check [PRODUCTS.md](PRODUCTS.md) for complete specifications
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you encounter issues

## Getting Help

- Email: contactmukundthiru@gmail.com
- GitHub Issues: https://github.com/contactmukundthiru-cyber/davinci-suite-scripts/issues
