import socket
import struct
from typing import Optional, Tuple

class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    @staticmethod
    def is_port_available(host: str, port: int) -> bool:
        """Check if port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.close()
            return True
        except:
            return False
    
    @staticmethod
    def send_with_size(sock: socket.socket, data: bytes) -> bool:
        """Send data with size header"""
        try:
            size = len(data)
            header = struct.pack('!I', size)
            sock.sendall(header + data)
            return True
        except:
            return False
    
    @staticmethod
    def recv_with_size(sock: socket.socket) -> Optional[bytes]:
        """Receive data with size header"""
        try:
            # Receive size
            header = NetworkUtils.recv_exact(sock, 4)
            if not header:
                return None
            
            size = struct.unpack('!I', header)[0]
            
            # Receive data
            return NetworkUtils.recv_exact(sock, size)
        except:
            return None
    
    @staticmethod
    def recv_exact(sock: socket.socket, size: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(min(size - len(data), 65536))
            if not chunk:
                return None
            data += chunk
        return data
    
    @staticmethod
    def calculate_bandwidth(bytes_transferred: int, time_seconds: float) -> float:
        """Calculate bandwidth in Mbps"""
        if time_seconds == 0:
            return 0
        bits = bytes_transferred * 8
        mbps = bits / time_seconds / 1_000_000
        return mbps
