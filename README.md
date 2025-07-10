# 🎤 Voice Transcription System
**AI-Powered Speech-to-Text with OpenAI Whisper + DeepSeek V3**

A complete voice transcription system featuring web interface, global system hotkey, and beautiful glass morphism UI.

---

## ✨ Features

### 🌐 **Web Interface**
- **Beautiful glass morphism design** with space background
- **Real-time recording** directly in browser
- **Live transcription history** with timestamps
- **Dual display**: Raw Whisper + DeepSeek cleaned text
- **Source tracking**: Web vs System hotkey transcriptions

### ⌨️ **Global Hotkey (Cmd+Shift+V)**
- **System-wide functionality** - works in any Mac app
- **Press and hold** to record, **release** to transcribe
- **Auto-paste** cleaned text into focused text field
- **Perfect for iMessage, Notes, any text input**

### 🤖 **AI Processing**
- **OpenAI Whisper** for accurate speech recognition
- **DeepSeek V3** for intelligent text cleanup
- **Removes filler words** (um, uh, like, etc.)
- **Adds proper punctuation** and capitalization
- **Fixes grammar** and improves flow

---

## 🚀 System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Flask Backend  │    │ Voice Assistant │
│   (Port 3000)   │◄──►│   (Port 5001)    │◄──►│ (Cmd+Shift+V)  │
│   Next.js UI    │    │ Whisper+DeepSeek │    │  Global Hotkey  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📋 Prerequisites

### **Required Software**
- **macOS** (for global hotkey functionality)
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Homebrew** (for ffmpeg)

### **API Requirements**
- **Novita API Key**: Your DeepSeek V3 key (`sk_2pX7-h3PlLnBnXHseAoLJT6T3_bHX1Fz2kfl-b0UBX0`)

---

## 🛠️ Installation & Setup

### **1. Install System Dependencies**
```bash
# Install ffmpeg (required for audio processing)
brew install ffmpeg

# Install Python dependencies
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Setup Voice Assistant Environment**
```bash
cd system-integration
python3 -m venv voice_env
source voice_env/bin/activate
pip install pyaudio requests pynput pyperclip
```

### **3. Install Frontend Dependencies**
```bash
cd /path/to/Wispr-Novita
npm install
```

### **4. Configure macOS Permissions**
**Required for global hotkey functionality:**

1. **System Preferences → Security & Privacy → Privacy**
2. **Accessibility**: Add Terminal and Python
3. **Microphone**: Allow browser and Terminal access
4. **Input Monitoring**: Add Terminal and Python

---

## 🚀 Starting the System

### **Option 1: Start All Components (Recommended)**

```bash
# Terminal 1: Backend (Flask + Whisper + DeepSeek)
cd backend
source venv/bin/activate
python app.py

# Terminal 2: Frontend (Next.js Web Interface)  
cd /path/to/Wispr-Novita
npm run dev

# Terminal 3: Voice Assistant (Global Hotkey)
cd system-integration
source voice_env/bin/activate
python voice_assistant.py
```

### **Option 2: Quick Start Script**

Create a `start.sh` file:
```bash
#!/bin/bash
cd /Users/diyagirishkumar/Wispr-Novita

# Start backend
cd backend && source venv/bin/activate && python app.py &

# Start frontend
npm run dev &

# Start voice assistant
cd system-integration && source voice_env/bin/activate && python voice_assistant.py &

