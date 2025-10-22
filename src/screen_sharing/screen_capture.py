import mss
import numpy as np
from PIL import Image
import io
import threading
import queue
from typing import Optional, Tuple

class ScreenCapture:
    """Handles screen capture with threading"""
    
    def __init__(self, monitor_id: int = 1, fps: int = 15):
        self.monitor_id = monitor_id
        self.fps = fps
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = False
        self.thread = None
        self.sct = mss.mss()
        
    def start(self) -> bool:
        """Start screen capture"""
        try:
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Error starting screen capture: {e}")
            return False
    
    def _capture_loop(self):
        """Continuous screen capture loop"""
        import time
        interval = 1.0 / self.fps
        
        while self.running:
            start_time = time.time()
            
            try:
                # Capture screen
                monitor = self.sct.monitors[self.monitor_id]
                screenshot = self.sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Clear old frames if queue is full
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                try:
                    self.frame_queue.put_nowait(img)
                except queue.Full:
                    pass
                
            except Exception as e:
                print(f"Error capturing screen: {e}")
            
            # Maintain frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)
    
    def read(self) -> Optional[Image.Image]:
        """Get latest screen capture"""
        try:
            return self.frame_queue.get(timeout=0.1)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop screen capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.sct.close()