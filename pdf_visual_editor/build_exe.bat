@echo off
echo ========================================
echo PDF Visual Editor - Build Executable
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
)

echo.
echo Installing/Updating PyInstaller...
pip install pyinstaller --quiet

echo.
echo Building executable with PyInstaller...
pyinstaller pdf_visual_editor.spec --clean --noconfirm

echo.
echo ========================================
if exist "dist\PDF Visual Editor.exe" (
    echo SUCCESS! Executable created successfully.
    echo.
    echo Location: dist\PDF Visual Editor.exe
    echo File size:
    dir "dist\PDF Visual Editor.exe" | find "PDF Visual Editor.exe"
    echo.
    echo You can now distribute this .exe file to users.
    echo The executable includes all dependencies and resources.
) else (
    echo ERROR! Build failed. Check the output above for errors.
    echo.
    echo Common issues:
    echo - Missing dependencies in requirements.txt
    echo - Resource files not found
    echo - Antivirus blocking PyInstaller
)
echo ========================================
echo.

pause
