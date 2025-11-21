@echo off
cd /d "%~dp0"

if exist .venv (
    set VENV_DIR=.venv
) else if exist venv (
    set VENV_DIR=venv
) else (
    echo Creating virtual environment...
    python -m venv .venv
    set VENV_DIR=.venv
)

call %VENV_DIR%\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Starting PDF Visual Editor...
python main.py
pause
