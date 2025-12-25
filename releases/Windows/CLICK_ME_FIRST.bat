@echo off
setlocal EnableDelayedExpansion
title Resolve Production Suite - Windows Installer
color 0B

echo.
echo ========================================
echo   RESOLVE PRODUCTION SUITE INSTALLER
echo ========================================
echo.
echo This will install the suite on your Windows PC.
echo.
echo Checking if Python is installed...
echo.

REM First check common Python installation paths directly
set "PYTHON_PATH="

REM Check user Python installation (most common after fresh install)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :found_python
)

REM Check system-wide Python installation
if exist "C:\Python311\python.exe" (
    set "PYTHON_PATH=C:\Python311\python.exe"
    goto :found_python
)
if exist "C:\Python312\python.exe" (
    set "PYTHON_PATH=C:\Python312\python.exe"
    goto :found_python
)

REM Try py launcher (but check it's not the Microsoft Store stub)
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3 --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_PATH=py -3"
        goto :found_python
    )
)

REM Try python command
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python --version 2>&1 | findstr /C:"Python 3" >nul
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_PATH=python"
        goto :found_python
    )
)

REM Python not found - need to install
echo.
echo [!] Python is not installed on this computer.
echo.
echo I will download and install Python for you.
echo This takes about 2-3 minutes.
echo.
echo Press any key to start the download...
pause >nul

echo.
echo ========================================
echo   DOWNLOADING PYTHON
echo ========================================
echo.
echo Downloading Python 3.11 (about 25 MB)...
echo Please wait...
echo.

REM Download Python using PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Write-Host 'Downloading from python.org...'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\python_install.exe' -UseBasicParsing; Write-Host 'Download complete!' } catch { Write-Host 'Download failed!'; exit 1 } }"

if not exist "%TEMP%\python_install.exe" (
    echo.
    echo [ERROR] Download failed!
    echo.
    echo Please check your internet connection and try again.
    echo.
    echo Or download Python manually from:
    echo    https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During manual install, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALLING PYTHON
echo ========================================
echo.
echo Installing Python (this takes about 1 minute)...
echo Please wait...
echo.

REM Install Python with PATH
start /wait "" "%TEMP%\python_install.exe" /passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1 Include_launcher=1

REM Clean up installer
del "%TEMP%\python_install.exe" >nul 2>&1

REM Check if Python was installed successfully
set "PYTHON_PATH="
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if defined PYTHON_PATH (
    echo.
    echo ========================================
    echo   PYTHON INSTALLED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Found Python at: !PYTHON_PATH!
    echo.
    echo Starting the installer now...
    echo.
    timeout /t 2 >nul
    goto :run_installer
) else (
    echo.
    echo ========================================
    echo   PYTHON INSTALLED - RESTART REQUIRED
    echo ========================================
    echo.
    echo Python was installed but I couldn't find it yet.
    echo.
    echo Please do the following:
    echo    1. CLOSE this window
    echo    2. Double-click CLICK_ME_FIRST.bat again
    echo.
    echo Press any key to close...
    pause >nul
    exit /b 0
)

:found_python
echo [OK] Python found: !PYTHON_PATH!
echo.

:run_installer
cd /d "%~dp0"

echo Starting Resolve Production Suite installer...
echo.

if "!PYTHON_PATH!"=="py -3" (
    py -3 installer.py
) else (
    "!PYTHON_PATH!" installer.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] The installer encountered an issue.
    echo.
    echo If you see errors, try:
    echo    1. Right-click CLICK_ME_FIRST.bat
    echo    2. Select "Run as administrator"
    echo.
)

echo.
pause
endlocal
