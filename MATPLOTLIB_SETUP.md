# Matplotlib Setup for Serverless Deployment

This document outlines the changes made to enable matplotlib on Vercel and Netlify serverless environments.

## Changes Made

### 1. Requirements.txt

- Uncommented matplotlib in requirements.txt:
```
matplotlib==3.4.3
```

### 2. Vercel Configuration

- Updated `vercel.json`:
  - Increased `maxLambdaSize` from 15MB to 50MB to accommodate matplotlib
  - Added `MATPLOTLIB_USE=Agg` environment variable

- Updated `build.sh`:
  - Added system dependencies installation for matplotlib on Linux
  - Added verification step to ensure matplotlib is installed

- Updated `api/index.py`:
  - Added early matplotlib import with Agg backend before importing the app
  - Set `VERCEL_ENV` environment variable in the request context

### 3. Netlify Configuration

- Updated `netlify-build.sh`:
  - Added system dependencies installation for matplotlib
  - Added verification step to ensure matplotlib is installed

### 4. Application Code

- Updated `app.py`:
  - Added early matplotlib import with proper error handling
  - Replaced conditional checks based on `'matplotlib' in sys.modules` with a global `MATPLOTLIB_AVAILABLE` flag
  - Fixed indentation issues in the plot generation function

### 5. Testing

- Created `test_matplotlib.py` script to verify matplotlib works correctly
- The script tests:
  - Importing matplotlib
  - Creating a simple plot
  - Saving to a file
  - Base64 encoding (used in the app)

## Troubleshooting

If matplotlib is not working in your deployment:

1. Check the build logs for any errors related to matplotlib installation
2. Ensure the Agg backend is being used (required for serverless environments)
3. Verify system dependencies are installed (libfreetype6-dev, libpng-dev on Linux)
4. Check the lambda size limit (should be at least 50MB for matplotlib)

## Local Development

For local development:

1. Ensure you're using the virtual environment Python:
   ```
   source venv/bin/activate
   ```

2. Run the test script to verify matplotlib is working:
   ```
   python test_matplotlib.py
   ```

3. If you see a "matplotlib_test.png" file created, matplotlib is working correctly! 