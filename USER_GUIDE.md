# 🚀 Collaboration Suite - User Guide

## Quick Start

### 1. Start the Server

On one machine (or VM):

```bash
cd /home/dk-zorin/Projects/collaboration-suite
python run_server.py
```

You should see:
```
Starting Collaboration Server...
Control server started
Video relay started
Audio relay started with mixing
Screen sharing server started
File server started
Chat server started
Server running on 0.0.0.0
Control Port: 5005
Video Port: 5000
Audio Port: 5001
Chat Port: 5003
File Port: 5004
```

### 2. Start the GUI Client

On client machines:

```bash
python gui_client.py
```

Or:

```bash
python run_client.py
```

### 3. Login

A dialog will appear:
- **Username**: Enter your name (e.g., "Sanjeet")
- **Server IP**: 
  - Use `127.0.0.1` if running on same machine
  - Use server's LAN IP (e.g., `192.168.1.100`) for network
  - Find server IP: `hostname -I` or `ip addr show`

Click **Connect**.

### 4. Join Session

Click the **"Join Session"** button in the top bar.

The application will:
- ✅ Connect to server
- ✅ Auto-start video
- ✅ Auto-start audio (unmuted)
- ✅ Show video grid with all participants

## 🎥 Using the Features

### Video Conferencing

**Start Video:**
- Click **"Start Video"** (auto-starts when joining)
- Your webcam feed appears in grid
- Other users see your video

**Stop Video:**
- Click **"Stop Video"**
- Your box shows placeholder
- Camera is released

**What You See:**
- **Your Video**: Top-left or first position (labeled "You")
- **Other Users**: Arranged in grid (2x2, 3x3, etc.)
- **No Video**: Gray placeholder with username

### Audio Conferencing

**Unmute (Speak):**
- Audio starts unmuted when joining
- Button shows **"Mute"** (red) when you can speak
- Your microphone is captured and sent to server

**Mute:**
- Click **"Mute"** button
- Button shows **"Unmute"** (purple)
- Your microphone stops sending audio

**What You Hear:**
- Mixed audio from all other participants
- Server mixes all voices together
- You don't hear yourself (no echo)

### Group Chat

**Send Message:**
1. Type in text box at bottom of chat panel
2. Press **Enter** or click **"Send"**
3. Message appears for everyone

**Message Format:**
```
[14:30:25] Sanjeet: Hello everyone!
[14:30:28] John: Hi Sanjeet!
[14:30:30] *** Alice joined the session ***
```

**Features:**
- Timestamp on every message
- Username identification
- System messages (join/leave)
- Auto-scroll to latest

### Screen Sharing

**Share Your Screen:**
1. Click **"Share Screen"**
2. (Currently shows "coming soon" - feature in development)

**View Shared Screen:**
- Replaces video grid when someone shares
- Shows full-screen presentation/demo

### File Sharing

**Send File:**
1. Click **"Send File"**
2. Select file from your computer
3. File uploads to server
4. All participants notified

**Download File:**
1. See files in **"Shared Files"** panel
2. Double-click file name
3. Choose save location
4. File downloads

**File List Shows:**
```
presentation.pdf (2.5 MB) - from Sanjeet
report.docx (0.8 MB) - from John
```

## 🎛️ Controls Reference

### Top Bar Buttons

| Button | Default State | Function |
|--------|---------------|----------|
| **Join Session** | Enabled | Connect to server and start collaboration |
| **Leave Session** | Disabled | Disconnect and stop all services |
| **Start Video** | Disabled until joined | Toggle webcam on/off |
| **Mute / Unmute** | Shows "Mute" when joined | Toggle microphone on/off |
| **Share Screen** | Disabled until joined | Share your screen with others |
| **Send File** | Disabled until joined | Upload a file to share |

### Status Bar

Shows current state:
- `Not connected - Click 'Join Session' to start`
- `Connected to 192.168.1.100`
- `Video started`
- `Audio muted`
- `Uploading file...`

## 🔧 Troubleshooting

### Cannot Connect to Server

**Problem**: "Connection Error: Failed to connect to server"

**Solutions:**
1. Verify server is running
2. Check server IP address
3. Ensure firewall allows ports 5000-5005
4. Ping server: `ping <server_ip>`

**Open Firewall Ports (Linux):**
```bash
sudo ufw allow 5000:5005/tcp
sudo ufw allow 5000:5001/udp
```

### No Video Showing

**Problem**: Camera not working or black screen

**Solutions:**
1. Check camera permissions
2. Close other apps using camera
3. Restart client
4. Check `/dev/video0` exists (Linux)

**Test Camera:**
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### No Audio / Echo

**Problem**: Cannot hear others or hearing echo

**Solutions:**
1. Check system volume
2. Verify microphone/speaker in system settings
3. Use headphones (prevents echo)
4. Click Mute/Unmute to reset

**Test Audio:**
```bash
python -c "import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())"
```

### Laggy Video

**Problem**: Video is choppy or delayed

**Solutions:**
1. Close other network apps
2. Reduce number of participants
3. Check network bandwidth
4. Lower video quality in config

**Edit `configs/config.json`:**
```json
{
  "video": {
    "quality": 60,  // Lower = smaller files
    "fps": 20       // Lower = less bandwidth
  }
}
```

