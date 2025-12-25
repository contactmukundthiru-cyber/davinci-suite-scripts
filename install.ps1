#Requires -Version 5.1
<#
.SYNOPSIS
    Resolve Production Suite Installer for Windows
.DESCRIPTION
    Installs the Resolve Production Suite with all dependencies
.PARAMETER Full
    Install with all optional extras (UI, analysis)
.PARAMETER Minimal
    Install base only (no UI, no analysis)
.PARAMETER Dev
    Install in development/editable mode
.PARAMETER Uninstall
    Remove the installation
.EXAMPLE
    .\install.ps1
    Interactive installation
.EXAMPLE
    .\install.ps1 -Full
    Install with all features
.EXAMPLE
    .\install.ps1 -Uninstall
    Remove installation
#>

[CmdletBinding()]
param(
    [switch]$Full,
    [switch]$Minimal,
    [switch]$Dev,
    [switch]$Uninstall,
    [switch]$Help
)

# =============================================================================
# Configuration
# =============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Version = Get-Content "$ScriptDir\VERSION" -ErrorAction SilentlyContinue
if (-not $Version) { $Version = "0.2.0" }
$VenvDir = Join-Path $ScriptDir ".venv"
$RpsHome = if ($env:RPS_HOME) { $env:RPS_HOME } else { Join-Path $env:USERPROFILE ".rps" }
$MinPythonVersion = [version]"3.9"

# =============================================================================
# Helper Functions
# =============================================================================

function Write-Banner {
    Write-Host ""
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host "                                                                       " -ForegroundColor Cyan
    Write-Host "           Resolve Production Suite Installer v$Version                " -ForegroundColor Cyan
    Write-Host "                                                                       " -ForegroundColor Cyan
    Write-Host "   Commercial-grade workflow automation for DaVinci Resolve            " -ForegroundColor Cyan
    Write-Host "                                                                       " -ForegroundColor Cyan
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host ">>> $Message" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Confirm-Action {
    param(
        [string]$Prompt,
        [bool]$Default = $true
    )
    $defaultText = if ($Default) { "[Y/n]" } else { "[y/N]" }
    $response = Read-Host "$Prompt $defaultText"
    if ([string]::IsNullOrWhiteSpace($response)) {
        return $Default
    }
    return $response -match "^[Yy]"
}

# =============================================================================
# Prerequisite Checks
# =============================================================================

function Test-Python {
    Write-Step "Checking Python installation"

    # Try py launcher first (Windows standard), then python
    $pythonCmd = $null
    $pythonPath = $null

    try {
        $pyVersion = & py -3 --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "py"
            $pythonPath = "py -3"
        }
    } catch {}

    if (-not $pythonCmd) {
        try {
            $pythonVersion = & python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pythonCmd = "python"
                $pythonPath = "python"
            }
        } catch {}
    }

    if (-not $pythonCmd) {
        Write-Error "Python not found. Please install Python $MinPythonVersion+"
        Write-Info "Download from: https://www.python.org/downloads/"
        return $false
    }

    # Parse version
    $versionString = if ($pythonCmd -eq "py") {
        & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    } else {
        & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    }

    $currentVersion = [version]$versionString

    if ($currentVersion -ge $MinPythonVersion) {
        Write-Success "Python $versionString found"
        $script:PythonCmd = $pythonPath
        return $true
    } else {
        Write-Error "Python $versionString found, but $MinPythonVersion+ is required"
        return $false
    }
}

function Find-Resolve {
    Write-Step "Detecting DaVinci Resolve installation"

    $resolvePaths = @(
        "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules",
        "C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting\Modules",
        "$env:PROGRAMDATA\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
    )

    $script:ResolveScriptPath = $null

    # Check environment variable first
    if ($env:RESOLVE_SCRIPT_API -and (Test-Path $env:RESOLVE_SCRIPT_API)) {
        $script:ResolveScriptPath = $env:RESOLVE_SCRIPT_API
        Write-Success "Using RESOLVE_SCRIPT_API from environment: $($env:RESOLVE_SCRIPT_API)"
        return
    }

    # Check common paths
    foreach ($path in $resolvePaths) {
        if (Test-Path $path) {
            $script:ResolveScriptPath = $path
            Write-Success "Found Resolve at: $path"
            return
        }
    }

    Write-Warning "DaVinci Resolve scripting modules not found automatically"
    Write-Info "Common location: C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"

    $customPath = Read-Host "Enter Resolve scripting modules path (or press Enter to skip)"
    if ($customPath -and (Test-Path $customPath)) {
        $script:ResolveScriptPath = $customPath
        Write-Success "Using custom path: $customPath"
    } elseif ($customPath) {
        Write-Warning "Path does not exist. Continuing without Resolve API configuration."
    }
}

# =============================================================================
# Installation Functions
# =============================================================================

