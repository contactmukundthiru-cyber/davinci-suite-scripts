# Troubleshooting

Common issues and solutions for Resolve Production Suite.

---

## Connection Issues

### "Cannot connect to DaVinci Resolve"

1. **Make sure Resolve is running first** - Open DaVinci Resolve before launching the suite
2. **Enable external scripting** in Resolve:
   - Go to Preferences → System → General
   - Set "External scripting using" to "Local" or "Network"
   - Restart Resolve after changing this setting
3. **Restart the suite** after making changes

### "Connection was lost"

- Resolve may have been closed or crashed
- Click "Reconnect" to re-establish connection

---

## Installation Issues

### Windows: "Windows protected your PC"

- Click "More info" then "Run anyway"
- This appears because the installer isn't digitally signed

### Windows: Nothing happens when double-clicking

- Right-click the file and select "Run as administrator"
- Or run from Command Prompt: `python installer.py`

### macOS: "Cannot be opened because the developer cannot be verified"

- Right-click the file and select "Open"
- Or go to System Preferences → Security & Privacy → click "Open Anyway"

### Desktop shortcut missing

Run the installer again and select "Create Desktop Shortcut" from the menu.

---

## Runtime Issues

### "No projects found"

- Open or create a project in DaVinci Resolve
- Click "Refresh" in the suite

### "No timelines found"

- Create a timeline in your current project
- Click "Refresh" in the suite

### Tool gives unexpected results

1. Enable "Dry Run" mode to preview changes without modifying your project
2. Check the tool options/JSON for correct settings
3. Review the generated reports in `~/.rps/reports/`

---

## Update Issues

### "Could not check for updates"

- Check your internet connection
- The update server may be temporarily unavailable
- Try again later

---

## Getting Help

If your issue isn't listed here:
- Email: contactmukundthiru@gmail.com
- GitHub Issues: https://github.com/contactmukundthiru-cyber/davinci-suite-scripts/issues
