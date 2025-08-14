#!/bin/bash

# ClipWave AI Shorts - Docker Deployment Script

set -e

echo "🚀 Starting ClipWave AI Shorts deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo "   Opening Docker Desktop..."
    open -a Docker
    echo "   Please wait for Docker to start and then run this script again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    cat > .env << EOF
# ClipWave AI Shorts Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_COOKIES_B64=your_base64_encoded_cookies_here
EOF
    echo "⚠️  Please edit .env file with your actual API keys and cookies before continuing."
    echo "   You can get the YOUTUBE_COOKIES_B64 value by running: python prepare_deployment.py"
    exit 1
fi

# Load environment variables
source .env

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$YOUTUBE_COOKIES_B64" ] || [ "$YOUTUBE_COOKIES_B64" = "your_base64_encoded_cookies_here" ]; then
    echo "❌ YOUTUBE_COOKIES_B64 not set in .env file"
    echo "   Run: python prepare_deployment.py to get the cookies value"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create storage directory if it doesn't exist
mkdir -p storage/videos

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down --remove-orphans

# Build the Docker image
echo "🔨 Building Docker image..."
docker compose build --no-cache

# Start the application
echo "🚀 Starting ClipWave AI Shorts..."
docker compose up -d

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Open your browser and go to: http://localhost:8000"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker compose logs -f"
    echo "   Stop app:  docker compose down"
    echo "   Restart:   docker compose restart"
else
    echo "❌ Application failed to start. Check logs with: docker compose logs"
    exit 1
fi 