# 🎥 LAN Collaboration Suite

A comprehensive multi-user video conferencing application with audio, chat, screen sharing, and file transfer capabilities.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🌟 Features

### ✨ Core Features

- 🎥 **Multi-User Video Conferencing** - See everyone in a dynamic grid layout
- 🎤 **Multi-User Audio** - Server-mixed audio for clear communication
- 💬 **Group Text Chat** - Real-time messaging with timestamps
- 📁 **File Sharing** - Upload and download files with all participants
- 🖥️ **Screen Sharing** - Share your screen or presentations (infrastructure ready)
- 👥 **Session Management** - Join/leave sessions with live updates

### 🎯 What Makes It Unique

- **Client-Server Architecture** - Centralized server for easy network management
- **Multi-Port Design** - Separate services on different ports (UDP for media, TCP for data)
- **Server-Side Audio Mixing** - Efficient bandwidth usage
- **Dynamic Video Grid** - Automatically adjusts layout for 1-16+ users
- **Professional GUI** - Modern, intuitive interface with color-coded controls
- **Real-Time Updates** - Live notifications for joins, leaves, and file shares

## 🖥️ What It Looks Like

### Login Screen
```
┌─────────────────────────────┐
│  LAN Collaboration Suite    │
│                             │
│  Username: [Sanjeet____]    │
│  Server IP: [127.0.0.1_]    │
│                             │
│       [ Connect ]           │
└─────────────────────────────┘
```

### Main Application
```
┌───────────────────────────────────────────────────────────┐
│ 👤 Sanjeet  [Join] [Leave] [Video] [Mute] [Screen] [File]│
├────────────────────────────────┬──────────────────────────┤
│                                │  💬 Group Chat           │
│        Video Grid              │  ┌──────────────────┐    │
│   ┌──────┬──────┬──────┐      │  │[14:30] Sanjeet:  │    │
│   │You   │John  │Alice │      │  │  Hello everyone! │    │
│   │      │      │      │      │  │[14:31] John:     │    │
│   └──────┴──────┴──────┘      │  │  Hi!             │    │
│   ┌──────┬──────┬──────┐      │  └──────────────────┘    │
│   │Bob   │      │      │      │  [Type message...] [Send]│
│   │      │      │      │      │                          │
│   └──────┴──────┴──────┘      │  📁 Shared Files         │
│                                │  • slides.pdf (2.5 MB)   │
│                                │  • report.docx (0.8 MB)  │
└────────────────────────────────┴──────────────────────────┘
│ Status: Connected to 192.168.1.100                        │
└───────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Requirements:
- opencv-python
- numpy
- pyaudio
- Pillow
- mss

### 2. Test Your System

```bash
python test_system.py
```

This checks:
- ✅ All required libraries
- ✅ Port availability (5000-5005)
- ✅ Camera access
- ✅ Audio devices

### 3. Start the Server

```bash
python run_server.py
```

You'll see:
```
Starting Collaboration Server...
Control server started
Video relay started
Audio relay started with mixing
Screen sharing server started
File server started
Chat server started
Server running on 0.0.0.0
```

### 4. Start Client(s)

```bash
python gui_client.py
```

Or use the launcher:
```bash
python run_client.py
```

### 5. Connect and Join

1. Enter your **username**
2. Enter **server IP**:
   - `127.0.0.1` for same machine
   - `192.168.x.x` for local network
3. Click **Connect**
4. Click **Join Session**
5. Start collaborating! 🎉

## 📖 Documentation

### Comprehensive Guides

- 📘 **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage instructions
  - Feature walkthroughs
  - Troubleshooting
  - Network setup
  - Performance tuning

- 🏗️ **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - Multi-port design
  - Data flow diagrams
  - Threading model
  - Protocol specifications

- ✅ **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What's implemented
  - Feature checklist
  - Technical details
  - Testing guide

## 🎛️ Architecture Overview

### Multi-Port Services

```
        +----------------+
        |   SERVER       |
        |  Port 5000 UDP | ← Video
        |  Port 5001 UDP | ← Audio (with mixing)
        |  Port 5002 TCP | ← Screen sharing
        |  Port 5003 TCP | ← Group chat
        |  Port 5004 TCP | ← File transfer
        |  Port 5005 TCP | ← Session control
        +----------------+
           /   |   |   \
          /    |   |    \
   [Client1] [Client2] [Client3] [Client4]
