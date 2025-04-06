#!/bin/bash
set -e

echo "Starting Kindle Dashboard addon..."

# Ensure the www directory exists
if [ ! -d "/app/www" ]; then
    echo "Error: /app/www directory not found!"
    exit 1
fi

# If we have ingress, create an nginx.conf that uses Home Assistant auth headers
if [ -n "${SUPERVISOR_TOKEN}" ]; then
    echo "Supervisor token detected - setting up for ingress"

    # If Python's http.server is not enough for CORS issues, we can set up a simple nginx server later
    # For now, we'll just add a note about how to access this addon
    echo "For best results, access this addon through Home Assistant UI"
    echo "Direct access URL: http://homeassistant:8080"
fi

echo "Serving files from /app/www"
cd /app/www

# Start the server in the foreground
echo "Starting HTTP server on port 8080..."
exec python3 -m http.server 8080
