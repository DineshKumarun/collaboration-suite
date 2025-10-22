import socket
import threading
import json
import uuid
import cv2
from typing import Optional, Dict
import sys
from pathlib import Path

# Handle both direct execution and module import
if __name__ == "__main__":
    # Add project root to path when run directly
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.video_conferencing import VideoCapture, VideoStreamer
    from src.audio_conferencing import AudioCapture, AudioPlayback, AudioStreamer
    from src.text_chat import ChatManager, MessageHandler
else:
    # Use relative imports when imported as module
    from .video_conferencing import VideoCapture, VideoStreamer
    from .audio_conferencing import AudioCapture, AudioPlayback, AudioStreamer
    from .text_chat import ChatManager, MessageHandler


class CollaborationClient:
    """Main client for collaboration suite"""
    
    def __init__(self, username: str, server_host: str, config_path: str = "configs/config.json"):
        self.username = username
        self.server_host = server_host
        self.client_id = str(uuid.uuid4())
        
        self.load_config(config_path)
        
        # Connection status
        self.connected = False
        self.running = False
        
        # Control connection
        self.control_socket = None
        
        # Feature modules
        self.video_capture = None
        self.video_streamer = None
        self.audio_capture = None
        self.audio_playback = None
        self.audio_streamer = None
        self.chat_manager = None
        
        # Threads
        self.threads = []
        
        # Connected clients
        self.other_clients = {}
        
    def load_config(self, config_path: str):
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except:
            print("Using default configuration")
            self.config = {
                "server": {
                    "video_port": 5000,
                    "audio_port": 5001,
                    "chat_port": 5003,
                    "control_port": 5005
                },
                "video": {"resolution": [640, 480], "fps": 30, "quality": 80},
                "audio": {"sample_rate": 44100, "channels": 1, "chunk_size": 1024}
            }
    
    def connect(self) -> bool:
        """Connect to server"""
        try:
            print(f"Connecting to server at {self.server_host}...")
            
            # Connect control socket
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((
                self.server_host,
                self.config['server']['control_port']
            ))
            
            # Send client info
            info = {
                'client_id': self.client_id,
                'username': self.username
            }
            self.control_socket.sendall(json.dumps(info).encode('utf-8'))
            
            # Receive acknowledgment
            data = self.control_socket.recv(4096)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('status') == 'connected':
                self.connected = True
                self.other_clients = {c['client_id']: c for c in response.get('clients', [])}
                print(f"Connected! {len(self.other_clients)} other clients online")
                
                # Start control message handler
                thread = threading.Thread(target=self.handle_control_messages, daemon=True)
                thread.start()
                self.threads.append(thread)
                
                return True
            else:
                print("Failed to connect")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def handle_control_messages(self):
        """Handle control messages from server"""
        while self.connected:
            try:
                data = self.control_socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                msg_type = message.get('type')
                
                if msg_type == 'client_update':
                    action = message.get('action')
                    client_id = message.get('client_id')
                    username = message.get('username')
                    
                    if action == 'joined':
                        self.other_clients[client_id] = {'username': username}
                        print(f"\n{username} joined the session")
                    elif action == 'left':
                        if client_id in self.other_clients:
                            del self.other_clients[client_id]
                            print(f"\n{username} left the session")
                
                elif msg_type == 'pong':
                    pass  # Keepalive response
                    
            except Exception as e:
                if self.connected:
                    print(f"Error handling control message: {e}")
                break
    
    def start_video(self) -> bool:
        """Start video conferencing"""
        try:
            print("Starting video...")
            
            # Initialize video capture
            resolution = tuple(self.config['video']['resolution'])
            fps = self.config['video']['fps']
            self.video_capture = VideoCapture(resolution=resolution, fps=fps)
            
            if not self.video_capture.start():
                print("Failed to start camera")
                return False
            
            # Initialize video streamer
            quality = self.config['video']['quality']
            self.video_streamer = VideoStreamer(quality=quality)
            self.video_streamer.setup_sender()
            
            # Start sending thread
            thread = threading.Thread(target=self.send_video_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
            
            # Start receiving thread
            thread = threading.Thread(target=self.receive_video_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
            
            # Start local display thread
            thread = threading.Thread(target=self.display_local_video, daemon=True)
            thread.start()
            self.threads.append(thread)
            
            print("Video started")
            return True
            
        except Exception as e:
            print(f"Error starting video: {e}")
            return False
    
    def send_video_loop(self):
        """Continuously send video frames"""
        server_addr = (self.server_host, self.config['server']['video_port'])
        
        while self.running and self.connected:
            frame = self.video_capture.read()
            if frame is not None:
                self.video_streamer.send_frame(frame, server_addr)
    
    def receive_video_loop(self):
        """Continuously receive video frames"""
        recv_streamer = VideoStreamer()
        recv_streamer.setup_receiver('0.0.0.0', self.config['server']['video_port'])
        
        while self.running and self.connected:
            frame = recv_streamer.receive_frame()
            if frame is not None:
                cv2.imshow("Remote Video", frame)
                cv2.waitKey(1)
    
    def display_local_video(self):
        """Display local video feed"""
        while self.running and self.connected:
            frame = self.video_capture.read()
            if frame is not None:
                cv2.imshow("My Video", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    
    def start_audio(self) -> bool:
        """Start audio conferencing"""
        try:
            print("Starting audio...")
            
            # Initialize audio capture
            sample_rate = self.config['audio']['sample_rate']
            channels = self.config['audio']['channels']
            chunk_size = self.config['audio']['chunk_size']
            
            self.audio_capture = AudioCapture(sample_rate, channels, chunk_size)
            self.audio_playback = AudioPlayback(sample_rate, channels, chunk_size)
            
            if not self.audio_capture.start():
                print("Failed to start microphone")
                return False
            
            if not self.audio_playback.start():
                print("Failed to start audio playback")
                return False
            
            # Initialize audio streamer
            self.audio_streamer = AudioStreamer()
            self.audio_streamer.setup_sender()
            
            # Start sending thread
            thread = threading.Thread(target=self.send_audio_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
            
            # Start receiving thread
            thread = threading.Thread(target=self.receive_audio_loop, daemon=True)
            thread.start()
            self.threads.append(thread)
            
            print("Audio started")
            return True
            
        except Exception as e:
            print(f"Error starting audio: {e}")
            return False
    
    def send_audio_loop(self):
        """Continuously send audio chunks"""
        server_addr = (self.server_host, self.config['server']['audio_port'])
        
        while self.running and self.connected:
            audio_data = self.audio_capture.read()
            if audio_data:
                self.audio_streamer.send_audio(audio_data, server_addr)
    
    def receive_audio_loop(self):
        """Continuously receive and play audio"""
        recv_streamer = AudioStreamer()
        recv_streamer.setup_receiver('0.0.0.0', self.config['server']['audio_port'])
        
        while self.running and self.connected:
            audio_data = recv_streamer.receive_audio()
            if audio_data:
                self.audio_playback.play(audio_data)
    
    def start_chat(self) -> bool:
        """Start text chat"""
        try:
            print("Starting chat...")
            
            self.chat_manager = ChatManager(self.username)
            
            if not self.chat_manager.connect(
                self.server_host,
                self.config['server']['chat_port']
            ):
                print("Failed to connect to chat")
                return False
            
            # Register callback for new messages
            self.chat_manager.register_callback(self.on_chat_message)
            
            print("Chat started")
            return True
            
        except Exception as e:
            print(f"Error starting chat: {e}")
            return False
    
    def on_chat_message(self, message):
        """Callback for new chat messages"""
        if message.sender != self.username:
            print(f"\n[{message.format_time()}] {message.sender}: {message.content}")
            print("> ", end="", flush=True)
    
    def send_chat_message(self, content: str):
        """Send a chat message"""
        if self.chat_manager:
            self.chat_manager.send_text(content)
    
    def start_all(self) -> bool:
        """Start all collaboration features"""
        if not self.connected:
            if not self.connect():
                return False
        
        self.running = True
        
        # Start video
        if not self.start_video():
            print("Warning: Video failed to start")
        
        # Start audio
        if not self.start_audio():
            print("Warning: Audio failed to start")
        
        # Start chat
        if not self.start_chat():
            print("Warning: Chat failed to start")
        
        print("\n=== Collaboration Session Started ===")
        print("Commands:")
        print("  Type messages to chat")
        print("  /quit - Exit session")
        print("  /clients - Show connected clients")
        print("=====================================\n")
        
        return True
    
    def run_interactive(self):
        """Run interactive chat interface"""
        import sys
        
        while self.running:
            try:
                print("> ", end="", flush=True)
                message = input()
                
                if message.startswith('/'):
                    # Handle commands
                    if message == '/quit':
                        break
                    elif message == '/clients':
                        print(f"\nConnected clients ({len(self.other_clients)}):")
                        for client_id, info in self.other_clients.items():
                            print(f"  - {info['username']}")
                        print()
                    else:
                        print("Unknown command")
                else:
                    # Send chat message
                    if message.strip():
                        self.send_chat_message(message)
                        
            except EOFError:
                break
            except KeyboardInterrupt:
                break
        
        self.stop()
    
    def stop(self):
        """Stop client and cleanup"""
        print("\nStopping client...")
        self.running = False
        self.connected = False
        
        # Stop video
        if self.video_capture:
            self.video_capture.stop()
        if self.video_streamer:
            self.video_streamer.close()
        
        # Stop audio
        if self.audio_capture:
            self.audio_capture.stop()
        if self.audio_playback:
            self.audio_playback.stop()
        if self.audio_streamer:
            self.audio_streamer.close()
        
        # Stop chat
        if self.chat_manager:
            self.chat_manager.stop()
        
        # Close control socket
        if self.control_socket:
            try:
                self.control_socket.close()
            except:
                pass
        
        # Close all OpenCV windows
        cv2.destroyAllWindows()
        
        print("Client stopped")


def main():
    """Main client entry point"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python client.py <username> <server_ip>")
        print("Example: python client.py John 192.168.1.100")
        sys.exit(1)
    
    username = sys.argv[1]
    server_host = sys.argv[2]
    
    client = CollaborationClient(username, server_host)
    
    if client.start_all():
        try:
            client.run_interactive()
        except KeyboardInterrupt:
            pass
    
    client.stop()


if __name__ == "__main__":
    main()