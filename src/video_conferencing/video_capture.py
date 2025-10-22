import cv2
import numpy as np
import threading
import queue
from typing import Optional, Tuple

class VideoCapture:
    """Handles webcam video capture with threading for performance"""
    
    def __init__(self, device_id: int = 0, resolution: Tuple[int, int] = (640, 480), fps: int = 30):
        self.device_id = device_id
        self.resolution = resolution
        self.fps = fps
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.capture = None
        self.thread = None
        
    def start(self) -> bool:
        """Initialize and start video capture"""
        self.capture = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
        
        if not self.capture.isOpened():
            return False
            
        # Set camera properties
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        return True
    
    def _capture_loop(self):
        """Continuous capture loop in separate thread"""
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                # Clear old frames if queue is full
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    pass
    
    def read(self) -> Optional[np.ndarray]:
        """Get latest frame from queue"""
        try:
            return self.frame_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop capture and cleanup"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.capture:
            self.capture.release()
