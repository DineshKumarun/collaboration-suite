import socket
import struct
import os
import hashlib
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
import json

@dataclass
class FileMetadata:
    """File metadata structure"""
    filename: str
    filesize: int
    checksum: str
    sender: str
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FileMetadata':
        data = json.loads(json_str)
        return cls(**data)


class FileTransfer:
    """Handles file transfer over TCP"""
    
    CHUNK_SIZE = 65536  # 64KB chunks
    
    def __init__(self):
        self.sock = None
        
    @staticmethod
    def calculate_checksum(filepath: str) -> str:
        """Calculate MD5 checksum of file"""
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()
    
    def setup_server(self, host: str, port: int) -> bool:
        """Setup TCP server for file transfer"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
            self.sock.listen(5)
            return True
        except Exception as e:
            print(f"Error setting up file server: {e}")
            return False
    
    def connect(self, host: str, port: int) -> bool:
        """Connect to file server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            return True
        except Exception as e:
            print(f"Error connecting to file server: {e}")
            return False
    
    def send_file(self, conn: socket.socket, filepath: str, sender: str,
                  progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """Send file with progress tracking"""
        try:
            # Get file info
            path = Path(filepath)
            if not path.exists():
                print(f"File not found: {filepath}")
                return False
            
            filename = path.name
            filesize = path.stat().st_size
            checksum = self.calculate_checksum(filepath)
            
            # Create metadata
            metadata = FileMetadata(filename, filesize, checksum, sender)
            metadata_json = metadata.to_json()
            
            # Send metadata
            metadata_bytes = metadata_json.encode('utf-8')
            metadata_size = len(metadata_bytes)
            
            # Send metadata size + metadata
            conn.sendall(struct.pack('!I', metadata_size))
            conn.sendall(metadata_bytes)
            
            # Wait for acknowledgment
            ack = conn.recv(3)
            if ack != b'ACK':
                print("No acknowledgment received")
                return False
            
            # Send file data
            bytes_sent = 0
            with open(filepath, 'rb') as f:
                while bytes_sent < filesize:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    conn.sendall(chunk)
                    bytes_sent += len(chunk)
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(bytes_sent, filesize)
            
            # Wait for final acknowledgment
            final_ack = conn.recv(3)
            if final_ack != b'ACK':
                print("File transfer not acknowledged")
                return False
            
            print(f"File sent successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error sending file: {e}")
            return False
    
    def receive_file(self, conn: socket.socket, save_dir: str,
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> Optional[FileMetadata]:
        """Receive file with progress tracking"""
        try:
            # Receive metadata size
            metadata_size_data = self._recv_exact(conn, 4)
            if not metadata_size_data:
                return None
            
            metadata_size = struct.unpack('!I', metadata_size_data)[0]
            
            # Receive metadata
            metadata_bytes = self._recv_exact(conn, metadata_size)
            if not metadata_bytes:
                return None
            
            metadata_json = metadata_bytes.decode('utf-8')
            metadata = FileMetadata.from_json(metadata_json)
            
            # Send acknowledgment
            conn.sendall(b'ACK')
            
            # Prepare save path
            save_path = Path(save_dir) / metadata.filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Receive file data
            bytes_received = 0
            md5 = hashlib.md5()
            
            with open(save_path, 'wb') as f:
                while bytes_received < metadata.filesize:
                    remaining = metadata.filesize - bytes_received
                    chunk_size = min(self.CHUNK_SIZE, remaining)
                    
                    chunk = self._recv_exact(conn, chunk_size)
                    if not chunk:
                        print("Connection lost during transfer")
                        return None
                    
                    f.write(chunk)
                    md5.update(chunk)
                    bytes_received += len(chunk)
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(bytes_received, metadata.filesize)
            
            # Verify checksum
            received_checksum = md5.hexdigest()
            if received_checksum != metadata.checksum:
                print(f"Checksum mismatch! Expected: {metadata.checksum}, Got: {received_checksum}")
                save_path.unlink()  # Delete corrupted file
                return None
            
            # Send final acknowledgment
            conn.sendall(b'ACK')
            
            print(f"File received successfully: {metadata.filename}")
            return metadata
            
        except Exception as e:
            print(f"Error receiving file: {e}")
            return None
    
    def _recv_exact(self, conn: socket.socket, size: int) -> Optional[bytes]:
        """Receive exact number of bytes"""
        data = b''
        while len(data) < size:
            chunk = conn.recv(min(size - len(data), self.CHUNK_SIZE))
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
