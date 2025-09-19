@echo off
echo Building CS2 Font Changer executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo Cleaning completed.
echo.

REM Install/upgrade required packages
echo Installing dependencies...
pip install --upgrade pyinstaller PyQt5 fonttools requests
echo.

REM Build with PyInstaller using spec file
echo Building executable...
pyinstaller CS2FontChanger.spec

echo.
if exist "dist/CS2FontChanger.exe" (
    echo SUCCESS: Executable created at dist/CS2FontChanger.exe
    echo File size: 
    dir "dist/CS2FontChanger.exe" | find "CS2FontChanger.exe"
) else (
    echo ERROR: Build failed - executable not found
)

echo.
pause