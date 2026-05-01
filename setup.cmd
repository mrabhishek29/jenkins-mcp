@echo off
setlocal

if not exist "%~dp0config.yaml" (
    if exist "%~dp0config.example.yaml" (
        copy "%~dp0config.example.yaml" "%~dp0config.yaml" >nul
        echo Created config.yaml from config.example.yaml — edit it with your Jenkins credentials.
    ) else (
        echo WARNING: No config.example.yaml found. Create config.yaml manually.
    )
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Creating virtual environment...
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        py -3 -m venv "%~dp0.venv"
    ) else (
        python -m venv "%~dp0.venv"
    )
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip -q
if errorlevel 1 exit /b 1

"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" -q
if errorlevel 1 exit /b 1

echo.
echo Setup complete. Edit config.yaml with your Jenkins credentials, then run:
echo   run-stdio.cmd
