#!/bin/bash

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping OSM Agentic AI services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Activate the single virtual environment at the project root
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting FastAPI Backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Streamlit UI..."
streamlit run ui/app.py --server.port 8501 &
FRONTEND_PID=$!

echo "========================================="
echo "OSM Agentic AI is up and running!"
echo "Backend/API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Frontend:    http://localhost:8501"
echo "Press Ctrl+C to stop both services."
echo "========================================="

# Wait indefinitely until interrupted
wait
