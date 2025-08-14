# 🐳 **Docker Installation Guide for macOS**

## 📋 **Prerequisites**

Before installing Docker, make sure you have:
- macOS 10.15 (Catalina) or newer
- At least 4GB of RAM
- Administrator privileges

## 🚀 **Installation Methods**

### **Method 1: Docker Desktop (Recommended)**

1. **Download Docker Desktop:**
   - Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Click "Download for Mac"
   - Choose the appropriate version:
     - **Apple Silicon (M1/M2)**: Download the Apple Silicon version
     - **Intel Mac**: Download the Intel version

2. **Install Docker Desktop:**
   - Open the downloaded `.dmg` file
   - Drag Docker to your Applications folder
   - Open Docker from Applications
   - Follow the installation wizard

3. **Verify Installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

### **Method 2: Homebrew (Alternative)**

If you prefer using Homebrew:

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop via Homebrew
brew install --cask docker
```

### **Method 3: Command Line Tools Only**

For advanced users who want only the command-line tools:

```bash
# Install Docker CLI via Homebrew
brew install docker docker-compose

# Note: This method requires additional setup for the Docker daemon
```

## ⚙️ **Post-Installation Setup**

### **1. Start Docker Desktop**
- Open Docker Desktop from Applications
- Wait for Docker to start (you'll see the whale icon in the menu bar)
- Docker Desktop will ask for permissions - grant them

### **2. Verify Everything Works**
```bash
# Test Docker installation
docker run hello-world

# Test Docker Compose
docker-compose --version
```

### **3. Configure Resources (Optional)**
- Open Docker Desktop
- Go to Settings → Resources
- Adjust memory, CPU, and disk space as needed
- Recommended: At least 4GB RAM for video processing

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. "Docker Desktop is starting..."**
- Wait a few minutes for Docker to fully start
- Check if Docker Desktop is running in Applications
- Restart Docker Desktop if needed

#### **2. Permission Denied**
```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in, or restart your computer
```

#### **3. Port Conflicts**
- Docker Desktop uses port 2375 by default
- If you have conflicts, change the port in Docker Desktop settings

#### **4. Apple Silicon Issues**
- Make sure you downloaded the Apple Silicon version
- Some images might need to be built for ARM64 architecture

### **Useful Commands:**
```bash
# Check Docker status
docker info

# List running containers
docker ps

# Check Docker Desktop status
docker system info

# Reset Docker Desktop (if having issues)
# Docker Desktop → Troubleshoot → Reset to factory defaults
```

## 🎯 **Next Steps**

Once Docker is installed and running:

1. **Verify installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Test with a simple container:**
   ```bash
   docker run hello-world
   ```

3. **Proceed with ClipWave AI deployment:**
   ```bash
   # Make sure you're in the project directory
   cd /path/to/clipwave-ai-shorts
   
   # Run the deployment script
   ./deploy.sh
   ```

## 📚 **Additional Resources**

- **Docker Documentation**: [https://docs.docker.com/](https://docs.docker.com/)
- **Docker Desktop for Mac**: [https://docs.docker.com/desktop/mac/](https://docs.docker.com/desktop/mac/)
- **Docker Compose**: [https://docs.docker.com/compose/](https://docs.docker.com/compose/)

## ✅ **Success Indicators**

Docker is properly installed when:

- ✅ `docker --version` shows a version number
- ✅ `docker-compose --version` shows a version number
- ✅ `docker run hello-world` runs successfully
- ✅ Docker Desktop shows "Docker Desktop is running" in the menu bar

---

**🎉 Once Docker is installed, you can proceed with deploying ClipWave AI Shorts!** 