function New-VirtualEnv {
    Write-Step "Creating virtual environment"

    if (Test-Path $VenvDir) {
        if (Confirm-Action "Virtual environment already exists. Recreate it?") {
            Remove-Item -Recurse -Force $VenvDir
        } else {
            Write-Info "Using existing virtual environment"
            return
        }
    }

    if ($PythonCmd -eq "py -3") {
        & py -3 -m venv $VenvDir
    } else {
        & python -m venv $VenvDir
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }

    Write-Success "Virtual environment created at $VenvDir"
}

function Enable-VirtualEnv {
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
        Write-Success "Virtual environment activated"
    } else {
        throw "Virtual environment activation script not found"
    }
}

function Update-Pip {
    Write-Step "Upgrading pip and build tools"

    & pip install --upgrade pip setuptools wheel --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to upgrade pip (continuing anyway)"
    } else {
        Write-Success "pip, setuptools, and wheel upgraded"
    }
}

function Install-BaseDependencies {
    Write-Step "Installing base dependencies"

    & pip install -r "$ScriptDir\requirements.txt" --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install base dependencies"
    }

    Write-Success "Base dependencies installed (jsonschema>=4.18)"
}

function Install-Package {
    Write-Step "Installing Resolve Production Suite package"

    $extras = ""

    if ($script:InstallUI -and $script:InstallAnalysis) {
        $extras = "[ui,analysis]"
    } elseif ($script:InstallUI) {
        $extras = "[ui]"
    } elseif ($script:InstallAnalysis) {
        $extras = "[analysis]"
    }

    $installPath = "${ScriptDir}${extras}"

    if ($Dev) {
        & pip install -e $installPath --quiet
        Write-Success "Package installed in development (editable) mode"
    } else {
        & pip install $installPath --quiet
        Write-Success "Package installed"
    }

    if ($script:InstallUI) {
        Write-Success "UI dependencies installed (PySide6)"
    }

    if ($script:InstallAnalysis) {
        Write-Success "Analysis dependencies installed (OpenCV, NumPy)"
    }
}

function New-Directories {
    Write-Step "Creating data directories"

    $dirs = @("logs", "reports", "presets", "packs")

    foreach ($dir in $dirs) {
        $path = Join-Path $RpsHome $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
        Write-Success "Created: $path"
    }
}

function Copy-SamplePresets {
    Write-Step "Installing sample presets and packs"

    $presetsDir = Join-Path $ScriptDir "presets"
    $packsDir = Join-Path $RpsHome "packs"

    if (Test-Path $presetsDir) {
        Get-ChildItem "$presetsDir\*.json" | ForEach-Object {
            $dest = Join-Path $packsDir $_.Name
            if (-not (Test-Path $dest)) {
                Copy-Item $_.FullName $dest
            }
        }
        Write-Success "Sample packs copied to $packsDir"
    }
}

function Set-Environment {
    Write-Step "Setting up environment variables"

    # Set user environment variables
    [Environment]::SetEnvironmentVariable("RPS_HOME", $RpsHome, "User")
    Write-Success "Set RPS_HOME=$RpsHome"

    if ($script:ResolveScriptPath) {
        [Environment]::SetEnvironmentVariable("RESOLVE_SCRIPT_API", $script:ResolveScriptPath, "User")
        Write-Success "Set RESOLVE_SCRIPT_API=$($script:ResolveScriptPath)"
    }

    # Add to PATH
    $venvBin = Join-Path $VenvDir "Scripts"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentPath -notlike "*$venvBin*") {
        $newPath = "$currentPath;$venvBin"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Success "Added $venvBin to PATH"
    }

    Write-Info "Restart your terminal for environment changes to take effect"
}

function New-BatchLaunchers {
    Write-Step "Creating launcher scripts"

    $venvScripts = Join-Path $VenvDir "Scripts"

    # Main CLI launcher
    $cliLauncher = Join-Path $ScriptDir "resolve-suite.bat"
    @"
@echo off
call "$venvScripts\activate.bat"
python -m cli.main %*
"@ | Set-Content $cliLauncher
    Write-Success "Created: $cliLauncher"

    # UI launcher
    if ($script:InstallUI) {
        $uiLauncher = Join-Path $ScriptDir "resolve-suite-ui.bat"
        @"
@echo off
call "$venvScripts\activate.bat"
pythonw -m ui.app %*
"@ | Set-Content $uiLauncher
        Write-Success "Created: $uiLauncher"
    }
}

function New-StartMenuShortcut {
    Write-Step "Creating Start Menu shortcut"

    if (-not $script:InstallUI) {
        Write-Info "Skipping Start Menu shortcut (UI not installed)"
        return
    }

    $startMenuPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
    $shortcutPath = Join-Path $startMenuPath "Resolve Production Suite.lnk"

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = Join-Path $ScriptDir "resolve-suite-ui.bat"
    $shortcut.WorkingDirectory = $ScriptDir
    $shortcut.Description = "Resolve Production Suite - Workflow Automation for DaVinci Resolve"
    $shortcut.Save()

    Write-Success "Created Start Menu shortcut"
}

