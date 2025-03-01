#!/bin/bash

# Exit on error
set -e

echo "Starting Netlify build process..."

# Create static directory structure
mkdir -p static/css
mkdir -p static/js

# Copy static assets with better error handling
echo "Copying static assets..."
if [ -d "static/css" ]; then
  echo "Copying CSS files..."
  find static/css -type f -name "*.css" -exec cp {} static/css/ \;
else
  echo "WARNING: No CSS directory found"
fi

if [ -d "static/js" ]; then
  echo "Copying JS files..."
  find static/js -type f -name "*.js" -exec cp {} static/js/ \;
else
  echo "WARNING: No JS directory found"
fi

# Copy HTML files
if [ -d "templates" ]; then
  echo "Copying HTML templates..."
  cp templates/index.html static/index.html || echo "WARNING: Failed to copy index.html from templates"
else
  echo "No templates directory found, checking for static/index.html..."
  if [ ! -f "static/index.html" ]; then
    echo "WARNING: No index.html found in static directory"
  fi
fi

# List the contents of the static directory for debugging
echo "Contents of static directory:"
find static -type f | sort

# Set up Python for functions
if [ -d "netlify/functions" ]; then
  echo "Setting up Python for Netlify functions..."
  if [ -f "netlify/requirements.txt" ]; then
    echo "Installing Python dependencies for functions..."
    pip install -r netlify/requirements.txt
  fi
fi

echo "Build process completed!" 