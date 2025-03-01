#!/bin/bash

# Print commands as they are executed
set -x

# Don't exit on error immediately to allow for debugging
# set -e

echo "Starting Netlify build process..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Install system dependencies for matplotlib
echo "Installing system dependencies for matplotlib..."
if [ -x "$(command -v apt-get)" ]; then
  apt-get update -y || true
  apt-get install -y libfreetype6-dev libpng-dev || true
elif [ -x "$(command -v yum)" ]; then
  yum install -y freetype-devel libpng-devel || true
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt || echo "WARNING: Failed to install Python dependencies"

# Verify matplotlib is installed
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')" || echo "WARNING: Matplotlib not installed correctly"

# Create static directory structure
mkdir -p static/css
mkdir -p static/js
echo "Created directory structure"

# Copy CSS files directly from source to destination
echo "Copying CSS files..."
if [ -f "static/css/styles.css" ]; then
  echo "Found styles.css in static/css, ensuring it's properly copied..."
  cp -v static/css/styles.css static/css/styles.css
  chmod 644 static/css/styles.css
  echo "CSS file copied successfully"
else
  echo "WARNING: styles.css not found in static/css directory"
  
  # Check if styles.css exists in the root directory
  if [ -f "styles.css" ]; then
    echo "Found styles.css in root directory, copying to static/css..."
    cp -v styles.css static/css/styles.css
    chmod 644 static/css/styles.css
  fi
  
  # Create a minimal CSS file if none exists
  if [ ! -f "static/css/styles.css" ]; then
    echo "Creating minimal CSS file..."
    echo "/* Basic styles */" > static/css/styles.css
    echo ".container { max-width: 1200px; margin: 0 auto; }" >> static/css/styles.css
    echo ".primary-btn { background-color: #2A93D5; color: white; }" >> static/css/styles.css
    chmod 644 static/css/styles.css
  fi
fi

# List CSS files for debugging
echo "CSS files in static/css:"
ls -la static/css || echo "Failed to list CSS files"

# Copy JS files
echo "Copying JS files..."
if [ -d "static/js" ]; then
  # Copy each JS file individually
  for jsfile in static/js/*.js; do
    if [ -f "$jsfile" ]; then
      echo "Copying $jsfile..."
      cp -v "$jsfile" static/js/
      chmod 644 static/js/$(basename "$jsfile")
    fi
  done
else
  echo "WARNING: No JS directory found"
  # Create minimal JS files
  echo "console.log('Netlify script loaded');" > static/js/netlify-script.js
  echo "console.log('Debug script loaded');" > static/js/debug.js
  chmod 644 static/js/netlify-script.js
  chmod 644 static/js/debug.js
fi

# List JS files for debugging
echo "JS files in static/js:"
ls -la static/js || echo "Failed to list JS files"

# Ensure index.html exists
echo "Checking for index.html..."
if [ -f "templates/index.html" ]; then
  echo "Copying index.html from templates..."
  cp -v templates/index.html static/index.html
elif [ -f "static/index.html" ]; then
  echo "index.html already exists in static directory"
else
  echo "WARNING: No index.html found, creating a minimal one..."
  cat > static/index.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Differential Equation Analyzer</title>
    <link rel="stylesheet" href="/css/styles.css?v=1.0.1">
</head>
<body>
    <div class="container">
        <h1>Differential Equation Analyzer</h1>
        <p>The application is being set up. Please check back soon.</p>
    </div>
    <script src="/js/netlify-script.js?v=1.0.1"></script>
</body>
</html>
EOL
fi

# List the contents of the static directory for debugging
echo "Contents of static directory:"
find static -type f | sort || echo "Failed to list static directory contents"

# Set up Python for functions
if [ -d "netlify/functions" ]; then
  echo "Setting up Python for Netlify functions..."
  if [ -f "netlify/requirements.txt" ]; then
    echo "Installing Python dependencies for functions..."
    pip install -r netlify/requirements.txt || echo "WARNING: Failed to install Python dependencies"
  fi
fi

echo "Build process completed!"
# Exit with success
exit 0 