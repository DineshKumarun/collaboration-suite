#!/usr/bin/env python3
"""
Diagnostic script for GUI issues
"""
import sys
import os

print("="*60)
print("GUI Diagnostics")
print("="*60)

# Check Python version
print(f"Python version: {sys.version}")

# Check DISPLAY
display = os.environ.get('DISPLAY', 'NOT SET')
print(f"DISPLAY: {display}")

# Test tkinter import
print("\n1. Testing tkinter import...")
try:
    import tkinter as tk
    print("   ✓ tkinter imported successfully")
except Exception as e:
    print(f"   ✗ tkinter import failed: {e}")
    sys.exit(1)

# Test creating a simple window
print("\n2. Testing simple window creation...")
try:
    root = tk.Tk()
    root.withdraw()  # Hide window
    print("   ✓ Window created successfully")
    root.destroy()
except Exception as e:
    print(f"   ✗ Window creation failed: {e}")
    sys.exit(1)

# Test visible window
print("\n3. Testing visible window (will appear for 2 seconds)...")
try:
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x150")
    
    label = tk.Label(root, text="GUI Test - This window will close in 2 seconds")
    label.pack(pady=20)
    
    # Schedule window to close
    root.after(2000, root.destroy)
    
    print("   Creating visible window...")
    print("   (Window should appear now)")
    root.mainloop()
    print("   ✓ Window displayed and closed successfully")
except Exception as e:
    print(f"   ✗ Visible window test failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All GUI tests passed! ✓")
print("="*60)
print("\nYour system can display tkinter GUIs.")
print("If gui_client.py still doesn't work, there may be an")
print("issue with the application code itself.")
