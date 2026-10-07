@echo off
title MalVision Threat Hunter
cd /d "%~dp0"

echo ===================================================
echo           MalVision Threat Hunter
echo    Image-Based Malware Classification System
echo ===================================================
echo.
echo Launching web application on http://localhost:8501 ...
echo Your default browser will open automatically.
echo (Keep this command window open while using the app)
echo Press Ctrl+C in this window to stop the server.
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m streamlit run app.py
) else if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" -m streamlit run app.py
) else (
    echo [ERROR] Python executable was not found.
    echo Please make sure Python is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application encountered an error or stopped unexpectedly.
    pause
)
