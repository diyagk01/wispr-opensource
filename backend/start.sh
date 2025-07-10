#!/bin/bash

# Activate virtual environment and start the backend
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run 'python3 setup.py' first."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Whisper backend..."
python3 app.py 