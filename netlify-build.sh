#!/bin/bash

# Exit on error
set -e

echo "Starting Netlify build process..."

# Create static directory structure
mkdir -p static/css
mkdir -p static/js

# Copy static assets with better error handling
echo "Copying static assets..."

# Explicitly copy CSS files with proper content type
echo "Copying CSS files..."
if [ -f "static/css/styles.css" ]; then
  echo "Found styles.css, copying to deployment directory..."
  cp static/css/styles.css static/css/styles.css
  # Ensure proper permissions
  chmod 644 static/css/styles.css
  echo "CSS file copied successfully"
else
  echo "WARNING: styles.css not found in static/css directory"
  # Try to find it elsewhere
  if [ -f "static/styles.css" ]; then
    echo "Found styles.css in static directory, moving to css folder..."
    cp static/styles.css static/css/styles.css
    chmod 644 static/css/styles.css
  fi
fi

# List CSS files for debugging
echo "CSS files in static/css:"
ls -la static/css

# Copy JS files
echo "Copying JS files..."
if [ -d "static/js" ]; then
  find static/js -type f -name "*.js" -exec cp {} static/js/ \;
  # Ensure proper permissions
  find static/js -type f -name "*.js" -exec chmod 644 {} \;
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