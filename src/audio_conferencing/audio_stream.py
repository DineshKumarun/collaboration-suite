import socket
import struct
from typing import Optional

class AudioStreamer:
    """Handles audio streaming over UDP"""
    
    def __init__(self, client_id: str = None):
        self.sock = None
        self.client_id = client_id
        
    def set_client_id(self, client_id: str):
        """Set client ID for packet identification"""
        self.client_id = client_id
        
    def setup_sender(self) -> socket.socket:
        """Setup UDP socket for sending audio"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        return self.sock
    
    def setup_receiver(self, host: str, port: int) -> socket.socket:
        """Setup UDP socket for receiving audio"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        # Bind to any available port (0 = OS assigns free port)
        self.sock.bind((host, 0))  # Changed from port to 0
        self.sock.settimeout(0.05)
        actual_port = self.sock.getsockname()[1]
        print(f"[AUDIO] Receiver bound to port {actual_port}")
        return self.sock
    
    def send_audio(self, audio_data: bytes, address: tuple) -> bool:
        """Send audio chunk via UDP with client identification"""
        try:
            # Add client ID prefix: client_id_len(1) + client_id + audio_data
            client_id_bytes = self.client_id.encode('utf-8') if self.client_id else b''
            client_id_len = len(client_id_bytes)
            
            header = struct.pack('B', client_id_len)
            packet = header + client_id_bytes + audio_data
            
            self.sock.sendto(packet, address)
            return True
        except Exception as e:
            print(f"Error sending audio: {e}")
            return False
    
    def receive_audio(self) -> Optional[bytes]:
        """Receive audio chunk from UDP"""
        try:
            data, _ = self.sock.recvfrom(65536)
            return data
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Error receiving audio: {e}")
            return None
    
    def close(self):
        """Close socket"""
        if self.sock:
            self.sock.close()