function Test-Installation {
    Write-Step "Verifying installation"

    try {
        $output = & python -m cli.main list 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "CLI tools accessible"
            Write-Host ""
            Write-Info "Available tools:"
            & python -m cli.main list
        } else {
            Write-Warning "CLI tools may have issues"
        }
    } catch {
        Write-Warning "Could not verify CLI tools"
    }
}

# =============================================================================
# Uninstall Function
# =============================================================================

function Remove-Installation {
    Write-Banner
    Write-Step "Uninstalling Resolve Production Suite"

    if (-not (Confirm-Action "This will remove the virtual environment and launcher scripts. Continue?" $false)) {
        Write-Info "Uninstall cancelled"
        return
    }

    # Remove virtual environment
    if (Test-Path $VenvDir) {
        Remove-Item -Recurse -Force $VenvDir
        Write-Success "Removed virtual environment"
    }

    # Remove launcher scripts
    Remove-Item -Force "$ScriptDir\resolve-suite.bat" -ErrorAction SilentlyContinue
    Remove-Item -Force "$ScriptDir\resolve-suite-ui.bat" -ErrorAction SilentlyContinue
    Write-Success "Removed launcher scripts"

    # Remove Start Menu shortcut
    $shortcutPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Resolve Production Suite.lnk"
    Remove-Item -Force $shortcutPath -ErrorAction SilentlyContinue
    Write-Success "Removed Start Menu shortcut"

    # Remove environment variables
    [Environment]::SetEnvironmentVariable("RPS_HOME", $null, "User")
    [Environment]::SetEnvironmentVariable("RESOLVE_SCRIPT_API", $null, "User")
    Write-Success "Removed environment variables"

    if (Confirm-Action "Also remove user data ($RpsHome)?" $false) {
        Remove-Item -Recurse -Force $RpsHome -ErrorAction SilentlyContinue
        Write-Success "Removed user data"
    } else {
        Write-Info "User data preserved at $RpsHome"
    }

    Write-Host ""
    Write-Success "Uninstall complete!"
}

# =============================================================================
# Help
# =============================================================================

function Show-Help {
    Write-Banner
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Full        Install with all optional extras (UI, analysis)"
    Write-Host "  -Minimal     Install base only (no UI, no analysis)"
    Write-Host "  -Dev         Install in development/editable mode"
    Write-Host "  -Uninstall   Remove the installation"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    Write-Host "After Installation:"
    Write-Host "  resolve-suite list              List all available tools"
    Write-Host "  resolve-suite run <tool_id>     Run a specific tool"
    Write-Host "  resolve-suite-ui                Launch the desktop application"
    Write-Host ""
}

# =============================================================================
# Main
# =============================================================================

function Main {
    if ($Help) {
        Show-Help
        return
    }

    if ($Uninstall) {
        Remove-Installation
        return
    }

    Write-Banner

    # Prerequisites
    if (-not (Test-Python)) {
        exit 1
    }

    Find-Resolve

    # Determine what to install
    if ($Full) {
        $script:InstallUI = $true
        $script:InstallAnalysis = $true
    } elseif ($Minimal) {
        $script:InstallUI = $false
        $script:InstallAnalysis = $false
    } else {
        # Interactive
        Write-Host ""
        $script:InstallUI = Confirm-Action "Install desktop UI (PySide6, ~150MB)?"
        $script:InstallAnalysis = Confirm-Action "Install analysis extras (OpenCV, NumPy)?"
    }

    Write-Host ""
    Write-Step "Starting installation"
    Write-Host "  - UI: $($script:InstallUI)"
    Write-Host "  - Analysis: $($script:InstallAnalysis)"
    Write-Host "  - Dev mode: $Dev"
    Write-Host ""

    if (-not (Confirm-Action "Proceed with installation?")) {
        Write-Info "Installation cancelled"
        return
    }

    # Install
    New-VirtualEnv
    Enable-VirtualEnv
    Update-Pip
    Install-BaseDependencies
    Install-Package
    New-Directories
    Copy-SamplePresets
    Set-Environment
    New-BatchLaunchers
    New-StartMenuShortcut
    Test-Installation

    # Success
    Write-Host ""
    Write-Host "=======================================================================" -ForegroundColor Green
    Write-Host "                                                                       " -ForegroundColor Green
    Write-Host "              Installation Complete!                                   " -ForegroundColor Green
    Write-Host "                                                                       " -ForegroundColor Green
    Write-Host "=======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Info "Quick Start:"
    Write-Host "  1. Restart your terminal for PATH changes"
    Write-Host "  2. List available tools: resolve-suite list"
    Write-Host "  3. Run a tool: resolve-suite run t1_revision_resolver --dry-run"
    if ($script:InstallUI) {
        Write-Host "  4. Launch UI: resolve-suite-ui"
    }
    Write-Host ""
    Write-Info "Documentation: $ScriptDir\docs\"
    Write-Info "Reports saved to: $RpsHome\reports\"
    Write-Host ""
}

# Run
Main
