#!/bin/bash

echo "========================================"
echo "PDF Visual Editor - Build Linux Binary"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found. Using system Python."
fi

echo ""
echo "Installing/Updating PyInstaller..."
pip install pyinstaller --quiet

echo ""
echo "Building executable with PyInstaller..."
pyinstaller pdf_visual_editor.spec --clean --noconfirm

echo ""
echo "========================================"
if [ -f "dist/PDF Visual Editor" ]; then
    echo "SUCCESS! Executable created successfully."
    echo ""
    echo "Location: dist/PDF Visual Editor"
    echo "File size:"
    ls -lh "dist/PDF Visual Editor" | awk '{print $5, $9}'
    echo ""
    echo "Making executable..."
    chmod +x "dist/PDF Visual Editor"
    echo ""
    echo "You can now distribute this binary to Linux users."
    echo "The executable includes all dependencies and resources."
else
    echo "ERROR! Build failed. Check the output above for errors."
    echo ""
    echo "Common issues:"
    echo "- Missing dependencies in requirements.txt"
    echo "- Resource files not found"
    echo "- Missing system libraries (Qt dependencies)"
fi
echo "========================================"
echo ""
