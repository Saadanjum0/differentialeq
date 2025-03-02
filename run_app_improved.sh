#!/bin/bash

# Exit on error
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PORT=${PORT:-5001}
HOST=${HOST:-127.0.0.1}

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}No active virtual environment detected.${NC}"
    
    # Check if venv directory exists
    if [[ -d "venv" ]]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            source venv/Scripts/activate
        else
            # Unix/Linux/MacOS
            source venv/bin/activate
        fi
    else
        echo -e "${RED}No virtual environment found. Run ./setup_environment.sh first.${NC}"
        exit 1
    fi
fi

# Kill any existing Python processes running the app
echo -e "${YELLOW}Checking for existing Flask processes...${NC}"
pkill -f "python.*app.py" > /dev/null 2>&1 || true

# Wait a moment for ports to be released
sleep 1

# Check if app.py exists
if [[ ! -f "app.py" ]]; then
    echo -e "${RED}Error: app.py not found in the current directory.${NC}"
    exit 1
fi

# Check if required modules are installed
echo -e "${YELLOW}Checking required modules...${NC}"
python -c "import flask, numpy, sympy" 2>/dev/null || {
    echo -e "${RED}Missing required modules. Running dependency fix script...${NC}"
    ./fix_dependencies.sh
}

# Load environment variables if .env exists
if [[ -f ".env" ]]; then
    echo -e "${YELLOW}Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs) || true
fi

# Run the application
echo -e "${GREEN}Starting the application on $HOST:$PORT...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

# Run with proper error handling
python app.py --port=$PORT --host=$HOST || {
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 1 ]]; then
        echo -e "${RED}Application exited with an error.${NC}"
        echo -e "${YELLOW}Check the error message above or try running ./fix_dependencies.sh${NC}"
    elif [[ $EXIT_CODE -eq 130 ]]; then
        echo -e "${YELLOW}Application stopped by user.${NC}"
    else
        echo -e "${RED}Application exited with code $EXIT_CODE${NC}"
    fi
    exit $EXIT_CODE
} 