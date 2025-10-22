import cv2
import numpy as np

class VideoDecoder:
    """Handles video frame decoding and display"""
    
    def __init__(self):
        self.windows = {}
    
    def display_frame(self, window_name: str, frame: np.ndarray):
        """Display frame in named window"""
        if frame is not None:
            cv2.imshow(window_name, frame)
            self.windows[window_name] = True
    
    def close_window(self, window_name: str):
        """Close specific window"""
        if window_name in self.windows:
            cv2.destroyWindow(window_name)
            del self.windows[window_name]
    
    def close_all(self):
        """Close all windows"""
        cv2.destroyAllWindows()
        self.windows.clear()