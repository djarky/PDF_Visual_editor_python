#!/bin/bash

# Script to clean up Python cache files and directories

echo "Cleaning up Python cache files..."

# Find and delete __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# Find and delete .pyc files
echo "Removing .pyc files..."
find . -type f -name "*.pyc" -delete

# Find and delete .pyo files
echo "Removing .pyo files..."
find . -type f -name "*.pyo" -delete

# Find and delete .pyd files
echo "Removing .pyd files..."
find . -type f -name "*.pyd" -delete

# Optional: Remove .pytest_cache
if [ -d ".pytest_cache" ]; then
    echo "Removing .pytest_cache..."
    rm -rf .pytest_cache
fi

# Optional: Remove .coverage files
if [ -f ".coverage" ]; then
    echo "Removing .coverage..."
    rm -f .coverage
fi

echo "Python cache cleanup complete!"
