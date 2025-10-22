# Quick Start Guide

## LAN-Based Collaboration Suite

### Starting the System

#### 1. Start the Server (One machine on LAN)
```bash
cd /home/dk-zorin/Projects/collaboration-suite
python3 src/server.py
```

#### 2. Start GUI Clients (Each participant)
```bash
python3 gui_client.py
```

- Enter your name
- Enter server IP (e.g., 192.168.1.100)
- Click Connect

### Using the Application

#### Video
- Click "📹 Start Video" to turn on camera
- Your video appears in your box
- All clients see your video

#### Audio  
- Click "🎤 Start Audio" to turn on microphone
- Speak - all clients hear you
- Multiple people can speak simultaneously (audio overlaps)

#### Screen Share
- Click "🖥️ Share Screen" to share your screen
- Your screen appears in your video box
- All clients see your screen

#### Chat
- Type message in chat box
- Press Enter or click Send
- All clients see the message

#### File Sharing
- Click "📁 Send File"
- Select file
- Choose recipient
- File transfers to selected client

### Troubleshooting

#### Can't connect?
```bash
# Check server IP
ip addr show

# Test connectivity
ping <server_ip>

# Check if server is running
ps aux | grep server.py
```

#### Camera not working?
```bash
# Check camera
ls /dev/video*

# Test camera
ffplay /dev/video0

# Kill hung processes
pkill -f client.py
```

#### No audio?
- Check volume/microphone in system settings
- Verify ALSA/PulseAudio is working
- Try adjusting chunk_size in code

### Network Setup

#### Find Your IP (Server Machine)
```bash
# Linux
ip addr show | grep inet

# Or
hostname -I
```

#### Firewall Rules (if needed)
```bash
# Allow ports 5000-5005
sudo ufw allow 5000:5005/tcp
sudo ufw allow 5000:5005/udp
```

### Current Status

✅ **Working**:
- GUI login and main window
- Video grid layout (auto-resizes)
- Video capture and local display
- Chat interface
- Control buttons

🚧 **In Progress**:
- Network streaming (video/audio to server)
- Multi-client synchronization
- Audio mixing
- Screen sharing implementation
- File transfer GUI

### Tips

- **Best Performance**: Use wired Ethernet instead of WiFi
- **Low Bandwidth**: Reduce video resolution in config
- **Audio Quality**: Increase chunk_size for stability
- **Multiple Cameras**: Change device_id in VideoCapture()

### System Requirements

- **Network**: LAN (100 Mbps recommended)
- **Python**: 3.8+
- **Camera**: USB webcam or built-in
- **Audio**: Microphone and speakers
- **RAM**: 2GB minimum, 4GB recommended
- **OS**: Linux (tested), Windows/Mac (should work)