```

### Communication Flow

**Video**: Client → JPEG compress → UDP → Server → Relay → All clients → Decompress → Display

**Audio**: Clients → Capture → UDP → Server → Mix → Broadcast → Clients → Play

**Chat**: Client → JSON → TCP → Server → Broadcast → Clients → Display

**Files**: Client → Upload → Server stores → Notify all → Clients can download

## 🎨 Features In Detail

### 🎥 Video Conferencing

- **Multi-user grid** - 2x2, 3x3, 4x4+ layouts
- **640x480 @ 30fps** - Smooth video (configurable)
- **JPEG compression** - Quality vs. bandwidth balance
- **Dynamic layout** - Adapts to participant count
- **Placeholders** - Shows when user has no video

### 🎤 Audio Conferencing

- **Server-side mixing** - Efficient bandwidth
- **44.1kHz, 16-bit** - Clear audio quality
- **Mute/Unmute** - Control your microphone
- **No echo** - Your voice excluded from mix
- **Low latency** - ~20ms mixing interval

### 💬 Group Chat

- **Real-time messaging** - Instant delivery
- **Timestamps** - [HH:MM:SS] on every message
- **System messages** - Join/leave notifications
- **Auto-scroll** - Always see latest messages

### 📁 File Sharing

- **Upload to server** - Shared with all
- **Metadata display** - Filename, size, uploader
- **Download on demand** - Double-click to download
- **Notifications** - Alert when new file shared

### 👥 Session Management

- **Join/Leave** - One-click session control
- **Client list sync** - Real-time participant tracking
- **Auto-connect** - Video and audio start automatically
- **Graceful disconnect** - Clean shutdown

## ⚙️ Configuration

Edit `configs/config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "video_port": 5000,
    "audio_port": 5001,
    "screen_port": 5002,
    "chat_port": 5003,
    "file_port": 5004,
    "control_port": 5005
  },
  "video": {
    "resolution": [640, 480],
    "fps": 30,
    "quality": 80
  },
  "audio": {
    "sample_rate": 44100,
    "channels": 1,
    "chunk_size": 2048
  }
}
```

### Performance Presets

**High Quality (LAN):**
```json
{"video": {"resolution": [1280, 720], "fps": 30, "quality": 90}}
```

**Balanced (Default):**
```json
{"video": {"resolution": [640, 480], "fps": 30, "quality": 80}}
```

**Low Bandwidth (Internet):**
```json
{"video": {"resolution": [480, 360], "fps": 20, "quality": 60}}
```

## 🔧 Troubleshooting

### Common Issues

**"Cannot connect to server"**
- ✅ Verify server is running
- ✅ Check IP address
- ✅ Ensure firewall allows ports 5000-5005

**"Failed to start camera"**
- ✅ Close other apps using camera
- ✅ Check camera permissions
- ✅ Verify `/dev/video0` exists (Linux)

**"No audio"**
- ✅ Check system volume
- ✅ Use headphones (prevents echo)
- ✅ Verify audio devices: `python test_system.py`

**"Laggy video"**
- ✅ Close other network apps
- ✅ Lower quality/fps in config
- ✅ Check network bandwidth

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

## 🌐 Network Setup

### Same Machine (Testing)
```bash
Server: python run_server.py
Client: Enter 127.0.0.1
```

### Local Network (LAN)
```bash
# Find server IP
hostname -I  # Linux/Mac
ipconfig     # Windows

