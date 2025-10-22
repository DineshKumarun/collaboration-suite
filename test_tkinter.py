#!/usr/bin/env python3
"""
Simple test to verify tkinter GUI works
"""
import tkinter as tk

def test_simple_gui():
    """Test basic tkinter window"""
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    label = tk.Label(root, text="If you see this, tkinter works!", font=("Arial", 12))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack()
    
    print("Window created. If you don't see it, there might be a display issue.")
    root.mainloop()
    print("Window closed.")

if __name__ == "__main__":
    test_simple_gui()
