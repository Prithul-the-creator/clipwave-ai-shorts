# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY postcss.config.js ./
COPY tailwind.config.ts ./
COPY eslint.config.js ./
COPY components.json ./
COPY index.html ./
COPY public/ ./public/
COPY src/ ./src/

# Install frontend dependencies and build
RUN npm ci --legacy-peer-deps
RUN npm run build

# Copy backend files
COPY backend/ ./backend/
COPY requirements-deploy.txt ./backend/

# Install Python dependencies with CPU-only PyTorch
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r backend/requirements-deploy.txt

# Create storage directory
RUN mkdir -p storage/videos

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000

# Start the application
CMD ["python", "backend/main.py"] 