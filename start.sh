#!/bin/bash

# --- EVE Startup Script ---
# This script cleans up old processes, sets up the environment,
# and starts both the backend and frontend services.

echo "🚀 Starting EVE: Your Everyday Virtual Executive"
echo "----------------------------------------------------"

# Function to kill processes on a given port
kill_process_on_port() {
  PORT=$1
  echo "🧹 Checking for process on port $PORT..."
  PID=$(lsof -ti:$PORT)
  
  if [ -n "$PID" ]; then
    echo "🔪 Terminating process $PID on port $PORT..."
    kill -9 $PID
    sleep 1
  else
    echo "✅ No process found on port $PORT."
  fi
}

# 1. Clean up existing processes
kill_process_on_port 8000 # Backend
kill_process_on_port 3000 # Frontend
echo ""

# 2. Check for .env file and API keys
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating one from env.example..."
    cp env.example .env
    echo "✅ Created .env file."
    echo "🛑 IMPORTANT: Please open the '.env' file and add your API keys."
    echo "   You need keys for OpenAI, ElevenLabs, and Gemini."
    echo "   After adding keys, please run './start.sh' again."
    exit 1
fi
echo "✅ .env file found."
echo ""

# 3. Set up and start Backend
echo "🛠️  Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo " activating virtual environment..."
source venv/bin/activate
echo "📦 Installing backend dependencies from requirements.txt..."
pip install -q -r requirements.txt
echo "✅ Backend setup complete."

echo " EVE backend server on http://localhost:8000"
./venv/bin/python run.py &
BACKEND_PID=$!
cd ..
sleep 3 # Give backend a moment to start

# 4. Health check for backend
echo ""
echo "🩺 Performing health check on backend..."
if curl -s "http://localhost:8000/health" | grep -q '"status":"healthy"'; then
  echo "✅ Backend is healthy and running!"
else
  echo "❌ Backend failed to start. Please check the logs."
  kill $BACKEND_PID
  exit 1
fi
echo ""


# 5. Set up and start Frontend
echo "🎨 Setting up Node.js frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies with npm..."
    npm install
fi
echo "✅ Frontend setup complete."

echo "🚀 Launching Next.js frontend on http://localhost:3000"
echo ""
echo "----------------------------------------------------"
echo "🎉 EVE is now running!"
echo "   Please open your browser to: http://localhost:3000"
echo "----------------------------------------------------"
echo "   To stop the application, press Ctrl+C in this terminal."
echo ""

# Trap Ctrl+C and kill the backend process
trap 'echo "
🛑 Shutting down EVE..."; kill $BACKEND_PID; exit 0' INT

npm run dev -- --port 3000

