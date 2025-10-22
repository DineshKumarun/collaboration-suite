import socket
import threading
import json
import struct
import time
import os
from typing import Dict, Set, Tuple
from pathlib import Path
import numpy as np

class CollaborationServer:
    """Main server coordinating all collaboration features"""
    
    def __init__(self, config_path: str = "configs/config.json"):
        self.load_config(config_path)
        
        self.clients: Dict[str, Dict] = {}  # client_id -> {address, sockets, info}
        self.clients_lock = threading.Lock()
        
        self.running = False
        self.control_socket = None
        
        # Server sockets for different services
        self.video_socket = None
        self.audio_socket = None
        self.screen_socket = None
        self.chat_socket = None
        self.file_socket = None
        
        # Audio mixing
        self.audio_buffer = {}  # client_id -> latest audio chunk
        self.audio_buffer_lock = threading.Lock()
        
        # File storage
        self.shared_files = {}  # file_id -> {filename, size, path, uploader}
        self.files_dir = Path("shared_files")
        self.files_dir.mkdir(exist_ok=True)
        
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Config file not found, using defaults")
            self.config = {
                "server": {
                    "host": "0.0.0.0",
                    "video_port": 5000,
                    "audio_port": 5001,
                    "screen_port": 5002,
                    "chat_port": 5003,
                    "file_port": 5004,
                    "control_port": 5005
                }
            }
    
    def start(self):
        """Start all server components"""
        print("Starting Collaboration Server...")
        
        self.running = True
        
        # Setup control server
        self.setup_control_server()
        
        # Setup service servers
        self.setup_video_relay()
        self.setup_audio_relay()
        self.setup_screen_relay()
        self.setup_chat_server()
        self.setup_file_server()
        
        print(f"Server running on {self.config['server']['host']}")
        print(f"Control Port: {self.config['server']['control_port']}")
        print(f"Video Port: {self.config['server']['video_port']}")
        print(f"Audio Port: {self.config['server']['audio_port']}")
        print(f"Chat Port: {self.config['server']['chat_port']}")
        print(f"File Port: {self.config['server']['file_port']}")
        
    def setup_control_server(self):
        """Setup control server for client management"""
        try:
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.control_socket.bind((
                self.config['server']['host'],
                self.config['server']['control_port']
            ))
            self.control_socket.listen(10)
            
            thread = threading.Thread(target=self.accept_control_connections, daemon=True)
            thread.start()
            
            print("Control server started")
        except Exception as e:
            print(f"Error starting control server: {e}")
    
    def accept_control_connections(self):
        """Accept control connections from clients"""
        while self.running:
            try:
                conn, addr = self.control_socket.accept()
                thread = threading.Thread(
                    target=self.handle_control_client,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running:
                    print(f"Error accepting control connection: {e}")
    
    def handle_control_client(self, conn: socket.socket, addr: Tuple):
        """Handle control messages from client"""
        client_id = None
        
        try:
            # Receive client info
            data = conn.recv(4096)
            if data:
                info = json.loads(data.decode('utf-8'))
                client_id = info.get('client_id')
                username = info.get('username')
                
                with self.clients_lock:
                    self.clients[client_id] = {
                        'address': addr,
                        'username': username,
                        'control_conn': conn,
                        'connected': True
                    }
                
                # Send acknowledgment with client list
                client_list = self.get_client_list()
                response = {
                    'status': 'connected',
                    'clients': client_list
                }
                conn.sendall(json.dumps(response).encode('utf-8'))
                
                # Broadcast new client to others
                self.broadcast_client_update('joined', client_id, username)
                
                print(f"Client connected: {username} ({client_id})")
            
            # Keep connection alive for control messages
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                
                # Handle control messages (requests, commands, etc.)
                self.process_control_message(client_id, data)
                
        except Exception as e:
            print(f"Error handling control client: {e}")
        finally:
            if client_id:
                with self.clients_lock:
                    if client_id in self.clients:
                        username = self.clients[client_id]['username']
                        del self.clients[client_id]
                        self.broadcast_client_update('left', client_id, username)
                        print(f"Client disconnected: {username}")
            
            try:
                conn.close()
            except:
                pass
    
    def process_control_message(self, client_id: str, data: bytes):
        """Process control messages from clients"""
        try:
            message = json.loads(data.decode('utf-8'))
            msg_type = message.get('type')
            
            if msg_type == 'ping':
                # Respond to keepalive
                with self.clients_lock:
                    if client_id in self.clients:
                        conn = self.clients[client_id]['control_conn']
                        conn.sendall(b'{"type":"pong"}')
            
            elif msg_type == 'request_clients':
                # Send updated client list
                client_list = self.get_client_list()
                response = {'type': 'client_list', 'clients': client_list}
                with self.clients_lock:
                    if client_id in self.clients:
                        conn = self.clients[client_id]['control_conn']
                        conn.sendall(json.dumps(response).encode('utf-8'))
                        
        except Exception as e:
            print(f"Error processing control message: {e}")
    
    def get_client_list(self) -> list:
        """Get list of connected clients"""
        with self.clients_lock:
            return [
                {'client_id': cid, 'username': info['username']}
                for cid, info in self.clients.items()
            ]
    
    def broadcast_client_update(self, action: str, client_id: str, username: str):
        """Broadcast client join/leave to all clients"""
        message = {
            'type': 'client_update',
            'action': action,
            'client_id': client_id,
            'username': username
        }
        data = (json.dumps(message) + '\n').encode('utf-8')  # Add newline delimiter
        
        print(f"Broadcasting {action} for {username} to all clients")
        
        with self.clients_lock:
            for cid, info in self.clients.items():
                if cid != client_id:  # Don't send to the client itself
                    try:
                        info['control_conn'].sendall(data)
                        print(f"  → Sent to {info['username']}")
                    except Exception as e:
                        print(f"  → Failed to send to {info['username']}: {e}")
    
    def setup_video_relay(self):
        """Setup UDP relay for video streams"""
        thread = threading.Thread(target=self.relay_video, daemon=True)
        thread.start()
    
    def relay_video(self):
        """Relay video packets between clients with sender identification"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152)  # 2MB buffer
            sock.bind((
                self.config['server']['host'],
                self.config['server']['video_port']
            ))
            
            print("Video relay started")
            
            while self.running:
                try:
                    data, addr = sock.recvfrom(65536)
                    
                    # Parse packet: client_id_len(1) + client_id + video_data
                    if len(data) < 2:
                        continue
                    
                    client_id_len = struct.unpack('B', data[0:1])[0]
                    if len(data) < 1 + client_id_len:
                        continue
                    
                    sender_id = data[1:1+client_id_len].decode('utf-8')
                    video_data = data[1+client_id_len:]
                    
                    # Relay to all other clients with sender ID
                    with self.clients_lock:
                        for client_id, client_info in self.clients.items():
                            if client_id != sender_id:
                                try:
                                    client_addr = client_info.get('video_addr', client_info['address'])
                                    sock.sendto(data, (client_addr[0], self.config['server']['video_port']))
                                except Exception as e:
                                    pass
                                    
                except Exception as e:
                    if self.running:
                        print(f"Error relaying video: {e}")
                        
        except Exception as e:
            print(f"Error starting video relay: {e}")
    
    def setup_audio_relay(self):
        """Setup UDP relay for audio streams"""
        thread = threading.Thread(target=self.relay_audio, daemon=True)
        thread.start()
    
    def relay_audio(self):
        """Receive audio from all clients, mix, and broadcast mixed audio"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2097152)  # 2MB buffer
            sock.bind((
                self.config['server']['host'],
                self.config['server']['audio_port']
            ))
            sock.settimeout(0.01)  # 10ms timeout for mixing loop
            
            print("Audio relay started with mixing")
            
            last_mix_time = time.time()
            mix_interval = 0.02  # Mix every 20ms
            
            while self.running:
                try:
                    # Receive audio packets
                    try:
                        data, addr = sock.recvfrom(65536)
                        
                        # Parse packet: client_id_len(1) + client_id + audio_data
                        if len(data) < 2:
                            continue
                        
                        try:
                            client_id_len = struct.unpack('B', data[0:1])[0]
                            if len(data) < 1 + client_id_len:
                                continue
                            
                            sender_id = data[1:1+client_id_len].decode('utf-8', errors='ignore')
                            audio_data = data[1+client_id_len:]
                        except Exception as decode_err:
                            # Skip malformed packets
                            continue
                        
                        # Store in buffer
                        with self.audio_buffer_lock:
                            self.audio_buffer[sender_id] = audio_data
                            
                    except socket.timeout:
                        pass
                    
                    # Mix and broadcast at regular intervals
                    current_time = time.time()
                    if current_time - last_mix_time >= mix_interval:
                        with self.audio_buffer_lock:
                            if len(self.audio_buffer) > 0:
                                # Mix audio from all clients
                                mixed_audio = self.mix_audio_streams(list(self.audio_buffer.values()))
                                
                                # Broadcast mixed audio to all clients
                                with self.clients_lock:
                                    for client_id, client_info in self.clients.items():
                                        try:
                                            client_addr = client_info.get('audio_addr', client_info['address'])
                                            sock.sendto(mixed_audio, (client_addr[0], self.config['server']['audio_port']))
                                        except Exception as e:
                                            pass
                                
                                # Clear buffer
                                self.audio_buffer.clear()
                        
                        last_mix_time = current_time
                        
                except Exception as e:
                    if self.running:
                        print(f"Error relaying audio: {e}")
                        
        except Exception as e:
            print(f"Error starting audio relay: {e}")
    
    def mix_audio_streams(self, audio_chunks):
        """Mix multiple audio streams together"""
        if not audio_chunks:
            return b''
        
        try:
            # Convert bytes to numpy arrays
            arrays = []
            for chunk in audio_chunks:
                arr = np.frombuffer(chunk, dtype=np.int16)
                arrays.append(arr)
            
            # Find minimum length
            min_len = min(len(arr) for arr in arrays)
            
            # Truncate all to same length
            arrays = [arr[:min_len] for arr in arrays]
            
            # Mix by averaging (prevents clipping)
            mixed = np.mean(arrays, axis=0).astype(np.int16)
            
            return mixed.tobytes()
        except Exception as e:
            print(f"Error mixing audio: {e}")
            # Return first chunk if mixing fails
            return audio_chunks[0] if audio_chunks else b''
    
    def setup_screen_relay(self):
        """Setup TCP relay for screen sharing"""
        thread = threading.Thread(target=self.relay_screen, daemon=True)
        thread.start()
    
    def relay_screen(self):
        """Relay screen sharing data via TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((
                self.config['server']['host'],
                self.config['server']['screen_port']
            ))
            sock.listen(10)
            
            print("Screen sharing server started")
            
            screen_clients = []  # List of connected screen sharing clients
            active_presenter = None  # Currently presenting client connection
            
            def handle_screen_client(conn, addr):
                nonlocal active_presenter
                screen_clients.append(conn)
                
                try:
                    while self.running:
                        # Receive data size first (4 bytes)
                        size_data = conn.recv(4)
                        if not size_data:
                            break
                        
                        data_size = struct.unpack('!I', size_data)[0]
                        
                        # Receive the actual data
                        data = b''
                        while len(data) < data_size:
                            chunk = conn.recv(min(data_size - len(data), 65536))
                            if not chunk:
                                break
                            data += chunk
                        
                        if len(data) != data_size:
                            break
                        
                        # Parse: client_id_len(1) + client_id + screen_data
                        if len(data) < 2:
                            continue
                        
                        client_id_len = struct.unpack('B', data[0:1])[0]
                        sender_id = data[1:1+client_id_len].decode('utf-8')
                        
                        # Broadcast to all other screen clients
                        for client_conn in screen_clients:
                            if client_conn != conn:
                                try:
                                    client_conn.sendall(size_data + data)
                                except:
                                    pass
                except Exception as e:
                    pass
                finally:
                    if conn in screen_clients:
                        screen_clients.remove(conn)
                    if active_presenter == conn:
                        active_presenter = None
                    try:
                        conn.close()
                    except:
                        pass
            
            while self.running:
                try:
                    conn, addr = sock.accept()
                    thread = threading.Thread(
                        target=handle_screen_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting screen connection: {e}")
                        
        except Exception as e:
            print(f"Error starting screen relay: {e}")
    
    def setup_file_server(self):
        """Setup file transfer server"""
        thread = threading.Thread(target=self.run_file_server, daemon=True)
        thread.start()
    
    def run_file_server(self):
        """Handle file upload/download requests"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((
                self.config['server']['host'],
                self.config['server']['file_port']
            ))
            sock.listen(10)
            
            print("File server started")
            
            def handle_file_client(conn, addr):
                try:
                    # Receive command
                    cmd_data = conn.recv(1024)
                    if not cmd_data:
                        return
                    
                    command = json.loads(cmd_data.decode('utf-8'))
                    cmd_type = command.get('type')
                    
                    if cmd_type == 'upload':
                        # Handle file upload
                        file_id = command.get('file_id')
                        filename = command.get('filename')
                        filesize = command.get('filesize')
                        uploader = command.get('uploader')
                        
                        # Receive file data
                        filepath = self.files_dir / f"{file_id}_{filename}"
                        received = 0
                        
                        with open(filepath, 'wb') as f:
                            while received < filesize:
                                chunk = conn.recv(min(filesize - received, 65536))
                                if not chunk:
                                    break
                                f.write(chunk)
                                received += len(chunk)
                        
                        # Store file metadata
                        self.shared_files[file_id] = {
                            'filename': filename,
                            'size': filesize,
                            'path': str(filepath),
                            'uploader': uploader
                        }
                        
                        # Send acknowledgment
                        response = {'status': 'success', 'message': 'File uploaded'}
                        conn.sendall(json.dumps(response).encode('utf-8'))
                        
                        # Notify all clients about new file
                        self.broadcast_file_notification(file_id, filename, filesize, uploader)
                        
                    elif cmd_type == 'download':
                        # Handle file download
                        file_id = command.get('file_id')
                        
                        if file_id in self.shared_files:
                            file_info = self.shared_files[file_id]
                            filepath = file_info['path']
                            
                            # Send file size first
                            filesize = os.path.getsize(filepath)
                            response = {
                                'status': 'success',
                                'size': filesize,
                                'filename': file_info['filename']
                            }
                            conn.sendall(json.dumps(response).encode('utf-8') + b'\n')
                            
                            # Wait for ready signal
                            conn.recv(1024)
                            
                            # Send file data
                            with open(filepath, 'rb') as f:
                                while True:
                                    chunk = f.read(65536)
                                    if not chunk:
                                        break
                                    conn.sendall(chunk)
                        else:
                            response = {'status': 'error', 'message': 'File not found'}
                            conn.sendall(json.dumps(response).encode('utf-8'))
                    
                    elif cmd_type == 'list':
                        # Send list of available files
                        files_list = [
                            {
                                'file_id': fid,
                                'filename': info['filename'],
                                'size': info['size'],
                                'uploader': info['uploader']
                            }
                            for fid, info in self.shared_files.items()
                        ]
                        response = {'status': 'success', 'files': files_list}
                        conn.sendall(json.dumps(response).encode('utf-8'))
                        
                except Exception as e:
                    print(f"Error handling file client: {e}")
                finally:
                    try:
                        conn.close()
                    except:
                        pass
            
            while self.running:
                try:
                    conn, addr = sock.accept()
                    thread = threading.Thread(
                        target=handle_file_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting file connection: {e}")
                        
        except Exception as e:
            print(f"Error starting file server: {e}")
    
    def broadcast_file_notification(self, file_id, filename, filesize, uploader):
        """Notify all clients about a new shared file"""
        message = {
            'type': 'file_notification',
            'file_id': file_id,
            'filename': filename,
            'size': filesize,
            'uploader': uploader
        }
        data = json.dumps(message).encode('utf-8')
        
        with self.clients_lock:
            for client_id, info in self.clients.items():
                try:
                    info['control_conn'].sendall(data + b'\n')
                except:
                    pass
    
    def setup_chat_server(self):
        """Setup chat message relay"""
        thread = threading.Thread(target=self.relay_chat, daemon=True)
        thread.start()
    
    def relay_chat(self):
        """Relay chat messages between clients"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((
                self.config['server']['host'],
                self.config['server']['chat_port']
            ))
            sock.listen(10)
            
            print("Chat server started")
            
            chat_clients = []
            
            def handle_chat_client(conn, addr):
                chat_clients.append(conn)
                try:
                    while self.running:
                        data = conn.recv(4096)
                        if not data:
                            break
                        
                        # Broadcast to all chat clients
                        for client_conn in chat_clients:
                            if client_conn != conn:
                                try:
                                    client_conn.sendall(data)
                                except:
                                    pass
                except:
                    pass
                finally:
                    if conn in chat_clients:
                        chat_clients.remove(conn)
                    conn.close()
            
            while self.running:
                try:
                    conn, addr = sock.accept()
                    thread = threading.Thread(
                        target=handle_chat_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    thread.start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting chat connection: {e}")
                        
        except Exception as e:
            print(f"Error starting chat server: {e}")
    
    def stop(self):
        """Stop server"""
        print("\nStopping server...")
        self.running = False
        
        # Close all sockets
        for sock in [self.control_socket, self.video_socket, self.audio_socket,
                     self.screen_socket, self.chat_socket, self.file_socket]:
            if sock:
                try:
                    sock.close()
                except:
                    pass
        
        print("Server stopped")


def main():
    """Main server entry point"""
    import signal
    
    server = CollaborationServer()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        server.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    server.start()
    
    # Keep server running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
