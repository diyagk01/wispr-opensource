#!/bin/bash

echo "🎤 Installing System-wide Voice Assistant..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This system integration is designed for macOS"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install pyaudio requests pynput pyperclip

# Install PortAudio (required for PyAudio)
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "🔧 Installing PortAudio..."
brew install portaudio

echo "🔑 Setting up accessibility permissions..."
echo "⚠️  IMPORTANT: You need to grant accessibility permissions to Terminal/Python"
echo "   1. Go to System Preferences → Security & Privacy → Privacy"
echo "   2. Click on 'Accessibility' in the left sidebar"
echo "   3. Click the lock to make changes"
echo "   4. Add Terminal (or the app you're running this from)"
echo "   5. Check the box next to it"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To run the voice assistant:"
echo "   python3 voice_assistant.py"
echo ""
echo "📱 Usage:"
echo "   • Press and hold Cmd+Shift+V to record"
echo "   • Release to transcribe and insert into any text field"
echo "   • Works with iMessage, Slack, email, anywhere!" 