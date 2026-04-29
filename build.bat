@echo off
title ASBC Converter Pro - Build Script
color 0A

echo.
echo  ============================================
echo   ASBC Converter Pro - Build to .EXE
echo  ============================================
echo.

echo [1/4] Upgrading PyInstaller...
pip install --upgrade pyinstaller --quiet

echo [2/4] Cleaning previous build cache...
if exist build  rmdir /s /q build
if exist dist   rmdir /s /q dist
if exist "ASBC Converter Pro.spec" del /q "ASBC Converter Pro.spec"

echo [3/4] Building .exe  (please wait 2-5 minutes)...
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=ea.ico ^
  --name="ASBC Converter Pro" ^
  --add-data "ea.ico;." ^
  --add-data "ASBC-Config.ini;." ^
  --copy-metadata numpy ^
  --copy-metadata pandas ^
  --collect-all openpyxl ^
  --hidden-import xlrd ^
  --noupx ^
  --exclude-module torch ^
  --exclude-module torchvision ^
  --exclude-module torchaudio ^
  --exclude-module tensorflow ^
  --exclude-module keras ^
  --exclude-module sklearn ^
  --exclude-module scipy ^
  --exclude-module matplotlib ^
  --exclude-module IPython ^
  --exclude-module jupyter ^
  --exclude-module notebook ^
  --exclude-module numba ^
  --exclude-module llvmlite ^
  --exclude-module transformers ^
  --exclude-module PIL ^
  --exclude-module cv2 ^
  --exclude-module imageio ^
  --exclude-module sympy ^
  --exclude-module zmq ^
  --exclude-module pyarrow ^
  ASBC_GUI.py

if errorlevel 1 (
    echo.
    echo  ERROR: Build failed
    pause & exit /b 1
)

echo [4/4] Build complete!
echo.
echo  ===================================================
echo   Output  :  dist\ASBC Converter Pro.exe
echo   *** อย่าแจก keygen.py ให้ลูกค้า ***
echo  ===================================================
echo.
pause
