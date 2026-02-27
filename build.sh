#!/bin/bash

echo "🏗️  Building Chameleon System..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install --upgrade pip
pip install -r Backend/requirements.txt

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🎨 Building frontend..."
npm run build

echo "✅ Build complete!"
