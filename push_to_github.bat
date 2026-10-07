@echo off
echo ========================================================
echo   Pushing MalVision to GitHub (ManasPatel126/MalVision)
echo ========================================================
echo.
echo Make sure you have created the empty repository on GitHub:
echo   https://github.com/new (Repository name: MalVision)
echo.
pause
echo.
echo Pushing to main branch...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Repository pushed to https://github.com/ManasPatel126/MalVision
) else (
    echo [ERROR] Push failed. Please verify that https://github.com/ManasPatel126/MalVision exists.
)
echo.
pause
