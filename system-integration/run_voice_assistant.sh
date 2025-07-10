#!/bin/bash

# Wrapper script to run the voice assistant with virtual environment
cd "$(dirname "$0")"

if [ ! -d "voice_env" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

echo "🎤 Starting System-wide Voice Assistant..."
echo "🔧 Make sure your Whisper+DeepSeek backend is running on http://localhost:5001"
echo ""

# Activate virtual environment and run
source voice_env/bin/activate
python3 voice_assistant.py 