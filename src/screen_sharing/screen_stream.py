import socket
import struct
from PIL import Image
import io
import threading
from typing import Optional

class ScreenStreamer:
    """Handles screen streaming over TCP for reliability"""
    
    def __init__(self, quality: int = 75):
        self.quality = quality
        self.sock = None
        
    def setup_server(self, host: str, port: int) -> socket.socket:
        """Setup TCP server for screen sharing"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        return self.sock
    
    def setup_client(self, host: str, port: int) -> socket.socket:
        """Setup TCP client for receiving screen"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        return self.sock
    
    def send_screen(self, conn: socket.socket, image: Image.Image) -> bool:
        """Send screen image via TCP"""
        try:
            # Compress image
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=self.quality, optimize=True)
            data = buffer.getvalue()
            
            # Send size header + data
            size = len(data)
            header = struct.pack('!I', size)
            
            conn.sendall(header + data)
            return True
            
        except Exception as e:
            print(f"Error sending screen: {e}")
            return False
    
    def receive_screen(self, conn: socket.socket) -> Optional[Image.Image]:
        """Receive screen image from TCP"""
        try:
            # Receive size header
            header = self._recv_exact(conn, 4)
            if not header:
                return None
            
            size = struct.unpack('!I', header)[0]
            
            # Receive image data
            data = self._recv_exact(conn, size)
            if not data:
                return None
            
            # Decode image
            image = Image.open(io.BytesIO(data))
            return image
            
        except Exception as e:
            print(f"Error receiving screen: {e}")
            return None
    
    def _recv_exact(self, conn: socket.socket, size: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            chunk = conn.recv(min(size - len(data), 65536))
            if not chunk:
                return None
            data += chunk
        return data
    
    def close(self):
        """Close socket"""
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()


class ScreenDisplay:
    """Handles screen image display"""
    
    def __init__(self):
        self.window_name = "Screen Share"
        
    def show(self, image: Image.Image):
        """Display screen image"""
        import cv2
        import numpy as np
        
        # Convert PIL to OpenCV
        img_array = np.array(image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        cv2.imshow(self.window_name, img_bgr)
        cv2.waitKey(1)
    
    def close(self):
        """Close display window"""
        import cv2
        cv2.destroyWindow(self.window_name)
