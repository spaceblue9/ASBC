@echo off
title ASBC Converter Pro - Build Script
color 0A

echo.
echo  ============================================
echo   ASBC Converter Pro - Build to .EXE
echo  ============================================
echo.

echo [1/3] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: pip install failed
    pause & exit /b 1
)

echo [2/3] Building .exe ...
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=ea.ico ^
  --name="ASBC Converter Pro" ^
  --add-data "ea.ico;." ^
  --add-data "ASBC-Config.ini;." ^
  ASBC_GUI.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause & exit /b 1
)

echo [3/3] Build complete!
echo.
echo  Output: dist\ASBC Converter Pro.exe
echo.
echo  *** Do NOT include keygen.py in distribution ***
echo.
pause
