#!/bin/bash

# Kill any existing Python processes running the app
echo "Checking for existing Flask processes..."
pkill -f "python.*app.py" > /dev/null 2>&1

# Wait a moment for ports to be released
sleep 1

# Run the differential equation application using the virtual environment's Python
echo "Starting the application on port 5001..."
/Users/saad/Desktop/differential-equation-app/venv/bin/python -c "
import sys
from flask import Flask
import app

# Override the port in the app
if __name__ == '__main__':
    try:
        app.app.run(debug=True, port=5001)
    except OSError as e:
        if 'Address already in use' in str(e):
            print('Port 5001 is also in use. Please manually kill the processes using:')
            print('pkill -f \"python.*app.py\"')
            sys.exit(1)
        else:
            raise e
" 