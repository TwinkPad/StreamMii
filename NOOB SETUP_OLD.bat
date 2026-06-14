@echo off
setlocal

:: AUTOELEVATE TO ADMIN
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo.
set PYURL=https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
set PYINSTALLER=python_installer.exe

echo [!] Downloading Python...
powershell -Command "Invoke-WebRequest -Uri %PYURL% -OutFile %PYINSTALLER%"

if not exist %PYINSTALLER% (
    echo [X] Python download failed.
    exit /b 1
)

echo [!] Installing Python silently...
%PYINSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo [!] Cleaning up Python installer...
del %PYINSTALLER%

echo [!] Waiting for PATH...
timeout /t 5 >nul

:: detect python
where python >nul 2>&1
if errorlevel 1 (
    set PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe
) else (
    set PYTHON_EXE=python
)
echo [!] Using Python: %PYTHON_EXE%
echo [!] Upgrading pip...
%PYTHON_EXE% -m pip install --upgrade pip

echo [!] Installing Python packages...
%PYTHON_EXE% -m pip install "requests>=2.31.0" "guessit>=3.2.0" "colorama>=0.4.6"
echo.
echo [!] Installing Chocolatey...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"Set-ExecutionPolicy Bypass -Scope Process -Force; ^
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; ^
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
set CHOCO_PATH=C:\ProgramData\chocolatey\bin
set PATH=%PATH%;%CHOCO_PATH%
where choco >nul 2>&1
if errorlevel 1 (
    echo [X] Chocolatey install failed or PATH not set.
    exit /b 1
)
echo [!] Chocolatey installed successfully.
echo [!] Refreshing environment...
call "%ProgramData%\chocolatey\bin\refreshenv.cmd" >nul 2>&1
echo.
echo [!] Installing FFmpeg (full)...
choco install ffmpeg-full -y
echo.
echo VERIFICATION

echo Python:
%PYTHON_EXE% --version

echo Pip packages:
%PYTHON_EXE% -m pip show requests
%PYTHON_EXE% -m pip show guessit
%PYTHON_EXE% -m pip show colorama

echo FFmpeg:
ffmpeg -version

echo Chocolatey:
choco --version

echo.
echo ALL DONE!
pause
