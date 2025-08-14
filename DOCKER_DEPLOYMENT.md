# 🐳 **ClipWave AI Shorts - Docker Deployment Guide**

## 🚀 **Quick Start**

### **Option 1: Automated Deployment (Recommended)**
```bash
# 1. Make sure you have the .env file with your API keys
# 2. Run the deployment script
./deploy.sh
```

### **Option 2: Manual Deployment**
```bash
# 1. Build and start with Docker Compose
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Stop the application
docker-compose down
```

## 📋 **Prerequisites**

### **Required Software:**
- ✅ **Docker** (version 20.10 or higher)
- ✅ **Docker Compose** (version 2.0 or higher)
- ✅ **Git** (to clone the repository)

### **Required API Keys:**
- ✅ **OpenAI API Key** (for GPT-4 video analysis)
- ✅ **YouTube Cookies** (base64 encoded for video downloading)

## 🔧 **Setup Instructions**

### **Step 1: Environment Configuration**

1. **Create `.env` file** in the project root:
```bash
# ClipWave AI Shorts Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_COOKIES_B64=your_base64_encoded_cookies_here
```

2. **Get your YouTube cookies** (if you haven't already):
```bash
cd backend
python ../prepare_deployment.py
```

3. **Copy the base64 string** from the script output and paste it in your `.env` file.

### **Step 2: Deploy with Docker**

#### **Automated Deployment:**
```bash
# Run the deployment script
./deploy.sh
```

#### **Manual Deployment:**
```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# Check if it's running
curl http://localhost:8000/health
```

### **Step 3: Access Your Application**

Once deployed, open your browser and go to:
```
http://localhost:8000
```

## 🐳 **Docker Configuration**

### **Dockerfile Features:**
- ✅ **Multi-stage build** for optimized image size
- ✅ **FFmpeg support** for video processing
- ✅ **Node.js and Python** in single container
- ✅ **Frontend build** during image creation
- ✅ **Health check endpoint** for monitoring

### **Docker Compose Features:**
- ✅ **Environment variable injection**
- ✅ **Volume mounting** for persistent storage
- ✅ **Health checks** for container monitoring
- ✅ **Automatic restart** on failure
- ✅ **Port mapping** (8000:8000)

## 📊 **Monitoring & Management**

### **View Application Logs:**
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs clipwave-ai
```

### **Container Management:**
```bash
# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Remove containers and volumes
docker-compose down -v
```

### **Health Monitoring:**
```bash
# Check application health
curl http://localhost:8000/health

# Check container status
docker-compose ps
```

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **1. Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Stop the conflicting service or change the port in docker-compose.yml
```

#### **2. Environment Variables Not Set**
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are loaded
docker-compose config
```

#### **3. Build Failures**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### **4. FFmpeg Issues**
```bash
# Check if FFmpeg is installed in container
docker-compose exec clipwave-ai ffmpeg -version
```

### **Debug Commands:**
```bash
# Enter the container shell
docker-compose exec clipwave-ai bash

# Check container resources
docker stats

# View container details
docker-compose ps
docker inspect clipwave-ai-shorts_clipwave-ai_1
```

## 🚀 **Production Deployment**

### **For Production Servers:**

1. **Use a reverse proxy** (nginx/traefik):
```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - clipwave-ai
```

2. **Add SSL certificates** for HTTPS

3. **Set up monitoring** (Prometheus/Grafana)

4. **Configure backups** for the storage volume

### **Environment Variables for Production:**
```bash
# Production .env
OPENAI_API_KEY=your_production_openai_key
YOUTUBE_COOKIES_B64=your_production_cookies
NODE_ENV=production
LOG_LEVEL=info
```

## 📁 **File Structure**

```
clipwave-ai-shorts/
├── Dockerfile              # Main Docker configuration
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore          # Files to exclude from build
├── deploy.sh              # Automated deployment script
├── .env                   # Environment variables (create this)
├── backend/               # Python backend
│   ├── main.py           # FastAPI application
│   ├── video_processor.py # Video processing logic
│   └── requirements.txt   # Python dependencies
├── src/                   # React frontend
├── storage/               # Video storage (mounted volume)
└── dist/                  # Built frontend (generated)
```

## 🔒 **Security Considerations**

### **Container Security:**
- ✅ **Non-root user** in container
- ✅ **Minimal base image** (python:3.11-slim)
- ✅ **No sensitive data** in image layers
- ✅ **Environment variables** for secrets

### **Network Security:**
- ✅ **Internal networking** between services
- ✅ **Port exposure** only where needed
- ✅ **Health checks** for monitoring

### **Data Security:**
- ✅ **Volume mounting** for persistent data
- ✅ **Environment variables** for API keys
- ✅ **No secrets** in code repository

## 📈 **Performance Optimization**

### **Image Optimization:**
- ✅ **Multi-stage builds** for smaller images
- ✅ **Layer caching** for faster builds
- ✅ **Minimal dependencies** in final image

### **Runtime Optimization:**
- ✅ **Resource limits** in docker-compose.yml
- ✅ **Health checks** for automatic recovery
- ✅ **Volume mounting** for I/O performance

## 🎯 **Next Steps**

After successful deployment:

1. **Test the application** with a YouTube video
2. **Monitor performance** and logs
3. **Set up backups** for important data
4. **Configure monitoring** for production use
5. **Set up CI/CD** for automated deployments

## ✅ **Success Indicators**

Your deployment is successful when:

- ✅ **Health check passes**: `curl http://localhost:8000/health`
- ✅ **Frontend loads**: Browser shows the application
- ✅ **Video processing works**: Can upload and process YouTube videos
- ✅ **Job queue functions**: Real-time updates via WebSocket
- ✅ **Video player works**: Can switch between different processed videos

## 🆘 **Support**

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify environment**: Ensure `.env` file is correct
3. **Check prerequisites**: Docker and Docker Compose versions
4. **Review troubleshooting**: See common issues above

---

**🎉 Congratulations! Your ClipWave AI Shorts application is now running with Docker!** 