#!/bin/bash

# Exit on error
set -e

echo "Generating favicon files from SVG..."

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is required but not installed. Please install it first."
    echo "On macOS: brew install imagemagick"
    echo "On Ubuntu: sudo apt-get install imagemagick"
    exit 1
fi

# Create directories if they don't exist
mkdir -p static/icons

# Generate favicon.ico (multiple sizes in one file)
convert -background none static/favicon.svg -define icon:auto-resize=16,32,48,64 static/favicon.ico

# Generate PNG favicons
convert -background none static/favicon.svg -resize 16x16 static/icons/favicon-16x16.png
convert -background none static/favicon.svg -resize 32x32 static/icons/favicon-32x32.png
convert -background none static/favicon.svg -resize 180x180 static/icons/apple-touch-icon.png
convert -background none static/favicon.svg -resize 192x192 static/icons/android-chrome-192x192.png
convert -background none static/favicon.svg -resize 512x512 static/icons/android-chrome-512x512.png

# Generate Open Graph image
convert -background none static/favicon.svg -resize 1200x630 -background "#ffffff" -flatten static/og-image.png

# Copy favicon.ico to static root for browsers that look for it there
cp static/favicon.ico static/

echo "Favicon generation complete!" 