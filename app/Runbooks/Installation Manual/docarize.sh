#!/bin/bash

# Check if docker-compose is installed
if ! command -v docker-compose &>/dev/null; then
    echo "❌ ERROR: docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ docker-compose is installed."

# Check if docker-compose.yml exists in the current directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ ERROR: docker-compose.yml not found in the current directory."
    exit 1
fi

echo "✅ Found docker-compose.yml, proceeding..."

# Run docker-compose build
echo "🚀 Building Docker images..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "❌ ERROR: docker-compose build failed."
    exit 1
fi
echo "✅ Build completed successfully."

# Run docker-compose up -d
echo "🚀 Starting Docker containers..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ ERROR: docker-compose up failed."
    exit 1
fi
echo "✅ Containers started successfully."

# Run docker ps
echo "🔍 Checking running containers..."
docker ps

echo "✅ Process completed successfully. Exiting..."
exit 0
