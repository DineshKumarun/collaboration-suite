#!/usr/bin/env python3
"""
Collaboration Suite - Easy Launcher
This script will guide you through starting the application
"""
import subprocess
import sys
import os

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_banner():
    print("=" * 70)
    print(" "*20 + "🎥 COLLABORATION SUITE 🎥")
    print("=" * 70)
    print()

def main():
    clear_screen()
    print_banner()
    
    print("Welcome to the LAN Collaboration Suite!\n")
    print("This launcher will help you start the application.\n")
    print("="*70)
    print("\n📋 Instructions:")
    print("   1. A login window will appear")
    print("   2. Enter your username (e.g., 'Sanjeet')")
    print("   3. Enter server IP address:")
    print("      - Use '127.0.0.1' if server is on same machine")
    print("      - Use actual IP (e.g., '192.168.1.100') for network")
    print("   4. Click 'Connect' button")
    print("   5. Main application window will open")
    print("   6. Click 'Join Session' to start")
    print("\n" + "="*70)
    
    input("\nPress ENTER to start the GUI application...")
    
    print("\n🚀 Launching GUI...")
    print("   (Look for the login window on your screen)\n")
    
    try:
        # Run the GUI client
        subprocess.run([sys.executable, "gui_client.py"], check=True)
        print("\n✅ Application closed normally.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Application exited with error code {e.returncode}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
