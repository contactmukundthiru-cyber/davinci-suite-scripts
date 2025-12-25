<#
.SYNOPSIS
    Sign Windows executables and scripts for Resolve Production Suite

.DESCRIPTION
    This script signs all relevant files with your code signing certificate.
    Requires a valid Windows code signing certificate (EV or standard).

.PARAMETER CertPath
    Path to your .pfx certificate file

.PARAMETER CertPassword
    Password for the certificate (will prompt if not provided)

.PARAMETER TimestampServer
    URL of timestamp server (default: DigiCert)

.EXAMPLE
    .\sign_windows.ps1 -CertPath "C:\certs\mycert.pfx"

.EXAMPLE
    .\sign_windows.ps1 -CertPath "C:\certs\mycert.pfx" -CertPassword "mypassword"

.NOTES
    Certificate providers:
    - DigiCert: https://www.digicert.com/signing/code-signing-certificates
    - Sectigo: https://sectigo.com/ssl-certificates-tls/code-signing
    - GlobalSign: https://www.globalsign.com/en/code-signing-certificate

    For EV certificates (recommended for SmartScreen reputation):
    - Requires hardware token (USB)
    - Use signtool with /fd sha256 /tr timestamp
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$CertPath,

    [Parameter(Mandatory=$false)]
    [string]$CertPassword,

    [Parameter(Mandatory=$false)]
    [string]$TimestampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Resolve Production Suite - Code Signing" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verify certificate exists
if (-not (Test-Path $CertPath)) {
    Write-Host "Error: Certificate not found at $CertPath" -ForegroundColor Red
    exit 1
}

# Get password if not provided
if (-not $CertPassword) {
    $securePassword = Read-Host "Enter certificate password" -AsSecureString
    $CertPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    )
}

# Find signtool
$SignTool = $null
$sdkPaths = @(
    "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\signtool.exe",
    "${env:ProgramFiles}\Windows Kits\10\bin\*\x64\signtool.exe",
    "${env:ProgramFiles(x86)}\Microsoft SDKs\Windows\*\bin\signtool.exe"
)

foreach ($pattern in $sdkPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
             Sort-Object -Descending |
             Select-Object -First 1
    if ($found) {
        $SignTool = $found.FullName
        break
    }
}

if (-not $SignTool) {
    Write-Host "Error: signtool.exe not found. Install Windows SDK." -ForegroundColor Red
    Write-Host "Download: https://developer.microsoft.com/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using signtool: $SignTool" -ForegroundColor Gray
Write-Host ""

# Files to sign
$filesToSign = @(
    # PowerShell scripts
    "$RootDir\install.ps1",
    "$RootDir\scripts\sign_windows.ps1",

    # Batch files
    "$RootDir\resolve-suite.bat",
    "$RootDir\resolve-suite-ui.bat",

    # Python GUI installer (for py2exe/pyinstaller builds)
    "$RootDir\dist\installer.exe",
    "$RootDir\dist\resolve-suite.exe",
    "$RootDir\dist\resolve-suite-ui.exe"
)

# Sign function
function Sign-File {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath)) {
        Write-Host "  Skipped (not found): $FilePath" -ForegroundColor Yellow
        return
    }

    Write-Host "  Signing: $FilePath" -ForegroundColor Gray

    $args = @(
        "sign",
        "/f", $CertPath,
        "/p", $CertPassword,
        "/fd", "sha256",
        "/tr", $TimestampServer,
        "/td", "sha256",
        "/v",
        $FilePath
    )

    $result = & $SignTool $args 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Signed successfully" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Signing failed" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    }
}

# Sign all files
Write-Host "Signing files..." -ForegroundColor Cyan
Write-Host ""

foreach ($file in $filesToSign) {
    Sign-File -FilePath $file
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Signing Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test signed files on a clean Windows machine"
Write-Host "  2. Rebuild release package: .\build_release.sh"
Write-Host "  3. Upload to Gumroad"
Write-Host ""

# Verification
Write-Host "Verifying signatures..." -ForegroundColor Cyan
foreach ($file in $filesToSign) {
    if (Test-Path $file) {
        $sig = Get-AuthenticodeSignature -FilePath $file
        $status = $sig.Status
        $signer = $sig.SignerCertificate.Subject

        if ($status -eq "Valid") {
            Write-Host "  [VALID] $file" -ForegroundColor Green
            Write-Host "          Signed by: $signer" -ForegroundColor Gray
        } else {
            Write-Host "  [$status] $file" -ForegroundColor Yellow
        }
    }
}
