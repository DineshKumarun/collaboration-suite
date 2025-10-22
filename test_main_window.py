#!/usr/bin/env python3
"""
Test if the main GUI window creation works
"""
import tkinter as tk
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_main_window():
    """Test creating the main application window"""
    print("Creating main window...")
    
    root = tk.Tk()
    root.title("Collaboration Suite - Test")
    root.geometry("1400x900")
    
    print("Window created, adding widgets...")
    
    # Add a simple label
    label = tk.Label(root, text="Main Application Window Test", font=("Arial", 24))
    label.pack(pady=50)
    
    # Add close button
    btn = tk.Button(root, text="Close", command=root.destroy, font=("Arial", 14))
    btn.pack(pady=20)
    
    print("Widgets added, starting mainloop...")
    print("Window should be visible now!")
    
    root.mainloop()
    
    print("Window closed")

if __name__ == "__main__":
    test_main_window()
