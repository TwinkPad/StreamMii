@echo off
setlocal EnableDelayedExpansion

:: go to admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo.
echo ============================================================
echo   StreamMii setup 
echo ============================================================
echo.

:: the old script downloaded the python
:: installer with NO integrity check and piped chocolatey install
:: script straight into iex -- remote code execution as admin
:: both are replaced with winget, which verifies every package
:: against a sha256 in microslop signed manifest repo before it
:: runs no unverified downloads no piped remote scripts

where winget >nul 2>&1
if errorlevel 1 goto NO_WINGET

echo [!] Installing Python 3.12 via winget (hash-verified)...
winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo [X] winget failed to install Python.
    goto FAIL
)

echo [!] Installing FFmpeg via winget (hash-verified)...
winget install --id Gyan.FFmpeg -e --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo [X] winget failed to install FFmpeg.
    goto FAIL
)

goto FIND_PYTHON

:NO_WINGET
echo [X] winget (App Installer) was not found on this system.
echo.
echo     For your security this installer will NOT download and run
echo     unverified executables. Please install the two dependencies
echo     manually, then rerun this script:
echo.
echo       1^) Python 3.12 : https://www.python.org/downloads/
echo                        ^(tick "Add python.exe to PATH"^)
echo       2^) FFmpeg       : https://ffmpeg.org/download.html
echo.
echo     Tip: install "App Installer" from the MicroSLOP Store to get
echo     winget, then rerun this script for the automatic path.
echo.
pause
exit /b 1

:FIND_PYTHON
echo [!] Waiting for PATH to update...
timeout /t 5 >nul

set "PYTHON_EXE="
where python >nul 2>&1 && set "PYTHON_EXE=python"
if not defined PYTHON_EXE (
    where py >nul 2>&1 && set "PYTHON_EXE=py -3"
)
if not defined PYTHON_EXE (
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
)
if not defined PYTHON_EXE (
    if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_EXE=%ProgramFiles%\Python312\python.exe"
)
if not defined PYTHON_EXE (
    echo [X] Could not locate Python in this session. Open a NEW terminal and re-run.
    goto FAIL
)
echo [!] Using Python: %PYTHON_EXE%

echo [!] Upgrading pip...
%PYTHON_EXE% -m pip install --upgrade pip

:: pinned + hash verified dependencies  with a hashed
:: requirements.txt pip rejects anything whose hash doesnt match
set "REQ=%~dp0requirements.txt"
echo [!] Installing Python packages...
if exist "%REQ%" (
    echo [!] Using hash-verified requirements: %REQ%
    %PYTHON_EXE% -m pip install --require-hashes -r "%REQ%"
) else (
    echo [!] requirements.txt not found next to this script; using pinned versions.
    %PYTHON_EXE% -m pip install "requests==2.34.2" "guessit==3.8.0" "colorama==0.4.6"
)

echo.
echo ================ VERIFICATION ================
echo.
echo Python:
%PYTHON_EXE% --version
echo.
echo Pip packages:
%PYTHON_EXE% -m pip show requests  | findstr /B /C:"Name" /C:"Version"
%PYTHON_EXE% -m pip show guessit   | findstr /B /C:"Name" /C:"Version"
%PYTHON_EXE% -m pip show colorama  | findstr /B /C:"Name" /C:"Version"
echo.
echo FFmpeg:
where ffmpeg >nul 2>&1 && (ffmpeg -version 2>&1 | findstr /B /C:"ffmpeg version") || echo   [i] ffmpeg installed but not on PATH in this session - open a new terminal.
echo.
echo ================ ALL DONE! ================
pause
exit /b 0

:FAIL
echo.
echo [X] Setup did not complete. See the messages above.
pause
exit /b 1
