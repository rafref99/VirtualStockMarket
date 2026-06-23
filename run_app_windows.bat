@echo off
setlocal

cd /d "%~dp0"

echo Starting Virtual Stock Market...

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON=python"
    ) else (
        echo Python 3 is required but was not found.
        echo Install Python 3 from https://www.python.org/downloads/ and run this again.
        pause
        exit /b 1
    )
)

%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info.major >= 3 else 1)"
if not %errorlevel%==0 (
    echo Python 3 is required.
    pause
    exit /b 1
)

%PYTHON% -c "import tkinter"
if not %errorlevel%==0 (
    echo Tkinter is required for the desktop app but is not available in this Python installation.
    echo Install a Python build that includes Tkinter, then run this launcher again.
    pause
    exit /b 1
)

findstr /R "^[ ]*[^# ][^ ]*" requirements.txt >nul 2>nul
if %errorlevel%==0 (
    echo Checking and installing Python package requirements...
    %PYTHON% -m pip install --upgrade pip
    if not %errorlevel%==0 (
        pause
        exit /b 1
    )
    %PYTHON% -m pip install -r requirements.txt
    if not %errorlevel%==0 (
        pause
        exit /b 1
    )
) else (
    echo No third-party packages are listed in requirements.txt.
)

echo Launching app...
%PYTHON% app.py

echo App closed.
pause
