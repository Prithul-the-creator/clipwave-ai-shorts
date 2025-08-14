# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy package files for frontend
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.ts ./
COPY postcss.config.js ./
COPY components.json ./
COPY eslint.config.js ./

# Install frontend dependencies with legacy peer deps to resolve conflicts
RUN npm ci --legacy-peer-deps

# Copy frontend source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Build frontend
RUN npm run build

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Create storage directory
RUN mkdir -p storage/videos

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Start the application
CMD ["python", "backend/main.py"] 