#!/bin/bash
set -e

# Print versions for debugging
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"
echo "System Python version:"
python --version || echo "Python not found in PATH"

# Try to find any Python 3 version
echo "Looking for Python 3..."
PYTHON_CMD=""

# Check for various Python commands in order of preference
for cmd in python3.9 python3.8 python3.7 python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>&1)
        echo "Found $cmd: $version"
        
        # Check if it's Python 3
        if [[ $version == *"Python 3"* ]]; then
            PYTHON_CMD=$cmd
            echo "Using $PYTHON_CMD"
            break
        else
            echo "$cmd is not Python 3, continuing search..."
        fi
    fi
done

# If no Python 3 found, use system Python as fallback
if [ -z "$PYTHON_CMD" ]; then
    echo "WARNING: No Python 3 found. Using system Python as fallback."
    PYTHON_CMD="python"
fi

echo "Selected Python command: $PYTHON_CMD ($(${PYTHON_CMD} --version 2>&1))"

# Install npm dependencies with legacy peer deps flag
echo "Installing npm dependencies..."
npm install --legacy-peer-deps

# Create necessary directories
mkdir -p static/css
mkdir -p static/js

# Install Python dependencies
echo "Installing Python dependencies..."
${PYTHON_CMD} -m pip install --upgrade pip || echo "Failed to upgrade pip, continuing with existing version"

# Use netlify-requirements.txt if it exists, otherwise fall back to requirements.txt
if [ -f "netlify-requirements.txt" ]; then
    echo "Using netlify-requirements.txt for dependencies..."
    ${PYTHON_CMD} -m pip install -r netlify-requirements.txt
else
    echo "Using requirements.txt for dependencies..."
    ${PYTHON_CMD} -m pip install -r requirements.txt
fi

# Copy static files
echo "Copying static files..."
if [ -d "static" ]; then
  cp -r static/* static/ || echo "Warning: Could not copy static files (possibly due to copying to itself)"
fi

# Ensure CSS file exists
if [ -f "static/css/styles.css" ]; then
  echo "CSS file found."
else
  echo "Creating minimal CSS file..."
  cat > static/css/styles.css << 'EOL'
/* Modern CSS Reset */
*, *::before, *::after { box-sizing: border-box; }
body, h1, h2, h3, h4, p, figure, blockquote, dl, dd { margin: 0; }
html { scroll-behavior: smooth; }
body {
  min-height: 100vh;
  text-rendering: optimizeSpeed;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333;
  background-color: #f8f9fa;
}
/* Base styles for the application */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
header {
  text-align: center;
  margin-bottom: 2rem;
}
.section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background-color: #2A93D5;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}
.btn:hover {
  background-color: #1c7eb9;
}
EOL
fi

# Ensure index.html exists in static directory
if [ -f "templates/index.html" ]; then
  echo "Copying index.html from templates..."
  cp templates/index.html static/index.html
  
  # Update CSS path in the HTML file
  sed -i.bak 's|href="/static/css/styles.css|href="css/styles.css|g' static/index.html
  sed -i.bak "s|src=\"{{ url_for('static', filename='js/script.js') }}\"|src=\"js/script.js\"|g" static/index.html
  rm -f static/index.html.bak
else
  echo "Error: templates/index.html not found!"
  exit 1
fi

# Copy JavaScript files
if [ -f "static/js/script.js" ]; then
  echo "JavaScript file found."
else
  if [ -f "static/js/netlify-script.js" ]; then
    echo "Copying Netlify-specific JavaScript..."
    cp static/js/netlify-script.js static/js/script.js
  else
    echo "Warning: No JavaScript file found."
  fi
fi

echo "Build completed successfully!" 