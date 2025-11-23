# Multi-stage build for Chameleon Cybersecurity ML
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python Backend with Frontend
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY Backend/requirements.txt ./Backend/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Backend/requirements.txt

# Copy backend code
COPY Backend/ ./Backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./Backend/static

# Expose port
EXPOSE $PORT

# Start command - serve both frontend and backend
CMD cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
