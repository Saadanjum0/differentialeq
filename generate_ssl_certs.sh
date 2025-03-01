#!/bin/bash

# Script to generate self-signed SSL certificates for testing
# Note: For production, you should use proper certificates from a trusted CA

echo "Generating self-signed SSL certificates for testing..."
echo "WARNING: These are for testing only. For production, use certificates from a trusted CA."

# Generate a private key and a self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Department/CN=localhost"

echo "Certificates generated:"
echo "  - cert.pem (public certificate)"
echo "  - key.pem (private key)"
echo ""
echo "You can now run ./deploy.sh to start the server with HTTPS." 