import numpy as np
from typing import Optional

class AudioMixer:
    """Mixes multiple audio streams"""
    
    def __init__(self):
        self.streams = {}
        
    def add_stream(self, stream_id: str, audio_data: bytes):
        """Add audio data from a stream"""
        self.streams[stream_id] = audio_data
    
    def mix(self) -> Optional[bytes]:
        """Mix all audio streams"""
        if not self.streams:
            return None
        
        try:
            # Convert all streams to numpy arrays
            arrays = []
            for audio_data in self.streams.values():
                arr = np.frombuffer(audio_data, dtype=np.int16)
                arrays.append(arr)
            
            # Mix by averaging (prevents clipping)
            mixed = np.mean(arrays, axis=0).astype(np.int16)
            
            # Clear streams for next mix
            self.streams.clear()
            
            return mixed.tobytes()
            
        except Exception as e:
            print(f"Error mixing audio: {e}")
            return None
    
    def clear(self):
        """Clear all streams"""
        self.streams.clear()