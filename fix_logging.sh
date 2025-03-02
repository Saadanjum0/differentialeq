#!/bin/bash
set -e

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Fixing logging configuration...${NC}"

# Check if logging_config.py exists
if [ -f "logging_config.py" ]; then
    echo -e "${GREEN}logging_config.py already exists.${NC}"
else
    echo -e "${YELLOW}Creating logging_config.py...${NC}"
    cat > logging_config.py << 'EOL'
import os
import logging
import time
from logging.handlers import RotatingFileHandler
from flask import request, g

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logging(app):
    """Configure logging for the application"""
    # Set up basic configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a file handler for detailed logs
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Create a file handler for errors only
    error_handler = RotatingFileHandler(
        'logs/error.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Add handlers to the app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    
    return app.logger

def log_request(app):
    """Log details about the current request"""
    # Skip logging for static files
    if request.path.startswith('/static'):
        return
    
    # Calculate request processing time if available
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
    else:
        duration = 0
    
    # Log request details
    app.logger.info(
        f"Request: {request.method} {request.path} "
        f"({request.remote_addr}) - "
        f"Duration: {duration:.4f}s"
    )

def log_error(app, error, status_code=500):
    """Log an error with details"""
    app.logger.error(
        f"Error {status_code}: {str(error)} - "
        f"URL: {request.url} - "
        f"Method: {request.method} - "
        f"IP: {request.remote_addr}"
    )
EOL
    echo -e "${GREEN}Created logging_config.py${NC}"
fi

# Create logs directory
echo -e "${YELLOW}Creating logs directory if it doesn't exist...${NC}"
mkdir -p logs
echo -e "${GREEN}Logs directory is ready.${NC}"

# Install required logging packages
echo -e "${YELLOW}Installing logging dependencies...${NC}"
pip install logging-formatter-anticrlf colorama

echo -e "${GREEN}Logging configuration fixed!${NC}"
echo -e "${YELLOW}You can now run the application with:${NC}"
echo "./run_app_improved.sh" 