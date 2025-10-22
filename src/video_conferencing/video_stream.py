import socket
import struct
import cv2
import asyncio
from typing import Optional
import numpy as np

class VideoStreamer:
    """Handles video streaming over UDP with compression"""
    
    def __init__(self, quality: int = 80, client_id: str = None):
        self.quality = quality
        self.client_id = client_id
        self.sock = None
        self.encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        self.frame_buffer = {}  # For multi-client reception: client_id -> chunks
        
    def set_client_id(self, client_id: str):
        """Set client ID for packet identification"""
        self.client_id = client_id
        
    def setup_sender(self) -> socket.socket:
        """Setup UDP socket for sending"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        return self.sock
    
    def setup_receiver(self, host: str, port: int) -> socket.socket:
        """Setup UDP socket for receiving"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        # Bind to any available port (0 = OS assigns free port)
        # Server will send packets to the address that sent video packets
        self.sock.bind((host, 0))  # Changed from port to 0
        self.sock.settimeout(0.1)
        actual_port = self.sock.getsockname()[1]
        print(f"[VIDEO] Receiver bound to port {actual_port}")
        return self.sock
    
    def send_frame(self, frame: np.ndarray, address: tuple) -> bool:
        """Encode and send frame via UDP with client identification"""
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, self.encode_params)
            data = buffer.tobytes()
            
            # Prepare client ID prefix
            client_id_bytes = self.client_id.encode('utf-8') if self.client_id else b''
            client_id_len = len(client_id_bytes)
            
            # Split into chunks if needed (UDP packet size limit)
            max_chunk = 60000
            total_chunks = (len(data) + max_chunk - 1) // max_chunk
            
            for i in range(total_chunks):
                start = i * max_chunk
                end = min((i + 1) * max_chunk, len(data))
                chunk = data[start:end]
                
                # Header: client_id_len(1) + client_id + chunk_index(2) + total_chunks(2) + data
                header = struct.pack('BHH', client_id_len, i, total_chunks)
                packet = header + client_id_bytes + chunk
                
                self.sock.sendto(packet, address)
            
            return True
        except Exception as e:
            print(f"Error sending frame: {e}")
            return False
    
    def receive_frame(self) -> Optional[tuple]:
        """Receive and decode frame from UDP - returns (client_id, frame) tuple"""
        try:
            chunks = {}
            total_chunks = None
            sender_id = None
            
            while True:
                try:
                    packet, _ = self.sock.recvfrom(65536)
                    
                    # Parse header: client_id_len(1) + chunk_idx(2) + total(2)
                    if len(packet) < 5:
                        continue
                    
                    client_id_len, chunk_idx, total = struct.unpack('BHH', packet[:5])
                    
                    # Extract client ID
                    if len(packet) < 5 + client_id_len:
                        continue
                    
                    current_sender = packet[5:5+client_id_len].decode('utf-8')
                    chunk_data = packet[5+client_id_len:]
                    
                    # If first packet, set sender
                    if sender_id is None:
                        sender_id = current_sender
                    
                    # Only collect chunks from the same sender
                    if current_sender == sender_id:
                        chunks[chunk_idx] = chunk_data
                        total_chunks = total
                    
                    # Check if we have all chunks
                    if total_chunks and len(chunks) == total_chunks:
                        break
                        
                except socket.timeout:
                    if chunks:
                        break
                    return None
            
            if not chunks:
                return None
            
            # Reassemble data
            data = b''.join([chunks[i] for i in sorted(chunks.keys())])
            
            # Decode JPEG
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return (sender_id, frame) if sender_id else (None, frame)
            
        except Exception as e:
            print(f"Error receiving frame: {e}")
            return None
    
    def close(self):
        """Close socket"""
        if self.sock:
            self.sock.close()