@echo off
REM Build script for Chess Bot GUI Executable and Installer

echo.
echo ========================================
echo Chess Bot GUI - Build Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install dependencies
echo [1/4] Installing dependencies...
pip install -r requirements-gui.txt
pip install pyinstaller

REM Build executable
echo [2/4] Building executable with PyInstaller...
python build_exe.py

if not exist "dist\ChessBot.exe" (
    echo ERROR: Failed to build executable.
    pause
    exit /b 1
)

REM Check NSIS
echo [3/4] Checking for NSIS...
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: NSIS not found. Skipping installer creation.
    echo Download NSIS from: https://nsis.sourceforge.io/download
    echo Then run: makensis chess_bot_installer.nsi
) else (
    echo [4/4] Building installer...
    makensis chess_bot_installer.nsi
    if exist "ChessBotSetup.exe" (
        echo.
        echo SUCCESS! Build complete.
        echo - Portable: dist\ChessBot.exe
        echo - Installer: ChessBotSetup.exe
    )
)

echo.
echo Build complete! Press any key to exit.
pause
