FROM python:3.11-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy addon files
COPY run.sh /app/run.sh
COPY www /app/www

# Expose port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/app/run.sh"]