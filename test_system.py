#!/usr/bin/env python3
"""
Quick test script to verify server and client can start
"""
import sys
import socket
import time

def test_port_available(port, protocol='tcp'):
    """Check if port is available"""
    try:
        if protocol == 'tcp':
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.bind(('127.0.0.1', port))
        s.close()
        return True
    except:
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    required = ['cv2', 'PIL', 'numpy', 'pyaudio', 'tkinter']
    
    for module in required:
        try:
            if module == 'PIL':
                __import__('PIL.Image')
            else:
                __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - NOT FOUND")
            return False
    
    return True

def test_ports():
    """Test if required ports are available"""
    print("\nTesting port availability...")
    ports = [
        (5000, 'udp', 'Video'),
        (5001, 'udp', 'Audio'),
        (5002, 'tcp', 'Screen'),
        (5003, 'tcp', 'Chat'),
        (5004, 'tcp', 'File'),
        (5005, 'tcp', 'Control')
    ]
    
    all_available = True
    for port, protocol, name in ports:
        available = test_port_available(port, protocol)
        status = "✓ Available" if available else "✗ In use"
        print(f"  Port {port} ({protocol.upper()}) - {name}: {status}")
        if not available:
            all_available = False
    
    return all_available

def test_camera():
    """Test if camera is accessible"""
    print("\nTesting camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("  ✓ Camera accessible")
                return True
            else:
                print("  ✗ Camera opened but cannot read frames")
                return False
        else:
            print("  ✗ Cannot open camera")
            return False
    except Exception as e:
        print(f"  ✗ Camera error: {e}")
        return False

def test_audio():
    """Test if audio devices are accessible"""
    print("\nTesting audio...")
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        
        has_input = False
        has_output = False
        
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                has_input = True
            if info['maxOutputChannels'] > 0:
                has_output = True
        
        p.terminate()
        
        if has_input and has_output:
            print(f"  ✓ Audio devices found ({device_count} total)")
            return True
        else:
            print(f"  ✗ Missing audio devices (Input: {has_input}, Output: {has_output})")
            return False
    except Exception as e:
        print(f"  ✗ Audio error: {e}")
        return False

def main():
    print("="*60)
    print("Collaboration Suite - System Check")
    print("="*60)
    
    results = {
        'imports': test_imports(),
        'ports': test_ports(),
        'camera': test_camera(),
        'audio': test_audio()
    }
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name.capitalize()}: {status}")
    
    print("="*60)
    
    if all(results.values()):
        print("\n✅ All tests passed! System ready for collaboration.")
        print("\nNext steps:")
        print("  1. Start server: python run_server.py")
        print("  2. Start client: python gui_client.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running.")
        print("\nCommon fixes:")
        if not results['imports']:
            print("  • Install requirements: pip install -r requirements.txt")
        if not results['ports']:
            print("  • Close apps using ports 5000-5005")
            print("  • Or change ports in configs/config.json")
        if not results['camera']:
            print("  • Close other apps using the camera")
            print("  • Check camera permissions")
        if not results['audio']:
            print("  • Check audio device connections")
            print("  • Install audio drivers")
        return 1

if __name__ == "__main__":
    sys.exit(main())
