#!/bin/bash

# Exit on error
set -e

echo "Starting Netlify build process..."

# Create static directory if it doesn't exist
mkdir -p static

# Copy static assets
echo "Copying static assets..."
cp -r static/css static/ || echo "No CSS files to copy"
cp -r static/js static/ || echo "No JS files to copy"

# Copy HTML files
if [ -d "templates" ]; then
  echo "Copying HTML templates..."
  cp -r templates/index.html static/index.html || echo "No index.html to copy"
else
  echo "No templates directory found, checking for static/index.html..."
  # If index.html is already in static directory, we don't need to copy it
  if [ ! -f "static/index.html" ]; then
    echo "WARNING: No index.html found in static directory"
  fi
fi

# Set up Python for functions
if [ -d "netlify/functions" ]; then
  echo "Setting up Python for Netlify functions..."
  if [ -f "netlify/requirements.txt" ]; then
    echo "Installing Python dependencies for functions..."
    pip install -r netlify/requirements.txt
  fi
fi

echo "Build process completed!" 