# 🎤 System-wide Voice Assistant

Transform any text field into a voice-powered input using Whisper + DeepSeek V3!

## ✨ Features

- **🌍 Works Everywhere**: iMessage, Slack, Email, any text field
- **🎯 Cmd+Shift+V Activation**: Press and hold Cmd+Shift+V to record
- **🧠 Dual Processing**: Raw Whisper + Cleaned DeepSeek text
- **⚡ Instant Insertion**: Text appears in focused field automatically
- **🔒 Privacy First**: All processing done locally + your API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd system-integration
chmod +x install.sh
./install.sh
```

### 2. Grant Permissions
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. Click **Accessibility** in sidebar
3. Click 🔒 to unlock
4. Add **Terminal** (or your Python app)
5. ✅ Check the box

### 3. Start Voice Assistant
```bash
python3 voice_assistant.py
```

### 4. Use Anywhere!
1. **Click any text field** (iMessage, Slack, etc.)
2. **Press and hold Cmd+Shift+V** keys
3. **Speak** your message
4. **Release** to transcribe
5. **Review and send** the cleaned text!

## 📱 iMessage Integration

Perfect for iMessage:
1. Open iMessage
2. Click in message box
3. Hold Cmd+Shift+V → Speak → Release
4. Cleaned text appears ready to send!

## ⚙️ How It Works

```
F13 Press → Record Audio → Send to Backend → Whisper + DeepSeek → Insert Text
     ↓              ↓              ↓                ↓              ↓
 Start Mic    Save to File   HTTP Request    Raw + Cleaned   Paste to Field
```

## 🔧 Customization

### Change Hotkey
Edit `voice_assistant.py` line 132:
```python
if key == Key.f13:  # Change to your preferred key
```

### Backend URL
Edit line 20:
```python
self.backend_url = "http://localhost:5001/transcribe"
```

## 🏗️ Advanced Setup

### Make it a Background Service
Create a launch daemon to start automatically:

1. **Create service file**:
```bash
sudo nano /Library/LaunchDaemons/com.voice.assistant.plist
```

2. **Add configuration**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.assistant</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/voice_assistant.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

3. **Load service**:
```bash
sudo launchctl load /Library/LaunchDaemons/com.voice.assistant.plist
```

## 🔍 Troubleshooting

### "Permission Denied"
- Grant Accessibility permissions in System Preferences

### "Backend Connection Failed"
- Make sure your Whisper+DeepSeek backend is running on port 5001

### "No Audio Recorded"
- Check microphone permissions
- Try a different hotkey

### "Text Not Inserting"
- Ensure accessibility permissions are granted
- Try clicking in the text field first

## 🎯 Pro Tips

- **Works in any app**: Try it in Slack, Discord, email, notes
- **Review before sending**: Text is inserted but not sent automatically
- **Multiple languages**: Whisper auto-detects language
- **Background usage**: Runs silently in background

## 📋 System Requirements

- **macOS 10.14+**
- **Python 3.7+**
- **Microphone access**
- **Accessibility permissions**
- **Whisper+DeepSeek backend running**

---

🎉 **Now you can voice-type into any app on your Mac!** 