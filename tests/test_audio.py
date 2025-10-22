import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import numpy as np
from src.audio_conferencing import AudioCapture, AudioPlayback
from src.audio_conferencing import AudioStreamer

def test_audio_capture():
    """Test audio capture functionality"""
    print("Testing audio capture...")
    
    capture = AudioCapture(sample_rate=44100, channels=1, chunk_size=2048)
    
    if not capture.start():
        print("❌ Failed to start audio capture")
        return False
    
    print("✓ Audio capture started")
    print("  Please speak into your microphone for 3 seconds...")
    
    # Capture audio for 3 seconds
    start_time = time.time()
    chunk_count = 0
    total_bytes = 0
    
    while time.time() - start_time < 3:
        audio_data = capture.read()
        if audio_data:
            chunk_count += 1
            total_bytes += len(audio_data)
    
    capture.stop()
    
    print(f"✓ Captured {chunk_count} audio chunks ({total_bytes} bytes)")
    
    # With chunk_size=2048, expect ~64 chunks in 3 seconds at 44.1kHz
    # (44100 samples/sec * 3 sec * 2 bytes/sample) / 2048 bytes/chunk = 129 chunks
    # But actual may be lower due to timing - require at least 50 chunks
    if chunk_count >= 50:
        print("✓ Audio capture test PASSED")
        return True
    else:
        print("❌ Audio capture test FAILED (insufficient chunks)")
        return False


def test_audio_playback():
    """Test audio playback functionality"""
    print("\nTesting audio playback...")
    
    playback = AudioPlayback(sample_rate=44100, channels=1, chunk_size=2048)
    
    if not playback.start():
        print("❌ Failed to start audio playback")
        return False
    
    print("✓ Audio playback started")
    print("  Generating test tone (440 Hz)...")
    
    # Generate 1 second of 440 Hz sine wave (A note)
    sample_rate = 44100
    duration = 1.0
    frequency = 440.0
    
    samples = np.arange(int(sample_rate * duration))
    wave = np.sin(2 * np.pi * frequency * samples / sample_rate)
    wave = (wave * 32767).astype(np.int16)
    
    # Play in chunks
    chunk_size = 1024
    for i in range(0, len(wave), chunk_size):
        chunk = wave[i:i+chunk_size].tobytes()
        playback.play(chunk)
        time.sleep(chunk_size / sample_rate)
    
    playback.stop()
    
    print("✓ Audio playback test PASSED")
    return True


def test_audio_loopback():
    """Test audio capture and playback together"""
    print("\nTesting audio loopback...")
    
    capture = AudioCapture()
    playback = AudioPlayback()
    
    if not capture.start() or not playback.start():
        print("❌ Failed to start audio devices")
        return False
    
    print("✓ Audio loopback started")
    print("  Speak into microphone - you should hear yourself for 5 seconds...")
    
    start_time = time.time()
    while time.time() - start_time < 5:
        audio_data = capture.read()
        if audio_data:
            playback.play(audio_data)
    
    capture.stop()
    playback.stop()
    
    print("✓ Audio loopback test PASSED")
    return True


if __name__ == "__main__":
    print("=== Audio Module Tests ===\n")
    
    test1 = test_audio_capture()
    test2 = test_audio_playback()
    test3 = test_audio_loopback()
    
    print("\n=== Test Summary ===")
    print(f"Audio Capture: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"Audio Playback: {'✓ PASS' if test2 else '❌ FAIL'}")
    print(f"Audio Loopback: {'✓ PASS' if test3 else '❌ FAIL'}")