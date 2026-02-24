#!/bin/bash
# Quick start script for PDF Text Replacer

echo "🚀 Starting PDF Text Replacer..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running. Starting Docker Desktop..."
    open -a Docker
    echo "⏳ Waiting for Docker to start..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
    done
    echo "✓ Docker is ready"
fi

# Build and start the application
echo "🔨 Building Docker image..."
docker compose build

echo "🚀 Starting application..."
docker compose up -d

echo ""
echo "✓ PDF Text Replacer is running!"
echo "🌐 Access at: http://localhost:8501"
echo ""
echo "Commands:"
echo "  View logs:  docker compose logs -f"
echo "  Stop:       docker compose down"
echo "  Restart:    docker compose restart"
