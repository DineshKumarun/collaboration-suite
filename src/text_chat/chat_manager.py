import socket
import threading
import queue
from typing import List, Callable, Optional
from .message_handler import Message, MessageHandler

class ChatManager:
    """Manages chat connections and message distribution"""
    
    def __init__(self, username: str):
        self.username = username
        self.sock = None
        self.running = False
        self.message_queue = queue.Queue()
        self.message_history: List[Message] = []
        self.receive_thread = None
        self.callbacks: List[Callable[[Message], None]] = []
        
    def setup_server(self, host: str, port: int) -> bool:
        """Setup TCP server for chat"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
            self.sock.listen(10)
            self.running = True
            return True
        except Exception as e:
            print(f"Error setting up chat server: {e}")
            return False
    
    def connect(self, host: str, port: int) -> bool:
        """Connect to chat server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Send join message
            join_msg = MessageHandler.create_message(
                self.username,
                f"{self.username} joined the chat",
                msg_type="system"
            )
            self.send_message(join_msg)
            
            return True
        except Exception as e:
            print(f"Error connecting to chat: {e}")
            return False
    
    def _receive_loop(self):
        """Continuously receive messages"""
        buffer = b''
        
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages (delimited by newline)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    message = MessageHandler.decode_message(line)
                    
                    if message:
                        self.message_history.append(message)
                        self.message_queue.put(message)
                        
                        # Call registered callbacks
                        for callback in self.callbacks:
                            try:
                                callback(message)
                            except Exception as e:
                                print(f"Error in message callback: {e}")
                                
            except Exception as e:
                if self.running:
                    print(f"Error receiving message: {e}")
                break
    
    def send_message(self, message: Message) -> bool:
        """Send message"""
        try:
            data = MessageHandler.encode_message(message)
            self.sock.sendall(data + b'\n')
            
            # Add to local history if not system message
            if message.message_type != "system":
                self.message_history.append(message)
            
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def send_text(self, content: str) -> bool:
        """Send text message"""
        message = MessageHandler.create_message(self.username, content)
        return self.send_message(message)
    
    def register_callback(self, callback: Callable[[Message], None]):
        """Register callback for new messages"""
        self.callbacks.append(callback)
    
    def get_message(self, timeout: float = 0.1) -> Optional[Message]:
        """Get message from queue"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_history(self, limit: int = 100) -> List[Message]:
        """Get message history"""
        return self.message_history[-limit:]
    
    def save_history(self, filepath: str):
        """Save chat history to file"""
        try:
            with open(filepath, 'w') as f:
                for msg in self.message_history:
                    f.write(msg.to_json() + '\n')
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def stop(self):
        """Stop chat manager"""
        self.running = False
        
        if self.sock:
            try:
                # Send leave message
                leave_msg = MessageHandler.create_message(
                    self.username,
                    f"{self.username} left the chat",
                    msg_type="system"
                )
                self.send_message(leave_msg)
            except:
                pass
            
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.sock.close()
        
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)