### Chat Not Working

**Problem**: Messages not appearing

**Solutions:**
1. Check chat connection in server logs
2. Restart client
3. Verify TCP port 5003 is open

## 🌐 Network Setup

### Same Machine (Testing)

Server IP: `127.0.0.1`
- Both server and client on same PC
- No network configuration needed

### Local Network (LAN)

**Find Server IP:**
```bash
# Linux/Mac
hostname -I
# Or
ip addr show | grep inet

# Windows
ipconfig
```

**Example**: Server IP is `192.168.1.100`
- All clients use this IP
- Must be on same network (WiFi/Ethernet)

### Port Forwarding (Internet)

To allow clients over internet:

1. **Router Port Forwarding:**
   - Forward ports 5000-5005 to server's local IP
   - Both TCP and UDP

2. **Server IP:**
   - Use public IP (find at https://whatismyipaddress.com)
   - Or use Dynamic DNS service

3. **Firewall:**
   - Allow incoming connections on ports 5000-5005

## ⚙️ Configuration

Edit `configs/config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",      // Listen on all interfaces
    "video_port": 5000,      // Video UDP port
    "audio_port": 5001,      // Audio UDP port
    "screen_port": 5002,     // Screen TCP port
    "chat_port": 5003,       // Chat TCP port
    "file_port": 5004,       // File TCP port
    "control_port": 5005     // Control TCP port
  },
  "video": {
    "resolution": [640, 480], // Camera resolution
    "fps": 30,                // Frames per second
    "quality": 80             // JPEG quality (1-100)
  },
  "audio": {
    "sample_rate": 44100,     // Audio sample rate
    "channels": 1,            // Mono audio
    "chunk_size": 2048        // Buffer size
  }
}
```

## 📊 Performance Tips

### For Better Video Quality:
- Increase `quality` to 90-95
- Increase `resolution` to [1280, 720]
- Requires more bandwidth

### For Lower Bandwidth:
- Decrease `quality` to 50-60
- Decrease `fps` to 15-20
- Lower `resolution` to [320, 240]

### For Better Audio:
- Increase `sample_rate` to 48000
- Set `channels` to 2 (stereo)
- Requires 2x bandwidth

### Optimal Settings (LAN):
```json
{
  "video": {"resolution": [640, 480], "fps": 30, "quality": 80},
  "audio": {"sample_rate": 44100, "channels": 1}
}
```

### Optimal Settings (Internet):
```json
{
  "video": {"resolution": [480, 360], "fps": 20, "quality": 60},
  "audio": {"sample_rate": 44100, "channels": 1}
}
```

## 🎯 Best Practices

1. **Use Headphones**: Prevents audio feedback/echo
2. **Good Lighting**: Improves video quality
3. **Stable Network**: Use Ethernet > WiFi
4. **Close Other Apps**: Frees bandwidth and CPU
5. **Mute When Not Speaking**: Reduces noise
6. **Test First**: Connect with one client before group session

## 📱 Multi-User Scenarios

### 2 Users
- Video: Side-by-side (1x2 grid)
- Audio: Clear conversation
- Bandwidth: Low

### 3-4 Users
- Video: 2x2 grid
- Audio: Group discussion
- Bandwidth: Medium

### 5-9 Users
- Video: 3x3 grid
- Audio: Meeting/conference
- Bandwidth: High

### 10+ Users
- Video: 4x4+ grid (smaller boxes)
- Audio: May be chaotic
- Bandwidth: Very high
- Recommendation: Use mute when not speaking

## 🆘 Getting Help

### Check Logs

**Server Logs:**
- Terminal where server is running
- Shows connections, errors

**Client Logs:**
- Terminal where client is running
- Shows connection status, errors

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Connection refused` | Server not running | Start server |
| `Failed to start camera` | Camera in use | Close other apps |
| `Failed to start audio` | Audio device busy | Restart client |
| `No module named 'cv2'` | OpenCV not installed | `pip install opencv-python` |

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 2 GB
- Network: 1 Mbps
- Webcam: Any USB/built-in
- Microphone: Any USB/built-in

**Recommended:**
- CPU: Quad-core 2.5 GHz+
- RAM: 4 GB+
- Network: 10 Mbps+
- Webcam: 720p or better
- Microphone: Noise-cancelling headset

## 🎓 Advanced Usage

### Running Server on Cloud

1. **Deploy to VPS** (DigitalOcean, AWS, etc.)
2. **Open Ports**: 5000-5005 TCP/UDP
3. **Use Public IP**: Clients connect via internet
4. **Monitor**: Use `htop` to watch resources

### Custom Configuration

Create `my_config.json`:
```json
{
  "server": {
    "video_port": 6000,
    "audio_port": 6001
    // ...custom ports
  }
}
```

Load with:
```python
server = CollaborationServer('my_config.json')
```

### Automated Testing

Run test suite:
```bash
cd tests
python run_all_tests.py
```

## 📞 Support

For issues, check:
1. This user guide
2. `TROUBLESHOOTING.md`
3. `ARCHITECTURE.md` for technical details
4. Server/client logs for error messages

---

**Enjoy your collaboration session! 🎉**
