@echo off
rem ---------------------------------------------------------------
rem  Vortex Traditional Chinese (zh-TW) language pack - launcher
rem
rem  This file is intentionally pure ASCII.
rem  cmd.exe corrupts multi-byte characters in UTF-8 batch files
rem  (even with chcp 65001), so all UI text lives in install.ps1.
rem ---------------------------------------------------------------
setlocal

if not exist "%~dp0install.ps1" (
    echo [ERROR] install.ps1 not found next to this file.
    echo         Please extract the whole archive before running.
    pause
    exit /b 1
)

rem Prefer PowerShell 7+ (pwsh) when installed; fall back to the built-in
rem Windows PowerShell 5.1, which every supported Windows has.
rem install.ps1 is saved as UTF-8 with BOM so both read it correctly.
set "PS=powershell"
where pwsh >nul 2>&1 && set "PS=pwsh"

%PS% -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" (
    echo.
    echo [ERROR] Installer exited with code %RC%.
    pause
)

endlocal
exit /b %RC%
