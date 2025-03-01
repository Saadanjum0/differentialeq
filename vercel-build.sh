#!/bin/bash

# Exit on error
set -e

echo "Starting Vercel build process..."

# Ensure we're using Python 3.9
export PYTHON_VERSION=3.9

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/css
mkdir -p static/js

# Copy static files
if [ -d "static" ]; then
  echo "Static directory exists, copying files..."
  cp -r static/* .vercel/output/static/
fi

# Copy CSS files
if [ -f "static/css/styles.css" ]; then
  echo "Found styles.css, ensuring it's properly copied..."
  cp -v static/css/styles.css static/css/styles.css
  chmod 644 static/css/styles.css
else
  echo "Creating minimal CSS file..."
  cat > static/css/styles.css << 'EOL'
/* Modern CSS reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #2A93D5, #3454D1);
    color: white;
    text-align: center;
    padding: 2rem;
}

.primary-btn {
    background-color: #2A93D5;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.primary-btn:hover {
    background-color: #2484c0;
}

.input-group {
    margin-bottom: 1.2rem;
}

.input-group input {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
}

.example-box {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

.use-example-btn {
    background-color: #e9ecef;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    color: #495057;
    cursor: pointer;
    margin-top: 10px;
}
EOL
  chmod 644 static/css/styles.css
fi

# Ensure index.html exists
if [ -f "templates/index.html" ]; then
  echo "Copying index.html from templates..."
  cp -v templates/index.html static/index.html
  # Update CSS path in index.html
  sed -i 's|href="{{ url_for(\'static\', filename=\'css/styles.css\') }}"|href="/static/css/styles.css?v=1.0.2"|g' static/index.html
fi

echo "Build process completed!" 