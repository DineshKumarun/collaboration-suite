"""Test which import is causing the hang"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports one by one...")

print("1. Importing video_conferencing...")
from src.video_conferencing import VideoCapture, VideoStreamer
print("   ✅ video_conferencing imported")

print("2. Importing text_chat...")
from src.text_chat import ChatManager, MessageHandler
print("   ✅ text_chat imported")

print("3. Importing screen_sharing...")
from src.screen_sharing import ScreenCapture, ScreenStreamer
print("   ✅ screen_sharing imported")

print("4. Importing file_sharing...")
from src.file_sharing import FileTransfer
print("   ✅ file_sharing imported")

print("5. Importing audio_conferencing (this might hang)...")
from src.audio_conferencing import AudioCapture, AudioPlayback, AudioStreamer
print("   ✅ audio_conferencing imported")

print("\n✅ All imports successful!")
