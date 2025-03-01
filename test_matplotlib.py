#!/usr/bin/env python3
"""
Test script to verify matplotlib is working correctly.
This script creates a simple plot and saves it to a file.
"""

import sys
import os
import io
import base64

try:
    print("Importing matplotlib...")
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    
    print(f"Matplotlib version: {matplotlib.__version__}")
    print(f"Backend: {matplotlib.get_backend()}")
    
    # Create a simple plot
    print("Creating test plot...")
    x = np.linspace(-5, 5, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, linewidth=2.5, color='#2A93D5')
    plt.title("Test Plot: sin(x)", fontsize=14)
    plt.xlabel("x", fontsize=12)
    plt.ylabel("y", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save to a file
    output_file = "matplotlib_test.png"
    plt.savefig(output_file, format='png', dpi=100)
    plt.close()
    print(f"Plot saved to {output_file}")
    
    # Also test base64 encoding (used in the app)
    buf = io.BytesIO()
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, linewidth=2.5, color='#2A93D5')
    plt.title("Base64 Test", fontsize=14)
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    print(f"Base64 encoding successful. Length: {len(base64_str)} characters")
    print("Matplotlib is working correctly!")
    sys.exit(0)
    
except ImportError as e:
    print(f"ERROR: Failed to import matplotlib: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Matplotlib test failed: {e}")
    sys.exit(1) 