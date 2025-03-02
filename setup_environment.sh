#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up environment for Differential Equation Analyzer${NC}"

# Check for Python 3.9
echo -e "${YELLOW}Checking for Python 3.9...${NC}"

PYTHON_CMD=""
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
    echo -e "${GREEN}Found Python 3.9 as 'python3.9'${NC}"
elif command -v python &> /dev/null && [[ $(python --version 2>&1) == *"Python 3.9"* ]]; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Found Python 3.9 as 'python'${NC}"
elif command -v python3 &> /dev/null && [[ $(python3 --version 2>&1) == *"Python 3.9"* ]]; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Found Python 3.9 as 'python3'${NC}"
else
    echo -e "${RED}Python 3.9 not found. This application requires Python 3.9.${NC}"
    echo -e "${YELLOW}Please install Python 3.9 and try again.${NC}"
    exit 1
fi

# Check for existing virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Existing virtual environment found.${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf venv
        echo -e "${YELLOW}Creating new virtual environment with $PYTHON_CMD...${NC}"
        $PYTHON_CMD -m venv venv
    fi
else
    echo -e "${YELLOW}Creating virtual environment with $PYTHON_CMD...${NC}"
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source venv/bin/activate
fi

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements-simplified.txt

echo -e "${GREEN}Environment setup complete!${NC}"
echo -e "${YELLOW}To activate this environment in the future, run:${NC}"
echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo
echo -e "${YELLOW}To run the application:${NC}"
echo "./run_app_simple.sh" 