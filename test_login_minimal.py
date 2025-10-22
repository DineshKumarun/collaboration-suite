#!/usr/bin/env python3
"""
Minimal test of the login dialog
"""
import tkinter as tk

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
            tk.messagebox.showerror("Error", "Please enter a username")
            return
        
        if not server_ip:
            tk.messagebox.showerror("Error", "Please enter server IP")
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


def main():
    """Main entry point"""
    print("Starting test...")
    print("Creating login dialog...")
    
    # Show login dialog
    login = LoginDialog()
    print("Showing login dialog window...")
    username, server_ip = login.show()
    
    print(f"Login dialog closed. Username: {username}, Server: {server_ip}")
    
    if not username or not server_ip:
        print("No username or server IP provided. Exiting.")
        return
    
    print(f"Success! Would connect to {server_ip} as {username}")


if __name__ == "__main__":
    main()
