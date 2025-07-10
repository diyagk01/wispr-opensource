#!/usr/bin/env python3
"""
Setup script for Whisper backend
"""
import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements in a virtual environment"""
    venv_path = "venv"
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_path):
        print("Creating Python virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    print("Installing Python dependencies in virtual environment...")
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ ffmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ffmpeg is not installed")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt update && sudo apt install ffmpeg")
        print("  Windows: choco install ffmpeg")
        return False

if __name__ == "__main__":
    print("Setting up Whisper backend...")
    
    if not check_ffmpeg():
        print("Please install ffmpeg first, then run this script again.")
        sys.exit(1)
    
    install_requirements()
    print("Setup complete!")
    print("\nTo start the backend:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print("  python3 app.py") 