# Example: 192.168.1.100
# All clients use this IP
```

### Internet (Port Forwarding)
1. Forward ports 5000-5005 on router
2. Use public IP for server address
3. Consider VPN or cloud server

## 📊 Performance

### Bandwidth (per client, 4-user session)

- **Video**: ~10 Mbps (3 other streams)
- **Audio**: ~200 kbps (mixed stream)
- **Total**: ~10.2 Mbps

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 2 GB
- Network: 1 Mbps
- Webcam + Microphone

**Recommended:**
- CPU: Quad-core 2.5 GHz+
- RAM: 4 GB+
- Network: 10 Mbps+
- HD Webcam + Headset

## 🧪 Testing

### System Check
```bash
python test_system.py
```

### Run Tests
```bash
cd tests
python run_all_tests.py
```

### Manual Test
```bash
# Terminal 1
python run_server.py

# Terminal 2
python gui_client.py
# Username: Alice, Server: 127.0.0.1

# Terminal 3
python gui_client.py
# Username: Bob, Server: 127.0.0.1
```

## 📁 Project Structure

```
collaboration-suite/
├── src/
│   ├── server.py              # Main server with 6 services
│   ├── client.py              # CLI client
│   ├── video_conferencing/    # Video capture & streaming
│   ├── audio_conferencing/    # Audio capture, mixing & streaming
│   ├── text_chat/             # Chat management
│   ├── screen_sharing/        # Screen capture & streaming
│   ├── file_sharing/          # File transfer
│   └── utils/                 # Network utilities, compression
├── gui_client.py              # GUI application (main)
├── run_server.py              # Server launcher
├── run_client.py              # CLI client launcher
├── test_system.py             # System check script
├── configs/
│   └── config.json            # Configuration
├── tests/                     # Test suite
├── docs/                      # Additional documentation
├── ARCHITECTURE.md            # Architecture documentation
├── USER_GUIDE.md              # User manual
├── IMPLEMENTATION_SUMMARY.md  # Implementation details
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔮 Future Enhancements

- [ ] Screen capture implementation
- [ ] File transfer with progress bars
- [ ] Recording sessions
- [ ] Private messaging
- [ ] User permissions/admin controls
- [ ] Encryption (TLS/SSL)
- [ ] Adaptive video quality
- [ ] Mobile app (Android/iOS)
- [ ] WebRTC integration
- [ ] Cloud deployment

## 🤝 Contributing

Contributions welcome! Areas to improve:

1. **Screen Sharing** - Complete the capture implementation
2. **File Transfer** - Add progress bars and resume capability
3. **Security** - Implement encryption
4. **Quality** - Adaptive bitrate for video
5. **Mobile** - Create mobile clients

## 📄 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

Built with:
- **OpenCV** - Video capture and processing
- **PyAudio** - Audio capture and playback
- **Tkinter** - GUI framework
- **NumPy** - Audio mixing and processing
- **Pillow** - Image handling

## 📞 Support

- 📖 Read the [User Guide](USER_GUIDE.md)
- 🏗️ Check [Architecture Docs](ARCHITECTURE.md)
- 🔍 Run `python test_system.py` for diagnostics
- 🐛 Review server/client logs for errors

## 🎯 Usage Examples

### Example 1: Team Meeting
```bash
# Start server
python run_server.py

# 5 team members connect
# All enable video and audio
# Share screen for presentation
# Chat for questions
# Share files (agenda, notes)
```

### Example 2: Remote Class
```bash
# Teacher runs server
# Students connect (10-20 users)
# Teacher shares screen (slides)
# Students mute by default
# Chat for questions
# Share handouts via files
```

### Example 3: Social Call
```bash
# Friend runs server
# 2-4 friends connect
# Video chat
# Share photos/videos
# Casual conversation
```

---

## 🚀 Get Started Now!

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test
python test_system.py

# 3. Run server
python run_server.py

# 4. Run client
python gui_client.py

# 5. Collaborate! 🎉
```

**Enjoy your collaboration session!** 🎥🎤💬📁
