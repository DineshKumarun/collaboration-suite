import pyaudio
import numpy as np
import threading
import queue
from typing import Optional
from contextlib import contextmanager
import sys
import os

# Suppress ALSA warnings
@contextmanager
def suppress_stdout_stderr():
    """Suppress stdout and stderr"""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class AudioCapture:
    """Handles microphone audio capture with threading"""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 2048):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        # Initialize PyAudio with suppressed warnings
        with suppress_stdout_stderr():
            self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.audio_queue = queue.Queue(maxsize=10)
        self.thread = None
        
    def start(self) -> bool:
        """Start audio capture"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.running = True
            self.stream.start_stream()
            return True
            
        except Exception as e:
            print(f"Error starting audio capture: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.running:
            try:
                self.audio_queue.put_nowait(in_data)
            except queue.Full:
                pass
        return (None, pyaudio.paContinue)
    
    def read(self) -> Optional[bytes]:
        """Get audio chunk from queue"""
        try:
            return self.audio_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop audio capture and cleanup"""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        self.audio.terminate()


class AudioPlayback:
    """Handles audio playback"""
    
    def __init__(self, sample_rate: int = 44100, channels: int = 1, chunk_size: int = 2048):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        
        # Initialize PyAudio with suppressed warnings
        with suppress_stdout_stderr():
            self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        
    def start(self) -> bool:
        """Start audio playback"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"Error starting audio playback: {e}")
            return False
    
    def play(self, audio_data: bytes):
        """Play audio chunk"""
        if self.running and self.stream:
            try:
                self.stream.write(audio_data)
            except Exception as e:
                print(f"Error playing audio: {e}")
    
    def stop(self):
        """Stop playback and cleanup"""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        self.audio.terminate()