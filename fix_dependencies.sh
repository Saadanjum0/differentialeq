#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python --version 2>&1)
echo "Current Python version: $python_version"

# Check if Python version is 3.9.x
if [[ $python_version != *"Python 3.9"* ]]; then
    echo -e "${RED}Warning: This application is designed for Python 3.9.x${NC}"
    echo -e "${YELLOW}You may encounter compatibility issues with $python_version${NC}"
    
    # Check if Python 3.9 is available
    if command -v python3.9 &> /dev/null; then
        echo -e "${GREEN}Python 3.9 is available as 'python3.9'${NC}"
        echo -e "${YELLOW}Consider creating a virtual environment with Python 3.9:${NC}"
        echo "python3.9 -m venv venv"
        echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    else
        echo -e "${YELLOW}Python 3.9 is not available. Consider installing it for best compatibility.${NC}"
    fi
fi

# Check for virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}No active virtual environment detected.${NC}"
    
    # Check if venv directory exists
    if [[ -d "venv" ]]; then
        echo -e "${YELLOW}Virtual environment directory 'venv' exists but is not activated.${NC}"
        echo -e "${YELLOW}Activate it with:${NC}"
        echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    else
        echo -e "${YELLOW}Consider creating a virtual environment:${NC}"
        echo "python -m venv venv"
        echo "source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    fi
else
    echo -e "${GREEN}Using virtual environment: ${VIRTUAL_ENV}${NC}"
fi

echo -e "${YELLOW}Checking and installing dependencies...${NC}"
pip install --upgrade pip

# Install dependencies with specific versions
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt

# Check for common issues with scientific packages
echo -e "${YELLOW}Checking for common issues with scientific packages...${NC}"

# Check NumPy
echo -e "${YELLOW}Verifying NumPy installation...${NC}"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')" || {
    echo -e "${RED}NumPy verification failed. Attempting to reinstall...${NC}"
    pip uninstall -y numpy
    pip install numpy==1.20.3
}

# Check SymPy
echo -e "${YELLOW}Verifying SymPy installation...${NC}"
python -c "import sympy; print(f'SymPy version: {sympy.__version__}')" || {
    echo -e "${RED}SymPy verification failed. Attempting to reinstall...${NC}"
    pip uninstall -y sympy
    pip install sympy==1.9
}

# Check Matplotlib
echo -e "${YELLOW}Verifying Matplotlib installation...${NC}"
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')" || {
    echo -e "${RED}Matplotlib verification failed. Attempting to reinstall...${NC}"
    pip uninstall -y matplotlib
    pip install matplotlib==3.4.3
}

# Check Flask and extensions
echo -e "${YELLOW}Verifying Flask and extensions...${NC}"
python -c "import flask; print(f'Flask version: {flask.__version__}')" || {
    echo -e "${RED}Flask verification failed. Attempting to reinstall...${NC}"
    pip uninstall -y flask
    pip install flask==2.0.1
}

python -c "import flask_limiter; print(f'Flask-Limiter version: {flask_limiter.__version__}')" || {
    echo -e "${RED}Flask-Limiter verification failed. Attempting to reinstall...${NC}"
    pip uninstall -y flask-limiter
    pip install flask-limiter==2.8.1
}

echo -e "${GREEN}Dependency check and installation completed!${NC}"
echo -e "${YELLOW}You can now run the application with:${NC}"
echo "./run_app_simple.sh" 