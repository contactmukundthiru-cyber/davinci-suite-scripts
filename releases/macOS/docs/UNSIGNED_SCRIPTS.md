# Running Unsigned Scripts

This software is not currently code-signed. Here's how to run it on different platforms.

## Windows

### Option 1: Use the GUI Installer (Recommended)
Double-click `installer_gui.py` or run:
```cmd
python installer_gui.py
```
Python scripts don't require signing.

### Option 2: Unblock PowerShell Scripts
Right-click the `.ps1` file → Properties → Check "Unblock" → OK

Or in PowerShell:
```powershell
Unblock-File -Path .\install.ps1
```

### Option 3: Set Execution Policy (Session Only)
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\install.ps1
```

### Option 4: Run with Bypass Flag
```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### SmartScreen Warning
When running `.exe` files (if provided), you may see "Windows protected your PC":
1. Click "More info"
2. Click "Run anyway"

---

## macOS

### Gatekeeper Warning
If you see "cannot be opened because the developer cannot be verified":

**Option 1: Right-click to open**
1. Right-click (or Ctrl+click) the file
2. Select "Open"
3. Click "Open" in the dialog

**Option 2: Allow in Security settings**
1. Go to System Preferences → Security & Privacy
2. Click "Allow Anyway" next to the blocked app
3. Try running again

**Option 3: Remove quarantine attribute**
```bash
xattr -d com.apple.quarantine install.sh
chmod +x install.sh
./install.sh
```

---

## Linux

### Permission Denied
Make the script executable:
```bash
chmod +x install.sh
./install.sh
```

Or run with bash directly:
```bash
bash install.sh
```

---

## Why Not Signed?

Code signing certificates cost $200-500/year and require identity verification.
For open-source/indie software, this is often not feasible initially.

The software is safe to run - you can inspect all source code before installation.

### When Will It Be Signed?

We plan to add code signing when resources allow. This will:
- Remove all security warnings
- Build SmartScreen reputation (Windows)
- Enable notarization (macOS)

---

## Verify Integrity (Alternative to Signing)

You can verify the download hasn't been tampered with using checksums.

### Generate Checksums (Publisher)
```bash
sha256sum resolve-production-suite-v*.zip > checksums.txt
```

### Verify Checksums (User)
```bash
sha256sum -c checksums.txt
```

Or on Windows PowerShell:
```powershell
Get-FileHash .\resolve-production-suite-v0.2.0.zip -Algorithm SHA256
```

Compare the output with the published checksum.
