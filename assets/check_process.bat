@echo off
timeout /t 2 /nobreak >nul
tasklist /FI "IMAGENAME eq notepad.exe" 2>NUL | find /I /N "notepad.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Notepad is running.
)