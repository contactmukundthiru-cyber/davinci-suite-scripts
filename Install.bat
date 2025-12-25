@echo off
setlocal enabledelayedexpansion

REM ============================================
REM   Resolve Production Suite Installer
REM   Windows Smart Launcher
REM ============================================

title Resolve Production Suite Installer

echo.
echo ============================================
echo   Resolve Production Suite Installer
echo ============================================
echo.

REM Check for standalone executable first
if exist "%~dp0dist\Setup.exe" (
    echo Found standalone installer...
    start "" "%~dp0dist\Setup.exe"
    exit /b 0
)

REM Check for Python
set PYTHON_CMD=

REM Try py launcher (Windows standard)
py -3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3
    goto :found_python
)

REM Try python
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python
        goto :found_python
    )
)

REM Try python3
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :found_python
)

REM Check for embedded Python in package
if exist "%~dp0python\python.exe" (
    set PYTHON_CMD=%~dp0python\python.exe
    goto :found_python
)

REM Python not found - offer to download
echo.
echo Python 3.9+ is required but was not found.
echo.
echo Options:
echo   1. Download and install Python automatically
echo   2. Open Python download page in browser
echo   3. Cancel
echo.
set /p CHOICE="Enter choice (1-3): "

if "%CHOICE%"=="1" goto :auto_install
if "%CHOICE%"=="2" goto :open_browser
goto :cancel

:auto_install
echo.
echo Downloading Python installer...

REM Download Python installer using PowerShell
set PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python_installer.exe

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"

if not exist "%PYTHON_INSTALLER%" (
    echo Failed to download Python installer.
    echo Please download manually from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing Python...
echo IMPORTANT: Make sure to check "Add Python to PATH"!
echo.

REM Run Python installer
start /wait "" "%PYTHON_INSTALLER%" /passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_tcltk=1

REM Clean up
del "%PYTHON_INSTALLER%" >nul 2>&1

echo.
echo Python installation complete!
echo Please close this window and run Install.bat again.
echo.
pause
exit /b 0

:open_browser
echo.
echo Opening Python download page...
start https://www.python.org/downloads/
echo.
echo After installing Python:
echo   1. Make sure to check "Add Python to PATH" during installation
echo   2. Close this window and run Install.bat again
echo.
pause
exit /b 0

:cancel
echo Installation cancelled.
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%

REM Check for tkinter
%PYTHON_CMD% -c "import tkinter" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Tkinter not found. The GUI installer requires Tkinter.
    echo.
    echo Tkinter is usually included with Python on Windows.
    echo If you installed Python from python.org, try reinstalling with
    echo the "tcl/tk and IDLE" option checked.
    echo.
    echo Alternatively, you can use the command-line installer:
    echo   powershell -ExecutionPolicy Bypass -File install.ps1
    echo.
    pause
    exit /b 1
)

echo Starting graphical installer...
echo.

%PYTHON_CMD% "%~dp0installer_gui.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation encountered an error.
    echo.
    echo If issues persist, try the command-line installer:
    echo   powershell -ExecutionPolicy Bypass -File install.ps1
    echo.
    pause
)

endlocal
