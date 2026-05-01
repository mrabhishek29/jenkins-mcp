@echo off
setlocal

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [jenkins-mcp] First run detected, running setup... >&2
    call "%~dp0setup.cmd" >&2
    if errorlevel 1 (
        echo [jenkins-mcp] Setup failed. Run setup.cmd manually. >&2
        exit /b 1
    )
)

"%~dp0.venv\Scripts\python.exe" "%~dp0server.py" %*
exit /b %ERRORLEVEL%
