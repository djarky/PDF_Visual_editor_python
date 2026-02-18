#!/bin/sh

# run_tests.sh - GameQt Test Runner Wrapper (POSIX compliant)

# Get the directory where the script is located
SCRIPT_PATH="$0"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Display help message
show_help() {
    echo "Usage: $0 [options] [args...]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message and exit"
    echo ""
    echo "All other arguments will be passed directly to the Python test runner."
}

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

# Check for virtual environment and set python executable
PYTHON_EXE="python3"
if [ -d "$PROJECT_ROOT/pdf_visual_editor/.venv" ]; then
    echo "Using virtual environment at $PROJECT_ROOT/pdf_visual_editor/.venv..."
    PYTHON_EXE="$PROJECT_ROOT/pdf_visual_editor/.venv/bin/python3"
elif [ -d "$PROJECT_ROOT/pdf_visual_editor/venv" ]; then
    echo "Using virtual environment at $PROJECT_ROOT/pdf_visual_editor/venv..."
    PYTHON_EXE="$PROJECT_ROOT/pdf_visual_editor/venv/bin/python3"
fi

# Set PYTHONPATH to include the project root and the app directory
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/pdf_visual_editor:$PYTHONPATH"

# Ensure python is available
if ! "$PYTHON_EXE" --version > /dev/null 2>&1; then
    echo "Error: python is not installed or not in PATH."
    exit 1
fi

echo "Starting GameQt Test Runner..."
# Pass all script arguments to the Python runner
"$PYTHON_EXE" "$SCRIPT_DIR/runner.py" "$@"
EXIT_CODE=$?

exit $EXIT_CODE
