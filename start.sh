#!/bin/bash

# Script to start both backend and frontend servers

echo "Starting Ethiopian Weather Dashboard..."

# Start backend server in the background
echo "Starting backend server..."
cd backend
python api.py &

# Start frontend server
echo "Starting frontend server..."
cd ../frontend
npm run dev

# Kill backend server when frontend is stopped
trap "kill %1" EXIT