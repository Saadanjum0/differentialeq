#!/bin/bash

# Production deployment script for Differential Equation Analyzer

# Exit on error
set -e

echo "Starting deployment process..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Generate a new secret key for this deployment
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export PRODUCTION=True

# Check if we're running with SSL certificates
if [ -f "cert.pem" ] && [ -f "key.pem" ]; then
    echo "SSL certificates found, starting with HTTPS..."
    gunicorn --bind 0.0.0.0:443 --certfile=cert.pem --keyfile=key.pem --workers=4 wsgi:app
else
    echo "No SSL certificates found, starting with HTTP only (not recommended for production)..."
    echo "For production, generate SSL certificates with:"
    echo "openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365"
    gunicorn --bind 0.0.0.0:80 --workers=4 wsgi:app
fi 