#!/bin/bash

# Print commands as they are executed
set -x

echo "Starting Netlify build process..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Ensure we're using the system Python
export PATH="/usr/bin:$PATH"
unset PYTHONPATH
unset PYTHONHOME

# Check Python version
echo "Checking Python version..."
/usr/bin/python3 --version || true
/usr/bin/python --version || true

# Install pip if needed
echo "Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
/usr/bin/python3 get-pip.py --user || /usr/bin/python get-pip.py --user

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Install system dependencies for matplotlib
echo "Installing system dependencies for matplotlib..."
if [ -x "$(command -v apt-get)" ]; then
  sudo apt-get update -y || true
  sudo apt-get install -y python3-dev python3-pip python3-venv libfreetype6-dev libpng-dev || true
elif [ -x "$(command -v yum)" ]; then
  sudo yum install -y python3-devel freetype-devel libpng-devel || true
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
/usr/bin/python3 -m venv .venv || /usr/bin/python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Verify matplotlib is installed
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')" || echo "WARNING: Matplotlib not installed correctly"

# Create static directory structure
mkdir -p static/css
mkdir -p static/js
echo "Created directory structure"

# Copy CSS files
echo "Copying CSS files..."
if [ -f "static/css/styles.css" ]; then
    echo "Found styles.css in static/css..."
    cp -v static/css/styles.css static/css/styles.css.bak
    chmod 644 static/css/styles.css.bak
elif [ -f "templates/static/css/styles.css" ]; then
    echo "Found styles.css in templates/static/css..."
    cp -v templates/static/css/styles.css static/css/styles.css
    chmod 644 static/css/styles.css
else
    echo "Creating styles.css with full styles..."
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

# Verify CSS file exists and has content
if [ ! -s "static/css/styles.css" ]; then
    echo "ERROR: styles.css is empty or missing!"
    exit 1
fi

echo "CSS files in static/css:"
ls -la static/css

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
    pip install --no-cache-dir -r netlify/requirements.txt || echo "WARNING: Failed to install Python dependencies"
  fi
fi

echo "Build process completed!"
# Exit with success
exit 0 