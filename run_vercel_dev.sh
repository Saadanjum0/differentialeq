#!/bin/bash
# Script to run the application locally using Vercel's development environment

# Set -e to exit on error
set -e

echo "Starting Vercel development environment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run Vercel dev
echo "Starting Vercel dev server..."
vercel dev

echo "Vercel dev server stopped." 