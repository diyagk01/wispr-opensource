This project is a complete macOS voice transcription system built around OpenAI Whisper for ASR and DeepSeek V3 (via Novita AI) for post-processing. Whisper handles the raw speech-to-text conversion, while DeepSeek cleans the output — adding punctuation, fixing grammar, and stripping filler words.

It has two entry points. The first is a Next.js + Tailwind web interface with a glass-morphism design. You can record directly from the browser using navigator.mediaDevices.getUserMedia(), stream audio to the backend, and get a live dual output: raw Whisper text and DeepSeek-polished text. Transcriptions are timestamped and persisted so you can review them later.

The second is a system-wide hotkey integration written in Python using pynput for keyboard hooks, pyaudio for recording, and pyperclip for clipboard management. Pressing Cmd+Shift+V anywhere on macOS starts recording; releasing the keys stops recording, sends the audio to the backend for Whisper + DeepSeek processing, and pastes the cleaned result into the active application.

The backend is a Flask API exposing endpoints for transcription (POST /transcribe), history retrieval (GET /transcriptions), and storage (POST /store-transcription). Whisper runs locally — you can swap between "tiny", "base", "small", "medium", and "large" models depending on accuracy and performance needs — and DeepSeek calls are made through Novita’s GPT-OSS endpoints with your API key.

Setup is minimal:
Install ffmpeg via Homebrew (required by Whisper).
Create Python virtual environments for both backend and hotkey, pip install the requirements.
npm install for the Next.js frontend.
Grant microphone, accessibility, and input monitoring permissions in macOS Privacy & Security settings.

You can launch everything manually (three terminals: backend, frontend, hotkey) or with a start.sh script. Once running, you have low-latency, locally hosted Whisper inference paired with API-powered text cleanup, accessible either from a browser or via a single key combo anywhere on your system.
