@echo off
echo ===================================
echo  Starting build process with PyInstaller...
echo ===================================

pyinstaller --onefile --windowed --add-data "web;web" main.py

echo.
echo ===================================
echo  Build complete.
echo  main.exe has been created in the 'dist' folder.
echo ===================================
echo.
pause