#!/bin/bash
# Script to deploy the application to Vercel

# Set -e to exit on error
set -e

echo "Preparing for Vercel deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Ensure static directory exists
if [ ! -d "static" ]; then
    echo "Error: static directory not found!"
    exit 1
fi

# Ensure API directory exists
if [ ! -d "api" ]; then
    echo "Error: api directory not found!"
    exit 1
fi

# Check for required files
if [ ! -f "vercel.json" ]; then
    echo "Error: vercel.json not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "All required files and directories found."

# Deploy to Vercel
echo "Deploying to Vercel..."
vercel --prod

echo "Deployment complete!"