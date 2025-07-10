#!/usr/bin/env python3
"""
System-wide Voice Assistant for macOS
Listens for fn key press, records audio, transcribes with Whisper + DeepSeek,
and injects cleaned text into any focused text field (iMessage, etc.)
"""

import pyaudio
import wave
import requests
import tempfile
import os
import threading
import time
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key
import subprocess
import uuid

class VoiceAssistant:
    def __init__(self):
        self.is_recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.pyaudio_instance = None
        self.backend_url = "http://localhost:5001/transcribe"
        self.current_session_id = None
        self.transcription_ready = False
        
        # Audio settings optimized for speed
        self.CHUNK = 512  # Smaller chunks for faster processing
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 8000  # Lower sample rate for faster processing
        
        print("🎤 Voice Assistant started!")
        print("Press and hold Cmd+Shift+V to record, release to transcribe")
        print("Text will be inserted into any focused text field")
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return
            
        try:
            self.is_recording = True
            self.audio_frames = []
            self.transcription_ready = False
            self.current_session_id = str(uuid.uuid4())
            
            # Store the current clipboard content to restore later if needed
            self.original_clipboard = pyperclip.paste()
            
            # Clear clipboard to prevent pasting old content
            print("🧹 Clearing clipboard...")
            pyperclip.copy("")
            
            # Initialize PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Start recording stream
            self.audio_stream = self.pyaudio_instance.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("🔴 Recording... (release keys to stop)")
            
            # Record in a separate thread
            self.record_thread = threading.Thread(target=self._record_audio)
            self.record_thread.start()
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
    
    def _record_audio(self):
        """Record audio frames"""
        while self.is_recording:
            try:
                data = self.audio_stream.read(self.CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and process transcription"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        session_id = self.current_session_id
        print("⏹️ Recording stopped, processing...")
        
        try:
            # Wait for recording thread to finish
            if hasattr(self, 'record_thread'):
                self.record_thread.join()
            
            # Clean up audio stream
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
            
            # Save audio to temporary file
            if self.audio_frames:
                temp_file = self._save_audio_to_file()
                if temp_file:
                    # Send to backend for transcription
                    self._transcribe_and_insert(temp_file, session_id)
                    # Clean up temp file
                    os.unlink(temp_file)
            else:
                print("No audio recorded")
                # Restore original clipboard content
                if hasattr(self, 'original_clipboard'):
                    pyperclip.copy(self.original_clipboard)
                    print("📋 Restored original clipboard content")
                
        except Exception as e:
            print(f"Error stopping recording: {e}")
            # Restore original clipboard content on error
            if hasattr(self, 'original_clipboard'):
                pyperclip.copy(self.original_clipboard)
                print("📋 Restored original clipboard content on error")
    
    def _save_audio_to_file(self):
        """Save recorded audio frames to a temporary WAV file"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.audio_frames))
            
            return temp_file.name
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return None
    
    def _transcribe_and_insert(self, audio_file_path, session_id):
        """Send audio to backend and insert cleaned text"""
        try:
            print("🔄 Transcribing with Whisper + DeepSeek...")
            
            # Send audio to our backend
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                response = requests.post(self.backend_url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    cleaned_text = result.get('cleaned_text', '')
                    raw_text = result.get('raw_text', '')
                    
                    print(f"🎤 Raw: {raw_text}")
                    print(f"✨ Cleaned: {cleaned_text}")
                    
                    # Only proceed if this is still the current session
                    if session_id == self.current_session_id:
                        if cleaned_text:
                            # Store transcription in backend for web interface
                            self._store_in_backend(raw_text, cleaned_text)
                            
                            # Insert text into focused field
                            self._insert_text(cleaned_text, session_id)
                        else:
                            print("No text transcribed")
                            pyperclip.copy("")  # Clear placeholder
                    else:
                        print("🚫 Session outdated, skipping insertion")
                else:
                    print(f"Transcription failed: {result.get('error', 'Unknown error')}")
                    # Restore original clipboard content
                    if hasattr(self, 'original_clipboard'):
                        pyperclip.copy(self.original_clipboard)
                        print("📋 Restored original clipboard content")
            else:
                print(f"Backend error: {response.status_code}")
                # Restore original clipboard content
                if hasattr(self, 'original_clipboard'):
                    pyperclip.copy(self.original_clipboard)
                    print("📋 Restored original clipboard content")
                
        except Exception as e:
            print(f"Error during transcription: {e}")
            # Restore original clipboard content
            if hasattr(self, 'original_clipboard'):
                pyperclip.copy(self.original_clipboard)
                print("📋 Restored original clipboard content")
    
    def _store_in_backend(self, raw_text, cleaned_text):
        """Store transcription in backend for web interface"""
        try:
            store_url = "http://localhost:5001/store-transcription"
            data = {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text
            }
            response = requests.post(store_url, json=data, timeout=5)
            if response.status_code == 200:
                print("📱 Stored in web interface")
            else:
                print(f"Failed to store in web interface: {response.status_code}")
        except Exception as e:
            print(f"Error storing in backend: {e}")
    
    def _insert_text(self, text, session_id):
        """Insert text into the currently focused text field"""
        try:
            # Double-check this is still the current session
            if session_id != self.current_session_id:
                print("🚫 Session mismatch, aborting insertion")
                return
            
            if not text or text.strip() == "":
                print("⚠️ No text to insert")
                return
                
            print(f"🔄 Preparing to insert: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Copy the new text to clipboard
            pyperclip.copy(text)
            
            # Verify the clipboard contains our text before pasting
            max_retries = 3
            for attempt in range(max_retries):
                time.sleep(0.1)  # Wait for clipboard to update
                clipboard_content = pyperclip.paste()
                if clipboard_content == text:
                    print(f"✅ Clipboard verified: {text[:30]}{'...' if len(text) > 30 else ''}")
                    break
                else:
                    print(f"🔄 Clipboard mismatch (attempt {attempt + 1}/{max_retries}), retrying...")
                    pyperclip.copy(text)
            else:
                print("⚠️ Clipboard verification failed, pasting anyway...")
            
            # Final session check before pasting
            if session_id != self.current_session_id:
                print("🚫 Session changed during clipboard setup, aborting paste")
                return
            
            # Brief delay before pasting to ensure clipboard is ready
            time.sleep(0.2)
            
            # Try multiple methods to paste the text
            paste_success = False
            
            # Method 1: AppleScript with better error handling
            try:
                applescript = '''
                tell application "System Events"
                    keystroke "v" using command down
                end tell
                '''
                result = subprocess.run(['osascript', '-e', applescript], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    paste_success = True
                    print(f"✅ Inserted via AppleScript: {text}")
                else:
                    print(f"⚠️ AppleScript failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                print("⚠️ AppleScript timed out")
            except Exception as e:
                print(f"⚠️ AppleScript error: {e}")
            
            # Method 2: Alternative AppleScript approach
            if not paste_success:
                try:
                    applescript2 = '''
                    tell application "System Events"
                        tell process (name of first process whose frontmost is true)
                            keystroke "v" using command down
                        end tell
                    end tell
                    '''
                    result = subprocess.run(['osascript', '-e', applescript2], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        paste_success = True
                        print(f"✅ Inserted via AppleScript (method 2): {text}")
                    else:
                        print(f"⚠️ AppleScript method 2 failed: {result.stderr}")
                except Exception as e:
                    print(f"⚠️ AppleScript method 2 error: {e}")
            
            # Method 3: Fallback - just copy to clipboard with instructions
            if not paste_success:
                print(f"📋 Copied to clipboard (paste manually with Cmd+V): {text}")
                print("💡 To enable auto-paste, grant 'Input Monitoring' permission to Terminal in System Preferences")
            
        except Exception as e:
            print(f"Error inserting text: {e}")
            # Fallback: just copy to clipboard
            try:
                pyperclip.copy(text)
                print(f"📋 Copied to clipboard (paste manually with Cmd+V): {text}")
                print("💡 To enable auto-paste, grant 'Input Monitoring' permission to Terminal in System Preferences")
            except:
                print("Failed to copy to clipboard")

def main():
    assistant = VoiceAssistant()
    recording_active = False
    cmd_pressed = False
    shift_pressed = False
    v_pressed = False
    
    def check_combo():
        return cmd_pressed and shift_pressed and v_pressed
    
    def on_key_press(key):
        nonlocal recording_active, cmd_pressed, shift_pressed, v_pressed
        try:
            # Track modifier keys
            if key == Key.cmd or key == Key.cmd_l or key == Key.cmd_r:
                cmd_pressed = True
            elif key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                shift_pressed = True
            elif hasattr(key, 'char') and key.char and key.char.lower() == 'v':
                v_pressed = True
            
            # Start recording if combo is pressed and not already recording
            if check_combo() and not recording_active:
                recording_active = True
                assistant.start_recording()
                
        except AttributeError:
            pass
    
    def on_key_release(key):
        nonlocal recording_active, cmd_pressed, shift_pressed, v_pressed
        try:
            # Track modifier key releases
            if key == Key.cmd or key == Key.cmd_l or key == Key.cmd_r:
                cmd_pressed = False
            elif key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                shift_pressed = False
            elif hasattr(key, 'char') and key.char and key.char.lower() == 'v':
                v_pressed = False
            
            # Stop recording if any part of combo is released while recording
            if recording_active and not check_combo():
                recording_active = False
                assistant.stop_recording()
            
            # ESC to quit
            if key == Key.esc:
                print("Exiting...")
                return False
                
        except AttributeError:
            pass
    
    print("\n🚀 Voice Assistant Controls:")
    print("• Press and hold Cmd+Shift+V to record")
    print("• Release any key to transcribe and insert text")
    print("• Press ESC to quit")
    print("\nListening for hotkeys...\n")
    
    # Start keyboard listener
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

if __name__ == "__main__":
    main() 