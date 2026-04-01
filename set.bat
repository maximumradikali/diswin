@echo off
chcp 65001 > nul
title Windows Update Manager v4.0

net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [!] Administrator access required.
    echo  Relaunching as Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  [!] Python is not installed!
    echo  Download it from: https://python.org
    echo.
    pause
    exit /b
)

cls
python "%~dp0windows_update_manager.py"
pause