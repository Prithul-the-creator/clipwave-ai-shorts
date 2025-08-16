#!/bin/bash

echo "🚀 ClipWave AI Shorts - Railway Deployment Script"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found. Please run this script from the project root."
    exit 1
fi

# Check if required files exist
echo "📋 Checking required files..."
required_files=("backend/main.py" "backend/video_processor.py" "requirements-deploy.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - Missing!"
    exit 1
fi
done

# Check environment variables
echo ""
echo "🔧 Environment Variables Check:"
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set (will need to be set in Railway)"
else
    echo "✅ OPENAI_API_KEY is set"
fi

if [ -z "$YOUTUBE_COOKIES_B64" ]; then
    echo "⚠️  YOUTUBE_COOKIES_B64 not set (will need to be set in Railway)"
else
    echo "✅ YOUTUBE_COOKIES_B64 is set"
fi

echo ""
echo "📦 Building Docker image..."
docker build -t clipwave-ai-shorts .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful"
else
    echo "❌ Docker build failed"
    exit 1
fi

echo ""
echo "🧪 Testing Docker container..."
docker run --rm -d --name clipwave-test -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e YOUTUBE_COOKIES_B64="$YOUTUBE_COOKIES_B64" \
    clipwave-ai-shorts

# Wait for container to start
sleep 10

# Test health endpoint
echo "Testing health endpoint..."
curl -f http://localhost:8000/api/health
if [ $? -eq 0 ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test storage endpoint
echo "Testing storage endpoint..."
curl -f http://localhost:8000/api/test-storage
if [ $? -eq 0 ]; then
    echo "✅ Storage test passed"
else
    echo "❌ Storage test failed"
fi

# Stop test container
docker stop clipwave-test

echo ""
echo "🎉 Deployment preparation complete!"
    echo ""
echo "📋 Next steps for Railway deployment:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Fix video file not found error'"
echo "   git push"
echo ""
echo "2. In Railway dashboard, ensure these environment variables are set:"
echo "   - OPENAI_API_KEY"
echo "   - YOUTUBE_COOKIES_B64"
echo "   - PORT=8000"
echo ""
echo "3. Deploy to Railway and test the endpoints:"
echo "   - /api/health"
echo "   - /api/test-storage"
echo "   - /api/test"
echo ""
echo "4. If you still get 'video file not found' errors, check the logs:"
echo "   railway logs"
echo ""
echo "🔧 Troubleshooting:"
echo "- The app now stores video data in memory as a fallback for Railway's ephemeral storage"
echo "- Check /api/test-storage endpoint to verify storage directory access"
echo "- Video files are served from multiple possible paths"
echo "- If file serving fails, videos are served from base64 encoded data" 