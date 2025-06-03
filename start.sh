#!/bin/bash

echo "🚀 Starting Dynamic Pricing System..."
echo

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Virtual environment not found. Running setup..."
    python3 setup.py
    echo
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting backend server..."
    cd backend
    source venv/bin/activate
    python app.py
}

# Function to start frontend
start_frontend() {
    echo "⚛️  Starting frontend server..."
    cd frontend
    npm start
}

# Start backend in background
start_backend &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend in background
start_frontend &
FRONTEND_PID=$!

echo
echo "🌐 Both servers are starting..."
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo
echo "📋 To stop the servers, press Ctrl+C"
echo

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 