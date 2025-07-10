#!/bin/bash

# Start script for Wispr Voice Interface
echo "🎤 Starting Wispr Voice Interface with Whisper..."

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found. Please run setup first."
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping services..."
    jobs -p | xargs -r kill
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend && chmod +x start.sh && ./start.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Go back to root directory
cd ..

# Start frontend
echo "⚛️  Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for background processes
wait 