echo "🚀 Voice Transcription System started!"
echo "🌐 Web Interface: http://localhost:3000"
echo "⌨️ Global Hotkey: Cmd+Shift+V"
```

---

## 🎯 Usage

### **Web Interface**
1. **Open**: http://localhost:3000
2. **Click** the microphone button to record
3. **Speak** your message
4. **Click** again to stop and process
5. **View** both raw and cleaned transcriptions

### **Global Hotkey**
1. **Navigate** to any text field (iMessage, Notes, etc.)
2. **Press and hold** `Cmd+Shift+V`
3. **Speak** your message
4. **Release** keys to transcribe and auto-paste

---

## 🔧 System Components

### **Backend (`backend/app.py`)**
- **Port**: 5001
- **Whisper Model**: `base` (can be upgraded to `large`)
- **API**: Novita.ai for DeepSeek V3
- **Endpoints**:
  - `POST /transcribe` - Process audio
  - `GET /transcriptions` - Fetch history
  - `POST /store-transcription` - Store new transcription

### **Frontend (`app/page.tsx`)**
- **Port**: 3000
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS + Glass Morphism
- **Features**: Real-time recording, transcription display

### **Voice Assistant (`system-integration/voice_assistant.py`)**
- **Hotkey**: Cmd+Shift+V
- **Libraries**: pynput, pyperclip, pyaudio
- **Features**: Global recording, auto-paste, clipboard management

---

## 🛠️ Troubleshooting

### **Port Already in Use**
```bash
# Kill processes on ports 3000 and 5001
lsof -ti :3000 :5001 | xargs kill -9
```

### **Microphone Not Working**
1. Check **System Preferences → Security & Privacy → Microphone**
2. Allow access for **Terminal** and **Google Chrome**
3. Restart the applications

### **Global Hotkey Not Working**
1. Check **System Preferences → Security & Privacy → Privacy → Accessibility**
2. Add **Terminal** and **Python** to allowed apps
3. Restart `voice_assistant.py`

### **Whisper Model Issues**
```bash
# Force reinstall Whisper
pip uninstall openai-whisper
pip install openai-whisper
```

### **DeepSeek API Timeout**
- Check your Novita API key in `backend/app.py`
- Verify internet connection
- API has 30-second timeout (configurable)

---

## 📁 Project Structure

```
Wispr-Novita/
├── backend/
│   ├── venv/                  # Python virtual environment
│   ├── app.py                 # Flask server + Whisper + DeepSeek
│   └── requirements.txt       # Python dependencies
├── system-integration/
│   ├── voice_env/            # Voice assistant environment
│   └── voice_assistant.py    # Global hotkey functionality
├── app/
│   ├── page.tsx              # Main web interface
│   ├── layout.tsx            # Next.js layout
│   └── globals.css           # Global styles + Tailwind
├── tailwind.config.js        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── package.json              # Node.js dependencies
└── README.md                 # This documentation
```

---

## ⚙️ Configuration

### **API Key Configuration**
Update your DeepSeek API key in `backend/app.py`:
```python
headers = {
    "Authorization": "Bearer sk_YOUR_NEW_API_KEY_HERE",
    "Content-Type": "application/json"
}
```

### **Whisper Model Selection**
Change model size in `backend/app.py`:
```python
# Options: tiny, base, small, medium, large
model = whisper.load_model("large")  # For better accuracy
```

### **Hotkey Customization**
Modify hotkey combination in `system-integration/voice_assistant.py`:
```python
# Current: Cmd+Shift+V
# Change to: Cmd+Option+V
hotkey = '<cmd>+<alt>+v'
```

---

## 🔍 Monitoring & Logs

### **Check System Status**
```bash
# Check all running processes
ps aux | grep -E "(python.*app\.py|python.*voice_assistant\.py|node.*next)" | grep -v grep

# Check port usage
lsof -i :3000 -i :5001
```

### **View Logs**
- **Backend**: Terminal output shows Whisper processing and API calls
- **Frontend**: Browser developer console for client-side issues
- **Voice Assistant**: Terminal output shows recording events and errors

---

## 🎨 Customization

### **UI Themes**
Modify the glass morphism design in `app/globals.css` and `app/page.tsx`.

### **Audio Settings**
Adjust recording quality in `app/page.tsx`:
```javascript
const stream = await navigator.mediaDevices.getUserMedia({ 
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    sampleRate: 44100  // Increase for better quality
  } 
})
```

---

## 📞 Support

### **Common Issues**
1. **"Address already in use"** → Kill existing processes
2. **"Microphone access denied"** → Check macOS permissions
3. **"osascript not allowed"** → Enable Accessibility permissions
4. **Poor transcription quality** → Upgrade to Whisper `large` model

### **Performance Tips**
- Use **wired internet** for DeepSeek API calls
- **Upgrade Whisper model** for better accuracy
- **Close other audio applications** during recording

---

## 🚀 Ready to Use!

Your complete voice transcription system is now ready:

1. ✅ **Backend**: OpenAI Whisper + DeepSeek V3 processing
2. ✅ **Frontend**: Beautiful glass morphism web interface  
3. ✅ **Global Hotkey**: System-wide Cmd+Shift+V functionality
4. ✅ **Shared History**: All transcriptions unified across interfaces

**Web Interface**: http://localhost:3000  
**Global Hotkey**: `Cmd+Shift+V` anywhere in macOS

*Enjoy your AI-powered voice transcription system! 🎤✨* 