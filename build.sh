#!/bin/bash

# Exit on error
set -e

echo "Starting Vercel build process..."

# Print Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p .vercel/output/static
mkdir -p .vercel/output/functions

# Copy static files
cp -r static/* .vercel/output/static/

# Copy API files
cp -r api/* .vercel/output/functions/

echo "Build completed successfully!" 