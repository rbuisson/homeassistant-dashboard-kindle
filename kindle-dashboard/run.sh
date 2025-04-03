#!/bin/bash
set -e

# Start a simple HTTP server
cd /app/www
exec python3 -m http.server 8080
