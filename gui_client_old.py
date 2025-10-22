"""
GUI-Based Collaboration Client with Video Grid
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
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video_conferencing import VideoCapture, VideoStreamer
from src.audio_conferencing import AudioCapture, AudioPlayback, AudioStreamer, AudioMixer
from src.text_chat import ChatManager, MessageHandler
from src.screen_sharing import ScreenCapture, ScreenStreamer
from src.file_sharing import FileTransfer


class LoginDialog:
    """Initial dialog to get username and server IP"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Join Collaboration Session")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        self.username = None
        self.server_ip = None
        
        self._create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
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
        self.root.mainloop()
        self.root.destroy()
        return self.username, self.server_ip


class ClientVideoBox(tk.Frame):
    """Video box for each client in the grid"""
    
    def __init__(self, parent, client_id, username):
        super().__init__(parent, bg="#2c3e50", relief=tk.RAISED, borderwidth=2)
        
        self.client_id = client_id
        self.username = username
        self.video_label = None
        self.name_label = None
        self.placeholder_image = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Name label at top
        self.name_label = tk.Label(
            self,
            text=self.username,
            bg="#34495e",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=5
        )
        self.name_label.pack(fill=tk.X)
        
        # Video display area
        self.video_label = tk.Label(self, bg="#000000")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Create placeholder
        self._show_placeholder()
        
    def _show_placeholder(self):
        """Show placeholder when no video"""
        # Create a simple colored placeholder
        width, height = 320, 240
        placeholder = np.zeros((height, width, 3), dtype=np.uint8)
        placeholder[:, :] = [44, 62, 80]  # Dark blue-gray
        
        # Add text
        cv2.putText(
            placeholder,
            self.username[:15],
            (10, height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2
        )
        cv2.putText(
            placeholder,
            "No Video",
            (10, height // 2 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
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
            # Resize frame to fit box
            height, width = frame.shape[:2]
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()
            
            if label_width > 1 and label_height > 1:
                # Calculate scaling to maintain aspect ratio
                scale_w = label_width / width
                scale_h = label_height / height
                scale = min(scale_w, scale_h)
                
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB for Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
        except Exception as e:
            print(f"Error updating frame for {self.username}: {e}")


class CollaborationGUI:
    """Main collaboration GUI with video grid"""
    
    def __init__(self, username, server_ip):
        self.username = username
        self.server_ip = server_ip
        self.client_id = str(uuid.uuid4())
        
        # Connection state
        self.connected = False
        self.running = True
        
        # Sockets and connections
        self.control_socket = None
        
        # Feature states
        self.video_enabled = False
        self.audio_enabled = False
        self.screen_sharing = False
        
        # Components
        self.video_capture = None
        self.audio_capture = None
        self.audio_playback = None
        self.audio_mixer = AudioMixer()
        self.chat_manager = None
        
        # Client tracking
        self.clients = {}  # client_id -> {username, video_box}
        self.video_frames = {}  # client_id -> frame
        
        # Queues
        self.chat_queue = queue.Queue()
        
        # Load config
        self.load_config()
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title(f"Collaboration Suite - {username}")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._create_gui()
        
    def load_config(self):
        """Load configuration"""
        self.config = {
            "server": {
                "video_port": 5000,
                "audio_port": 5001,
                "chat_port": 5003,
                "control_port": 5005
            },
            "video": {"resolution": [640, 480], "fps": 30, "quality": 80},
            "audio": {"sample_rate": 44100, "channels": 1, "chunk_size": 2048}
        }
        
    def _create_gui(self):
        """Create main GUI layout"""
        # Top control panel
        control_frame = tk.Frame(self.root, bg="#34495e", height=60)
        control_frame.pack(fill=tk.X, side=tk.TOP)
        control_frame.pack_propagate(False)
        
        # Control buttons
        btn_config = {
            'font': ("Arial", 10, "bold"),
            'padx': 15,
            'pady': 8,
            'relief': tk.RAISED,
            'borderwidth': 2
        }
        
        btn_frame = tk.Frame(control_frame, bg="#34495e")
        btn_frame.pack(pady=10)
        
        self.video_btn = tk.Button(
            btn_frame,
            text="📹 Start Video",
            command=self.toggle_video,
            bg="#3498db",
            fg="white",
            **btn_config
        )
        self.video_btn.pack(side=tk.LEFT, padx=5)
        
        self.audio_btn = tk.Button(
            btn_frame,
            text="🎤 Start Audio",
            command=self.toggle_audio,
            bg="#9b59b6",
            fg="white",
            **btn_config
        )
        self.audio_btn.pack(side=tk.LEFT, padx=5)
        
        self.screen_btn = tk.Button(
            btn_frame,
            text="🖥️ Share Screen",
            command=self.toggle_screen_share,
            bg="#e67e22",
            fg="white",
            **btn_config
        )
        self.screen_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_btn = tk.Button(
            btn_frame,
            text="📁 Send File",
            command=self.send_file,
            bg="#27ae60",
            fg="white",
            **btn_config
        )
        self.file_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video grid (left side - 70%)
        self.video_container = tk.Frame(main_frame, bg="#1a1a1a")
        self.video_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Chat panel (right side - 30%)
        chat_frame = tk.Frame(main_frame, bg="#ecf0f1", width=350)
        chat_frame.pack(side=tk.RIGHT, fill=tk.Y)
        chat_frame.pack_propagate(False)
        
        # Chat title
        chat_title = tk.Label(
            chat_frame,
            text="Chat",
            bg="#34495e",
            fg="white",
            font=("Arial", 12, "bold"),
            pady=10
        )
        chat_title.pack(fill=tk.X)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg="white"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat input
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
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Connecting...",
            bg="#2c3e50",
            fg="white",
            anchor=tk.W,
            padx=10
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def run(self):
        """Start the application"""
        # Connect to server
        if self.connect_to_server():
            self.status_bar.config(text=f"Connected to {self.server_ip}")
            
            # Start update loop
            self.update_gui()
            
            # Start Tkinter main loop
            self.root.mainloop()
        else:
            messagebox.showerror("Connection Error", "Failed to connect to server")
            self.root.destroy()
            
    def connect_to_server(self):
        """Connect to collaboration server"""
        # TODO: Implement server connection
        # For now, create local client entry
        self.clients[self.client_id] = {
            'username': self.username,
            'video_box': None
        }
        self.connected = True
        self._update_video_grid()
        return True
        
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
                padx=2,
                pady=2
            )
            
            # Store reference
            client_info['video_box'] = video_box
        
        # Configure grid weights for equal distribution
        for i in range(rows):
            self.video_container.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            self.video_container.grid_columnconfigure(i, weight=1)
            
    def update_gui(self):
        """Periodic GUI update"""
        if not self.running:
            return
        
        try:
            # Update video frames
            if self.video_enabled and self.video_capture:
                frame = self.video_capture.read()
                if frame is not None:
                    # Update own video box
                    if self.client_id in self.clients:
                        video_box = self.clients[self.client_id].get('video_box')
                        if video_box:
                            video_box.update_frame(frame)
            
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
                self.video_btn.config(text="📹 Stop Video", bg="#e74c3c")
                self.status_bar.config(text="Video started")
            else:
                messagebox.showerror("Error", "Failed to start camera")
        else:
            # Stop video
            if self.video_capture:
                self.video_capture.stop()
                self.video_capture = None
            self.video_enabled = False
            self.video_btn.config(text="📹 Start Video", bg="#3498db")
            self.status_bar.config(text="Video stopped")
            
            # Show placeholder
            if self.client_id in self.clients:
                video_box = self.clients[self.client_id].get('video_box')
                if video_box:
                    video_box._show_placeholder()
                    
    def toggle_audio(self):
        """Toggle audio on/off"""
        if not self.audio_enabled:
            # Start audio
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
                self.audio_btn.config(text="🎤 Stop Audio", bg="#e74c3c")
                self.status_bar.config(text="Audio started")
            else:
                messagebox.showerror("Error", "Failed to start audio")
        else:
            # Stop audio
            if self.audio_capture:
                self.audio_capture.stop()
                self.audio_capture = None
            if self.audio_playback:
                self.audio_playback.stop()
                self.audio_playback = None
            self.audio_enabled = False
            self.audio_btn.config(text="🎤 Start Audio", bg="#9b59b6")
            self.status_bar.config(text="Audio stopped")
            
    def toggle_screen_share(self):
        """Toggle screen sharing"""
        if not self.screen_sharing:
            self.screen_sharing = True
            self.screen_btn.config(text="🖥️ Stop Sharing", bg="#e74c3c")
            self.status_bar.config(text="Screen sharing started")
            # TODO: Implement screen capture and streaming
        else:
            self.screen_sharing = False
            self.screen_btn.config(text="🖥️ Share Screen", bg="#e67e22")
            self.status_bar.config(text="Screen sharing stopped")
            
    def send_file(self):
        """Open file picker and send file"""
        filepath = filedialog.askopenfilename(title="Select file to send")
        if filepath:
            # TODO: Show recipient selection and send file
            messagebox.showinfo("File Send", f"Sending {filepath}")
            
    def send_chat_message(self):
        """Send chat message"""
        message = self.chat_input.get().strip()
        if message:
            # Add to display
            self._display_chat_message(f"{self.username}: {message}")
            self.chat_input.delete(0, tk.END)
            # TODO: Send to server
            
    def _display_chat_message(self, message):
        """Display chat message"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
    def _on_close(self):
        """Handle window close"""
        self.running = False
        
        # Stop all services
        if self.video_capture:
            self.video_capture.stop()
        if self.audio_capture:
            self.audio_capture.stop()
        if self.audio_playback:
            self.audio_playback.stop()
        
        self.root.destroy()


def main():
    """Main entry point"""
    # Show login dialog
    login = LoginDialog()
    username, server_ip = login.show()
    
    if not username or not server_ip:
        return
    
    # Create and run GUI
    app = CollaborationGUI(username, server_ip)
    app.run()


if __name__ == "__main__":
    main()
