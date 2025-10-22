# 🚀 Quick Reference Card

## Start Server
```bash
cd /home/dk-zorin/Projects/collaboration-suite
python3 run_server.py
```

## Start Client
```bash
python3 gui_client.py
```

## Login
- **Username**: Your name (e.g., "Sanjeet")
- **Server IP**: 
  - `127.0.0.1` (same machine)
  - `192.168.x.x` (local network)

## Controls

| Button | Action |
|--------|--------|
| **Join Session** | Connect to server, start collaboration |
| **Leave Session** | Disconnect gracefully |
| **Start Video** / **Stop Video** | Toggle webcam |
| **Mute** / **Unmute** | Toggle microphone |
| **Share Screen** | Share your screen (coming soon) |
| **Send File** | Upload a file to share |

## Features

### 🎥 Video
- Auto-starts when joining
- Shows all users in grid
- Dynamic layout (2x2, 3x3, etc.)

### 🎤 Audio
- Auto-starts unmuted
- Server mixes all voices
- Use headphones!

### 💬 Chat
- Type message, press Enter
- Timestamps on all messages
- Join/leave notifications

### 📁 Files
- Click "Send File" to upload
- Double-click file to download
- All users notified

## Ports Used

| Port | Service | Protocol |
|------|---------|----------|
| 5000 | Video | UDP |
| 5001 | Audio | UDP |
| 5002 | Screen | TCP |
| 5003 | Chat | TCP |
| 5004 | Files | TCP |
| 5005 | Control | TCP |

## Troubleshooting

### Can't Connect
```bash
# Check server is running
# Verify IP address
# Open firewall ports 5000-5005
```

### No Video
```bash
# Close other camera apps
# Check /dev/video0 exists
# Run: python3 test_system.py
```

### No Audio
```bash
# Check volume
# Use headphones
# Test: python3 test_system.py
```

### Laggy
```bash
# Close other network apps
# Lower quality in config
# Use wired connection
```

## Configuration

Edit `configs/config.json`:

**High Quality:**
```json
{"video": {"resolution": [1280, 720], "fps": 30, "quality": 90}}
```

**Low Bandwidth:**
```json
{"video": {"resolution": [480, 360], "fps": 20, "quality": 60}}
```

## Network Setup

### Find Server IP
```bash
hostname -I
```

### Test System
```bash
python3 test_system.py
```

### Firewall (if needed)
```bash
sudo ufw allow 5000:5005/tcp
sudo ufw allow 5000:5001/udp
```

## Common Commands

```bash
# Start server
python3 run_server.py

# Start GUI client
python3 gui_client.py

# Start CLI client
python3 run_client.py Alice 127.0.0.1

# Test system
python3 test_system.py

# Run tests
cd tests && python3 run_all_tests.py
```

## Documentation

- 📖 `USER_GUIDE.md` - Complete user manual
- 🏗️ `ARCHITECTURE.md` - System architecture
- ✅ `IMPLEMENTATION_SUMMARY.md` - Technical details
- 📋 `COMPLETION_SUMMARY.md` - What's been implemented
- ❓ `TROUBLESHOOTING.md` - Problem solving

## Quick Test

```bash
# Terminal 1: Server
python3 run_server.py

# Terminal 2: Client 1
python3 gui_client.py
# Login: Alice, 127.0.0.1, Join

# Terminal 3: Client 2  
python3 gui_client.py
# Login: Bob, 127.0.0.1, Join

# You should see both users in video grid!
```

## Tips

1. **Use Headphones** - Prevents echo
2. **Good Lighting** - Better video quality
3. **Stable Network** - Ethernet > WiFi
4. **Close Other Apps** - Frees bandwidth
5. **Mute When Not Speaking** - Reduces noise

## Performance

### Bandwidth per User
- Video: ~2-4 Mbps per other user
- Audio: ~200 kbps (total)
- **4 users**: ~10 Mbps

### System Requirements
- CPU: 2+ cores, 2 GHz+
- RAM: 2+ GB
- Network: 1+ Mbps per user
- Webcam + Microphone

## Support

🐛 **Issues?**
1. Read `USER_GUIDE.md`
2. Run `python3 test_system.py`
3. Check server/client logs
4. Review `TROUBLESHOOTING.md`

---

**Enjoy! 🎉**
