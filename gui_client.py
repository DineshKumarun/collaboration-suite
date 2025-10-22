"""
Enhanced GUI-Based Collaboration Client
Multi-user video conferencing with audio, chat, screen sharing, and file transfer
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import cv2
from PIL import Image, ImageTk
import threading
import queue
import socket
import json
import uuid
import numpy as np
import struct
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.video_conferencing import VideoCapture, VideoStreamer
from src.audio_conferencing import AudioCapture, AudioPlayback, AudioStreamer
from src.text_chat import ChatManager, MessageHandler
from src.screen_sharing import ScreenCapture, ScreenStreamer
from src.file_sharing import FileTransfer


class LoginDialog:
    """Initial dialog to get username and server IP"""
    
    def __init__(self):
        print("[LoginDialog] Initializing...")
        self.root = tk.Tk()
        self.root.title("Join Collaboration Session")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self.username = None
        self.server_ip = None
        
        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        print("[LoginDialog] Initialized successfully")
        
    def _create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="LAN Collaboration Suite",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)
        
        # Username field
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(frame1, text="Username:", width=12, anchor='w').pack(side=tk.LEFT)
        self.username_entry = tk.Entry(frame1, width=25)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.username_entry.focus()
        
        # Server IP field
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(frame2, text="Server IP:", width=12, anchor='w').pack(side=tk.LEFT)
        self.server_entry = tk.Entry(frame2, width=25)
        self.server_entry.insert(0, "127.0.0.1")
        self.server_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Connect button
        connect_btn = tk.Button(
            self.root,
            text="Connect",
            command=self._on_connect,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        )
        connect_btn.pack(pady=20)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self._on_connect())
        
    def _on_connect(self):
        username = self.username_entry.get().strip()
        server_ip = self.server_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        if not server_ip:
            messagebox.showerror("Error", "Please enter server IP")
            return
        
        self.username = username
        self.server_ip = server_ip
        self.root.quit()
        
    def _on_close(self):
        self.root.quit()
        
    def show(self):
        """Show dialog and return username, server_ip"""
        print("[LoginDialog] Starting mainloop...")
        self.root.mainloop()
        print("[LoginDialog] Mainloop ended, destroying window...")
        self.root.destroy()
        print(f"[LoginDialog] Returning: username='{self.username}', server_ip='{self.server_ip}'")
        return self.username, self.server_ip


class ClientVideoBox(tk.Frame):
    """Video box for each client in the grid"""
    
    def __init__(self, parent, client_id, username):
        super().__init__(parent, bg="#2c3e50", relief=tk.RAISED, borderwidth=2)
        
        self.client_id = client_id
        self.username = username
        self.video_label = None
        self.name_label = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Name label at top
        self.name_label = tk.Label(
            self,
            text=self.username,
            bg="#34495e",
            fg="white",
            font=("Arial", 10, "bold"),
            pady=5
        )
        self.name_label.pack(fill=tk.X)
        
        # Video display area
        self.video_label = tk.Label(self, bg="#000000")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Show placeholder initially
        self._show_placeholder()
        
    def _show_placeholder(self):
        """Show placeholder when no video"""
        width, height = 320, 240
        placeholder = np.zeros((height, width, 3), dtype=np.uint8)
        placeholder[:, :] = [44, 62, 80]  # Dark blue-gray
        
        # Add text
        cv2.putText(
            placeholder,
            self.username[:15],
            (10, height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
        cv2.putText(
            placeholder,
            "No Video",
            (10, height // 2 + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (150, 150, 150),
            1
        )
        
        self.update_frame(placeholder)
        
    def update_frame(self, frame):
        """Update video frame"""
        if frame is None:
            self._show_placeholder()
            return
        
        try:
            # Get label dimensions
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            
            if label_width > 1 and label_height > 1:
                # Resize maintaining aspect ratio
                height, width = frame.shape[:2]
                scale_w = label_width / width
                scale_h = label_height / height
                scale = min(scale_w, scale_h)
                
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB for Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
        except Exception as e:
            print(f"Error updating frame for {self.username}: {e}")


class CollaborationGUI:
    """Main collaboration GUI with all features"""
    
    def __init__(self, username, server_ip):
        print(f"[CollaborationGUI.__init__] ENTERED - username={username}, server_ip={server_ip}")
        self.username = username
        self.server_ip = server_ip
        self.client_id = str(uuid.uuid4())
        print(f"[CollaborationGUI.__init__] Client ID generated: {self.client_id}")
        
        # Connection state
        self.connected = False
        self.session_active = False
        self.running = True
        
        # Sockets
        self.control_socket = None
        self.video_socket = None
        self.audio_socket = None
        self.chat_socket = None
        
        # Feature states
        self.video_enabled = False
        self.audio_enabled = False
        self.audio_muted = False
        self.screen_sharing = False
        
        # Components
        self.video_capture = None
        self.video_streamer = None
        self.audio_capture = None
        self.audio_playback = None
        self.audio_streamer = None
        
        # Client tracking
        self.clients = {}  # client_id -> {username, video_box}
        self.video_frames = queue.Queue()  # Queue of (client_id, frame) tuples
        
        # Queues
        self.chat_queue = queue.Queue()
        self.control_queue = queue.Queue()
        
        # Load config
        self.load_config()
        
        print(f"[CollaborationGUI] Config loaded")
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"Collaboration Suite - {username}")
        self.root.geometry("1400x900")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        print(f"[CollaborationGUI] Tk window created, building interface...")
        self._create_gui()
        print(f"[CollaborationGUI] GUI created successfully")
        
    def load_config(self):
        """Load configuration"""
        try:
            with open("configs/config.json", 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "server": {
                    "video_port": 5000,
                    "audio_port": 5001,
                    "screen_port": 5002,
                    "chat_port": 5003,
                    "file_port": 5004,
                    "control_port": 5005
                },
                "video": {"resolution": [640, 480], "fps": 30, "quality": 80},
                "audio": {"sample_rate": 44100, "channels": 1, "chunk_size": 2048}
            }
        
    def _create_gui(self):
        """Create main GUI layout"""
        print("[_create_gui] Starting GUI creation...")
        
        # Top bar with username and controls
        print("[_create_gui] Creating top bar...")
        top_bar = tk.Frame(self.root, bg="#34495e", height=70)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)
        
        # Username display
        print("[_create_gui] Creating username display...")
        user_frame = tk.Frame(top_bar, bg="#34495e")
        user_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        print("[_create_gui] Creating username label...")
        tk.Label(
            user_frame,
            text=f"👤 {self.username}",
            bg="#34495e",
            fg="white",
            font=("Arial", 14, "bold")
        ).pack()
        
        # Control buttons
        print("[_create_gui] Creating control buttons...")
        btn_config = {
            'font': ("Arial", 10, "bold"),
            'padx': 12,
            'pady': 8,
            'relief': tk.RAISED,
            'borderwidth': 2
        }
        
        btn_frame = tk.Frame(top_bar, bg="#34495e")
        btn_frame.pack(side=tk.LEFT, expand=True, pady=10)
        
        print("[_create_gui] Creating Join Session button...")
        self.join_btn = tk.Button(
            btn_frame,
            text="Join Session",
            command=self.join_session,
            bg="#27ae60",
            fg="white",
            **btn_config
        )
        self.join_btn.pack(side=tk.LEFT, padx=3)
        
        print("[_create_gui] Creating Leave Session button...")
        self.leave_btn = tk.Button(
            btn_frame,
            text="Leave Session",
            command=self.leave_session,
            bg="#e74c3c",
            fg="white",
            state=tk.DISABLED,
            **btn_config
        )
        self.leave_btn.pack(side=tk.LEFT, padx=3)
        
        self.video_btn = tk.Button(
            btn_frame,
            text="Start Video",
            command=self.toggle_video,
            bg="#3498db",
            fg="white",
            state=tk.DISABLED,
            **btn_config
        )
        self.video_btn.pack(side=tk.LEFT, padx=3)
        
        self.audio_btn = tk.Button(
            btn_frame,
            text="Unmute",
            command=self.toggle_audio_mute,
            bg="#9b59b6",
            fg="white",
            state=tk.DISABLED,
            **btn_config
        )
        self.audio_btn.pack(side=tk.LEFT, padx=3)
        
        self.screen_btn = tk.Button(
            btn_frame,
            text="Share Screen",
            command=self.toggle_screen_share,
            bg="#e67e22",
            fg="white",
            state=tk.DISABLED,
            **btn_config
        )
        self.screen_btn.pack(side=tk.LEFT, padx=3)
        
        self.file_btn = tk.Button(
            btn_frame,
            text="Send File",
            command=self.send_file,
            bg="#16a085",
            fg="white",
            state=tk.DISABLED,
            **btn_config
        )
        self.file_btn.pack(side=tk.LEFT, padx=3)
        
        # Main content area
        print("[_create_gui] Creating main content area...")
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video grid (left side - 70%)
        print("[_create_gui] Creating video container...")
        self.video_container = tk.Frame(main_frame, bg="#1a1a1a")
        self.video_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel (30%)
        print("[_create_gui] Creating right panel...")
        right_panel = tk.Frame(main_frame, bg="#ecf0f1", width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Chat section
        print("[_create_gui] Creating chat section...")
        chat_frame = tk.Frame(right_panel, bg="#ecf0f1")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        print("[_create_gui] Chat frame created")
        
        chat_title = tk.Label(
            chat_frame,
            text="💬 Group Chat",
            bg="#34495e",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=8
        )
        chat_title.pack(fill=tk.X)
        print("[_create_gui] Chat title created")
        
        print("[_create_gui] Creating ScrolledText widget...")
        # Create frame for text and scrollbar
        chat_text_frame = tk.Frame(chat_frame, bg="white")
        chat_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbar
        chat_scrollbar = tk.Scrollbar(chat_text_frame)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create text widget
        self.chat_display = tk.Text(
            chat_text_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="white",
            height=15,
            yscrollcommand=chat_scrollbar.set
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.config(command=self.chat_display.yview)
        self.chat_display.config(state=tk.DISABLED)
        print("[_create_gui] Chat display widget created and configured")
        
        chat_input_frame = tk.Frame(chat_frame, bg="#ecf0f1")
        chat_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chat_input = tk.Entry(chat_input_frame, font=("Arial", 10))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())
        
        send_btn = tk.Button(
            chat_input_frame,
            text="Send",
            command=self.send_chat_message,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold")
        )
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # File sharing section
        print("[_create_gui] Creating file sharing section...")
        file_frame = tk.Frame(right_panel, bg="#ecf0f1", height=200)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        file_frame.pack_propagate(False)
        
        file_title = tk.Label(
            file_frame,
            text="📁 Shared Files",
            bg="#34495e",
            fg="white",
            font=("Arial", 11, "bold"),
            pady=6
        )
        file_title.pack(fill=tk.X)
        
        self.file_listbox = tk.Listbox(file_frame, font=("Arial", 9))
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.file_listbox.bind('<Double-Button-1>', self.download_file)
        
        # Status bar
        print("[_create_gui] Creating status bar...")
        self.status_bar = tk.Label(
            self.root,
            text="Not connected - Click 'Join Session' to start",
            bg="#2c3e50",
            fg="white",
            anchor=tk.W,
            padx=10,
            font=("Arial", 9)
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        print("[_create_gui] GUI creation completed!")
        
    def join_session(self):
        """Join the collaboration session"""
        if self.session_active:
            return
        
        self.status_bar.config(text="Connecting to server...")
        self.root.update()
        
        # Connect to server
        if self.connect_to_server():
            self.session_active = True
            self.status_bar.config(text=f"Connected to {self.server_ip}")
            
            # Enable controls
            self.join_btn.config(state=tk.DISABLED)
            self.leave_btn.config(state=tk.NORMAL)
            self.video_btn.config(state=tk.NORMAL)
            self.audio_btn.config(state=tk.NORMAL)
            self.screen_btn.config(state=tk.NORMAL)
            self.file_btn.config(state=tk.NORMAL)
            
            # Video grid already updated in connect_to_server
            # Don't auto-start video/audio - user must click buttons
            
            # Start video/audio receivers (even if not sending yet)
            print("[CLIENT] Starting video receiver thread...")
            video_recv_thread = threading.Thread(target=self.receive_video_loop, daemon=True)
            video_recv_thread.start()
            
            print("[CLIENT] Starting audio receiver thread...")
            audio_recv_thread = threading.Thread(target=self.receive_audio_loop, daemon=True)
            audio_recv_thread.start()
            
            # Start update loop
            self.update_gui()
        else:
            messagebox.showerror("Connection Error", "Failed to connect to server")
            self.status_bar.config(text="Connection failed")
            
    def leave_session(self):
        """Leave the collaboration session"""
        if not self.session_active:
            return
        
        self.session_active = False
        self.connected = False
        
        # Stop all services
        if self.video_enabled:
            self.toggle_video()
        if self.audio_enabled:
            self.stop_audio()
        
        # Close sockets
        self.disconnect_from_server()
        
        # Update UI
        self.join_btn.config(state=tk.NORMAL)
        self.leave_btn.config(state=tk.DISABLED)
        self.video_btn.config(state=tk.DISABLED)
        self.audio_btn.config(state=tk.DISABLED)
        self.screen_btn.config(state=tk.DISABLED)
        self.file_btn.config(state=tk.DISABLED)
        
        # Clear video grid
        self.clients.clear()
        self._update_video_grid()
        
        self.status_bar.config(text="Disconnected from session")
        
    def connect_to_server(self):
        """Connect to collaboration server"""
        try:
            # Connect control socket
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((
                self.server_ip,
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
                # Add other clients to grid
                for client in response.get('clients', []):
                    if client['client_id'] != self.client_id:
                        self.clients[client['client_id']] = {
                            'username': client['username'],
                            'video_box': None
                        }
                
                # Add self to grid
                self.clients[self.client_id] = {
                    'username': self.username + " (You)",
                    'video_box': None
                }
                
                # Update video grid to show all participants
                self._update_video_grid()
                
                # Start control message handler
                thread = threading.Thread(target=self.handle_control_messages, daemon=True)
                thread.start()
                
                self.connected = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect_from_server(self):
        """Disconnect from server"""
        if self.control_socket:
            try:
                self.control_socket.close()
            except:
                pass
            self.control_socket = None
    
    def handle_control_messages(self):
        """Handle control messages from server"""
        while self.connected and self.session_active:
            try:
                data = self.control_socket.recv(4096)
                if not data:
                    break
                
                # Handle multiple JSON messages
                for line in data.decode('utf-8').strip().split('\n'):
                    if line:
                        message = json.loads(line)
                        self.control_queue.put(message)
                        
            except Exception as e:
                if self.connected:
                    print(f"Error handling control message: {e}")
                break
        
    def process_control_messages(self):
        """Process control messages in main thread"""
        try:
            while True:
                message = self.control_queue.get_nowait()
                msg_type = message.get('type')
                
                if msg_type == 'client_update':
                    action = message.get('action')
                    client_id = message.get('client_id')
                    username = message.get('username')
                    
                    print(f"[CLIENT] Received {action} notification for {username} (ID: {client_id})")
                    
                    if action == 'joined':
                        if client_id not in self.clients:
                            print(f"[CLIENT] Adding {username} to clients list")
                            self.clients[client_id] = {
                                'username': username,
                                'video_box': None
                            }
                            self._update_video_grid()
                            self._display_chat_message(f"*** {username} joined the session ***")
                        else:
                            print(f"[CLIENT] {username} already in clients list")
                        
                    elif action == 'left':
                        if client_id in self.clients:
                            user = self.clients[client_id]['username']
                            print(f"[CLIENT] Removing {user} from clients list")
                            del self.clients[client_id]
                            self._update_video_grid()
                            self._display_chat_message(f"*** {user} left the session ***")
                
                elif msg_type == 'file_notification':
                    file_id = message.get('file_id')
                    filename = message.get('filename')
                    filesize = message.get('size')
                    uploader = message.get('uploader')
                    
                    # Add to file list
                    size_mb = filesize / (1024 * 1024)
                    display_text = f"{filename} ({size_mb:.2f} MB) - from {uploader}"
                    self.file_listbox.insert(tk.END, display_text)
                    self._display_chat_message(f"*** {uploader} shared file: {filename} ***")
                    
        except queue.Empty:
            pass
        
    def _add_client_to_grid(self, client_id, username):
        """Add a client to the video grid"""
        if client_id not in self.clients:
            self.clients[client_id] = {
                'username': username,
                'video_box': None
            }
            self._update_video_grid()
    
    def _update_video_grid(self):
        """Update video grid layout based on number of clients"""
        # Clear existing grid
        for widget in self.video_container.winfo_children():
            widget.destroy()
        
        num_clients = len(self.clients)
        if num_clients == 0:
            return
        
        # Calculate grid dimensions
        cols = int(np.ceil(np.sqrt(num_clients)))
        rows = int(np.ceil(num_clients / cols))
        
        # Create grid
        client_list = list(self.clients.items())
        for idx, (client_id, client_info) in enumerate(client_list):
            row = idx // cols
            col = idx % cols
            
            # Create video box
            video_box = ClientVideoBox(
                self.video_container,
                client_id,
                client_info['username']
            )
            
            video_box.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=3,
                pady=3
            )
            
            # Store reference
            client_info['video_box'] = video_box
        
        # Configure grid weights
        for i in range(rows):
            self.video_container.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            self.video_container.grid_columnconfigure(i, weight=1)
            
    def update_gui(self):
        """Periodic GUI update - 30 FPS"""
        if not self.running:
            return
        
        try:
            # Process control messages
            self.process_control_messages()
            
            # Update video frames
            try:
                while True:
                    sender_id, frame = self.video_frames.get_nowait()
                    if sender_id in self.clients:
                        video_box = self.clients[sender_id].get('video_box')
                        if video_box:
                            video_box.update_frame(frame)
            except queue.Empty:
                pass
            
            # Process chat messages
            try:
                while True:
                    msg = self.chat_queue.get_nowait()
                    self._display_chat_message(msg)
            except queue.Empty:
                pass
                
        except Exception as e:
            print(f"Error in update_gui: {e}")
        
        # Schedule next update
        self.root.after(33, self.update_gui)  # ~30 FPS
        
    def toggle_video(self):
        """Toggle video on/off"""
        if not self.video_enabled:
            # Start video
            self.video_capture = VideoCapture(
                resolution=tuple(self.config['video']['resolution']),
                fps=self.config['video']['fps']
            )
            
            if self.video_capture.start():
                self.video_enabled = True
                self.video_btn.config(text="Stop Video", bg="#e74c3c")
                
                # Start video streamer
                self.video_streamer = VideoStreamer(
                    quality=self.config['video']['quality'],
                    client_id=self.client_id
                )
                self.video_streamer.setup_sender()
                
                # Start sending thread
                thread = threading.Thread(target=self.send_video_loop, daemon=True)
                thread.start()
                
                # Receiver already started in join_session
                
                self.status_bar.config(text="Video started")
            else:
                messagebox.showerror("Error", "Failed to start camera")
        else:
            # Stop video
            self.video_enabled = False
            if self.video_capture:
                self.video_capture.stop()
                self.video_capture = None
            if self.video_streamer:
                self.video_streamer.close()
                self.video_streamer = None
            
            self.video_btn.config(text="Start Video", bg="#3498db")
            self.status_bar.config(text="Video stopped")
            
            # Show placeholder for self
            if self.client_id in self.clients:
                video_box = self.clients[self.client_id].get('video_box')
                if video_box:
                    video_box._show_placeholder()
                    
    def send_video_loop(self):
        """Continuously send video frames"""
        server_addr = (self.server_ip, self.config['server']['video_port'])
        
        while self.video_enabled and self.session_active:
            frame = self.video_capture.read()
            if frame is not None:
                # Also update own video box
                if self.client_id in self.clients:
                    self.video_frames.put((self.client_id, frame.copy()))
                
                # Send to server
                self.video_streamer.send_frame(frame, server_addr)
            time.sleep(0.033)  # ~30 FPS
    
    def receive_video_loop(self):
        """Continuously receive video frames from server"""
        try:
            recv_streamer = VideoStreamer(client_id=self.client_id)
            recv_streamer.setup_receiver('0.0.0.0', self.config['server']['video_port'])
            
            print("[VIDEO_RECV] Video receiver started")
            
            while self.session_active:  # Keep receiving as long as session is active
                result = recv_streamer.receive_frame()
                if result:
                    sender_id, frame = result
                    if sender_id and sender_id != self.client_id:
                        print(f"[VIDEO_RECV] Received frame from {sender_id}")
                        self.video_frames.put((sender_id, frame))
                        
        except Exception as e:
            print(f"Error receiving video: {e}")
    
    def start_audio(self):
        """Start audio (unmuted by default)"""
        if self.audio_enabled:
            return
        
        # Initialize audio
        self.audio_capture = AudioCapture(
            self.config['audio']['sample_rate'],
            self.config['audio']['channels'],
            self.config['audio']['chunk_size']
        )
        self.audio_playback = AudioPlayback(
            self.config['audio']['sample_rate'],
            self.config['audio']['channels'],
            self.config['audio']['chunk_size']
        )
        
        if self.audio_capture.start() and self.audio_playback.start():
            self.audio_enabled = True
            self.audio_muted = False
            self.audio_btn.config(text="Mute", bg="#e74c3c")
            
            # Start audio streamer
            self.audio_streamer = AudioStreamer(client_id=self.client_id)
            self.audio_streamer.setup_sender()
            
            # Start sending thread
            thread = threading.Thread(target=self.send_audio_loop, daemon=True)
            thread.start()
            
            # Start receiving thread
            thread = threading.Thread(target=self.receive_audio_loop, daemon=True)
            thread.start()
            
    def stop_audio(self):
        """Stop audio"""
        self.audio_enabled = False
        if self.audio_capture:
            self.audio_capture.stop()
            self.audio_capture = None
        if self.audio_playback:
            self.audio_playback.stop()
            self.audio_playback = None
        if self.audio_streamer:
            self.audio_streamer.close()
            self.audio_streamer = None
    
    def toggle_audio_mute(self):
        """Toggle audio mute/unmute"""
        if not self.audio_enabled:
            self.start_audio()
        else:
            self.audio_muted = not self.audio_muted
            if self.audio_muted:
                self.audio_btn.config(text="Unmute", bg="#9b59b6")
                self.status_bar.config(text="Audio muted")
            else:
                self.audio_btn.config(text="Mute", bg="#e74c3c")
                self.status_bar.config(text="Audio unmuted")
    
    def send_audio_loop(self):
        """Continuously send audio chunks"""
        server_addr = (self.server_ip, self.config['server']['audio_port'])
        
        while self.audio_enabled and self.session_active:
            if not self.audio_muted:
                audio_data = self.audio_capture.read()
                if audio_data:
                    self.audio_streamer.send_audio(audio_data, server_addr)
    
    def receive_audio_loop(self):
        """Continuously receive and play mixed audio"""
        try:
            recv_streamer = AudioStreamer(client_id=self.client_id)
            recv_streamer.setup_receiver('0.0.0.0', self.config['server']['audio_port'])
            
            # Create audio playback for receiving (independent of sending)
            temp_playback = AudioPlayback(
                self.config['audio']['sample_rate'],
                self.config['audio']['channels'],
                self.config['audio']['chunk_size']
            )
            temp_playback.start()
            
            print("[AUDIO_RECV] Audio receiver started")
            
            while self.session_active:  # Keep receiving as long as session is active
                audio_data = recv_streamer.receive_audio()
                if audio_data:
                    temp_playback.play(audio_data)
                    
        except Exception as e:
            print(f"Error receiving audio: {e}")
    
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not self.screen_sharing:
            self.screen_sharing = True
            self.screen_btn.config(text="Stop Sharing", bg="#c0392b")
            self.status_bar.config(text="Screen sharing started")
            messagebox.showinfo("Screen Share", "Screen sharing feature coming soon!")
            # TODO: Implement screen capture and streaming
        else:
            self.screen_sharing = False
            self.screen_btn.config(text="Share Screen", bg="#e67e22")
            self.status_bar.config(text="Screen sharing stopped")
            
    def send_file(self):
        """Open file picker and send file"""
        filepath = filedialog.askopenfilename(title="Select file to send")
        if filepath:
            self.status_bar.config(text=f"Uploading {Path(filepath).name}...")
            # TODO: Implement file upload
            messagebox.showinfo("File Send", f"File sharing: {Path(filepath).name}\n(Upload in progress)")
    
    def download_file(self, event):
        """Download selected file"""
        selection = self.file_listbox.curselection()
        if selection:
            file_text = self.file_listbox.get(selection[0])
            messagebox.showinfo("Download", f"Downloading: {file_text}\n(Download in progress)")
            # TODO: Implement file download
    
    def send_chat_message(self):
        """Send chat message"""
        message = self.chat_input.get().strip()
        if message:
            # Display locally
            self._display_chat_message(f"{self.username}: {message}")
            self.chat_input.delete(0, tk.END)
            
            # TODO: Send to server via chat socket
            
    def _display_chat_message(self, message):
        """Display chat message"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = time.strftime("[%H:%M:%S]")
        self.chat_display.insert(tk.END, f"{timestamp} {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def _on_close(self):
        """Handle window close"""
        self.running = False
        self.session_active = False
        self.connected = False
        
        # Stop all services
        if self.video_enabled:
            self.toggle_video()
        if self.audio_enabled:
            self.stop_audio()
        
        # Close sockets
        self.disconnect_from_server()
        
        self.root.destroy()
        
    def run(self):
        """Start the application"""
        print("[CollaborationGUI] Starting Tkinter mainloop...")
        print("[CollaborationGUI] Main window should be visible now!")
        # Start Tkinter main loop
        self.root.mainloop()
        print("[CollaborationGUI] Mainloop ended")


def main():
    """Main entry point"""
    print("Starting Collaboration Suite GUI...")
    print("Creating login dialog...")
    
    # Show login dialog
    login = LoginDialog()
    print("Showing login dialog window...")
    username, server_ip = login.show()
    
    print(f"Login dialog closed. Username: {username}, Server: {server_ip}")
    
    if not username or not server_ip:
        print("No username or server IP provided. Exiting.")
        return
    
    print("Creating main application window...")
    # Create and run GUI
    app = CollaborationGUI(username, server_ip)
    print("Starting main application...")
    app.run()
    print("Application closed.")


if __name__ == "__main__":
    main()
