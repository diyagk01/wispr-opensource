from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os
import logging
import requests
import json
import datetime
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Shared transcription storage (in-memory for simplicity)
transcriptions_storage = []
storage_lock = threading.Lock()

def store_transcription(raw_text, cleaned_text, source="web"):
    """Store a transcription in shared storage"""
    with storage_lock:
        transcription = {
            'id': str(len(transcriptions_storage) + 1),
            'timestamp': datetime.datetime.now().strftime('%I:%M %p'),
            'rawText': raw_text,
            'cleanedText': cleaned_text,
            'source': source,
            'created_at': datetime.datetime.now().isoformat()
        }
        transcriptions_storage.insert(0, transcription)  # Add to beginning
        # Keep only last 50 transcriptions
        if len(transcriptions_storage) > 50:
            transcriptions_storage.pop()
        return transcription

# Initialize Whisper model (using 'small' for better accuracy and reasonable speed)
# Options: tiny (fastest), base (balanced), small, medium, large (most accurate)
print("Loading Whisper model...")
model = whisper.load_model("small")
print("Whisper model loaded successfully!")

# Novita API configuration for DeepSeek V3
NOVITA_API_KEY = "sk_2pX7-h3PlLnBnXHseAoLJT6T3_bHX1Fz2kfl-b0UBX0"
NOVITA_API_URL = "https://api.novita.ai/v3/openai/chat/completions"

def cleanup_text_with_deepseek(raw_text):
    """Clean up transcription using DeepSeek V3 via Novita"""
    try:
        headers = {
            "Authorization": f"Bearer {NOVITA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Clean up this speech transcription by removing filler words, adding proper punctuation, fixing grammar, and making it flow naturally. 

Raw transcription: {raw_text}

Return ONLY the cleaned text with no prefixes, quotes, or explanations. Do not add "Here's the cleaned-up transcription:" or any other introductory text."""

        data = {
            "model": "deepseek/deepseek-v3-0324",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that cleans up speech transcriptions."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "response_format": { "type": "text" }
        }
        
        response = requests.post(NOVITA_API_URL, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            cleaned_text = result["choices"][0]["message"]["content"].strip()
            
            # Remove any unwanted prefixes or formatting that might slip through
            unwanted_prefixes = [
                "Here's the cleaned-up transcription:",
                "Here is the cleaned-up transcription:",
                "Cleaned transcription:",
                "Here's the cleaned text:",
                "Here is the cleaned text:",
                "The cleaned text is:",
                "Cleaned text:"
            ]
            
            for prefix in unwanted_prefixes:
                if cleaned_text.startswith(prefix):
                    cleaned_text = cleaned_text[len(prefix):].strip()
            
            # Remove surrounding quotes if present
            if (cleaned_text.startswith('"') and cleaned_text.endswith('"')) or \
               (cleaned_text.startswith("'") and cleaned_text.endswith("'")):
                cleaned_text = cleaned_text[1:-1].strip()
            
            return cleaned_text
        else:
            print(f"Novita API error: {response.status_code} - {response.text}")
            return raw_text  # Return original if cleanup fails
            
    except Exception as e:
        print(f"Error with Novita/DeepSeek cleanup: {str(e)}")
        return raw_text  # Return original if cleanup fails

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        # Check if audio file is present in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Transcribe audio using Whisper with optimized settings for speed
            print(f"Transcribing audio file: {temp_filename}")
            result = model.transcribe(
                temp_filename,
                fp16=False,  # Use float32 for better compatibility
                language="en",  # Force English language
                task="transcribe",
                verbose=False,  # Reduce logging overhead
                condition_on_previous_text=True,  # Use previous text for better context/accuracy
                temperature=0.2  # Slightly higher for robustness
                # Removed compression_ratio_threshold, logprob_threshold, no_speech_threshold for better accuracy
            )
            
            # Extract raw text from Whisper
            raw_text = result["text"].strip()
            print(f"Raw Whisper transcription: {raw_text}")
            
            # Clean up text using DeepSeek V3
            print("Cleaning up transcription with DeepSeek V3...")
            cleaned_text = cleanup_text_with_deepseek(raw_text)
            print(f"Cleaned transcription: {cleaned_text}")
            
            # Store transcription in shared storage
            stored_transcription = store_transcription(raw_text, cleaned_text, "web")
            
            return jsonify({
                'success': True,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'language': result.get("language", "unknown"),
                'transcription': stored_transcription
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'whisper_loaded': model is not None})

@app.route('/transcriptions', methods=['GET'])
def get_transcriptions():
    """Get all stored transcriptions"""
    try:
        with storage_lock:
            return jsonify({
                'success': True,
                'transcriptions': transcriptions_storage.copy()
            })
    except Exception as e:
        print(f"Error getting transcriptions: {str(e)}")
        return jsonify({'error': f'Failed to get transcriptions: {str(e)}'}), 500

@app.route('/store-transcription', methods=['POST'])
def store_voice_assistant_transcription():
    """Store a transcription from the voice assistant"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        raw_text = data.get('raw_text', '')
        cleaned_text = data.get('cleaned_text', '')
        
        if not raw_text and not cleaned_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Store transcription
        stored_transcription = store_transcription(raw_text, cleaned_text, "voice_assistant")
        
        return jsonify({
            'success': True,
            'transcription': stored_transcription
        })
        
    except Exception as e:
        print(f"Error storing voice assistant transcription: {str(e)}")
        return jsonify({'error': f'Failed to store transcription: {str(e)}'}), 500

@app.route('/clear-history', methods=['POST'])
def clear_transcription_history():
    """Clear all stored transcriptions"""
    try:
        with storage_lock:
            transcriptions_storage.clear()
            print("🗑️ Transcription history cleared")
        
        return jsonify({
            'success': True,
            'message': 'Transcription history cleared successfully'
        })
        
    except Exception as e:
        print(f"Error clearing transcription history: {str(e)}")
        return jsonify({'error': f'Failed to clear history: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 