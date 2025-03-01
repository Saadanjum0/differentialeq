#!/bin/bash

# Exit on error
set -e

echo "Starting Vercel build process..."

# Print Python version
python --version

# Install system dependencies for matplotlib (if on Linux)
if [ "$(uname)" == "Linux" ]; then
    echo "Installing system dependencies for matplotlib..."
    apt-get update -y || true
    apt-get install -y libfreetype6-dev libpng-dev || true
fi

# Install dependencies
pip install -r requirements.txt

# Verify matplotlib is installed
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')"

# Generate favicons if ImageMagick is available
if command -v convert &> /dev/null; then
    echo "Generating favicons..."
    ./generate_favicons.sh
else
    echo "ImageMagick not found, skipping favicon generation."
    # Create a simple favicon.ico if it doesn't exist
    if [ ! -f static/favicon.ico ]; then
        echo "Creating a placeholder favicon.ico"
        # This is a 1x1 transparent pixel
        echo -ne '\x00\x00\x01\x00\x01\x00\x01\x01\x00\x00\x01\x00\x18\x00\x0A\x00\x00\x00\x16\x00\x00\x00\x28\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' > static/favicon.ico
    fi
fi

# Create necessary directories
mkdir -p .vercel/output/static
mkdir -p .vercel/output/functions

# Copy static files
cp -r static/* .vercel/output/static/

# Copy API files
cp -r api/* .vercel/output/functions/

echo "Build completed successfully!" 