#!/bin/bash

# Kill any existing Python processes running the app
echo "Checking for existing Flask processes..."
pkill -f "python.*app.py" > /dev/null 2>&1

# Wait a moment for ports to be released
sleep 1

# Run the differential equation application using the virtual environment's Python
echo "Starting the application on port 5001..."
/Users/saad/Desktop/differential-equation-app/venv/bin/python app.py --port=5001 