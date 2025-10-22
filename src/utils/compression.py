import zlib
import numpy as np
from typing import Tuple, Optional

class CompressionUtils:
    """Compression utility functions"""
    
    @staticmethod
    def compress_data(data: bytes, level: int = 6) -> bytes:
        """Compress data using zlib"""
        return zlib.compress(data, level)
    
    @staticmethod
    def decompress_data(data: bytes) -> bytes:
        """Decompress zlib data"""
        return zlib.decompress(data)
    
    @staticmethod
    def compress_frame(frame: np.ndarray, quality: int = 80) -> Tuple[bytes, Tuple[int, int]]:
        """Compress video frame"""
        import cv2
        
        # Encode as JPEG
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_params)
        
        return buffer.tobytes(), frame.shape[:2]
    
    @staticmethod
    def decompress_frame(data: bytes, shape: Optional[Tuple[int, int]] = None) -> Optional[np.ndarray]:
        """Decompress video frame"""
        import cv2
        
        try:
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except:
            return None
    
    @staticmethod
    def compress_audio(audio_data: bytes) -> bytes:
        """Compress audio data (simple zlib for now)"""
        return zlib.compress(audio_data, level=1)
    
    @staticmethod
    def decompress_audio(data: bytes) -> bytes:
        """Decompress audio data"""
        return zlib.decompress(data)
