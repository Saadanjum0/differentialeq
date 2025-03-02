#!/bin/bash

# Exit on error
set -e

# Configuration
PORT=${PORT:-5001}
HOST=${HOST:-127.0.0.1}

# Kill any existing Python processes running the app
echo "Checking for existing Flask processes..."
pkill -f "python.*app.py" > /dev/null 2>&1 || true

# Wait a moment for ports to be released
sleep 1

# Determine Python path
if [ -d "venv" ]; then
    # Use virtual environment if it exists
    if [ -f "venv/bin/python" ]; then
        PYTHON_PATH="venv/bin/python"
    elif [ -f "venv/Scripts/python.exe" ]; then
        # Windows path
        PYTHON_PATH="venv/Scripts/python.exe"
    else
        echo "Virtual environment found but Python executable not found. Using system Python."
        PYTHON_PATH="python"
    fi
else
    # Use system Python if no virtual environment
    PYTHON_PATH="python"
fi

# Check if Python is available
if ! command -v $PYTHON_PATH &> /dev/null; then
    echo "Error: Python not found at $PYTHON_PATH"
    echo "Please ensure Python is installed and virtual environment is set up correctly."
    exit 1
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Run the application
echo "Starting the application on $HOST:$PORT..."
$PYTHON_PATH app.py --port=$PORT --host=$HOST 