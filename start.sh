#!/bin/bash

echo "🚀 Starting EVE: The Everyday Virtual Executive"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from env.example..."
    cp env.example .env
    echo ""
    echo "✅ Created .env file"
    echo "⚠️  IMPORTANT: Edit .env and add your API keys before continuing!"
    echo ""
    echo "Required API keys:"
    echo "  - OPENAI_API_KEY (get from: https://platform.openai.com/api-keys)"
    echo "  - ELEVENLABS_API_KEY (get from: https://elevenlabs.io/)"
    echo "  - GEMINI_API_KEY (get from: https://aistudio.google.com/apikey)"
    echo ""
    echo "After adding your keys, run this script again."
    exit 1
fi

echo "📦 Setting up backend..."
cd backend

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install
source venv/bin/activate
pip install -q -r requirements.txt

echo "✅ Backend ready"
echo ""

# Start backend in background
echo "🔧 Starting FastAPI backend on port 8000..."
python main.py &
BACKEND_PID=$!

cd ..

echo "📦 Setting up frontend..."
cd frontend

# Install npm packages if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node packages..."
    npm install
fi

echo "✅ Frontend ready"
echo ""

# Start frontend
echo "🎨 Starting Next.js frontend on port 3000..."
echo ""
echo "=========================================="
echo "✅ EVE is running!"
echo "=========================================="
echo ""
echo "📱 Open your browser to: http://localhost:3000"
echo ""
echo "To stop EVE:"
echo "  Press Ctrl+C"
echo ""

npm run dev

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null

