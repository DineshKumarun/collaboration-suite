# 🏗️ Collaboration Suite Architecture

## Overview

This is a **Client-Server** architecture where all clients communicate through a centralized server. The server acts as a relay/router for all data streams.

```
        +----------------+
        |   SERVER APP   |
        | (Data Router)  |
        +----------------+
           /   |   |   \
          /    |   |    \
   [Client1] [Client2] [Client3]
```

## 🌐 Multi-Port Architecture

The application uses **6 separate ports** for different services:

| Feature              | Protocol | Port | Why                         |
| -------------------- | -------- | ---- | --------------------------- |
| Video Conferencing   | UDP      | 5000 | Low latency (loss-tolerant) |
| Audio Conferencing   | UDP      | 5001 | Real-time, fast             |
| Screen/Slide Sharing | TCP      | 5002 | Needs reliability           |
| Group Chat           | TCP      | 5003 | Text must not be lost       |
| File Transfer        | TCP      | 5004 | Large files, reliable       |
| Session Management   | TCP      | 5005 | Login, join/leave info      |

### Why This Design?

- **Separation of Concerns**: Each feature is independent
- **Optimal Protocols**: UDP for real-time (video/audio), TCP for reliability (chat/files)
- **Scalability**: Services can be scaled independently
- **Fault Tolerance**: One service failing doesn't crash others

## 📡 Communication Flow

### Video Conferencing (UDP - Port 5000)

**Client → Server → Other Clients**

1. **Capture**: Client captures webcam frame using OpenCV
2. **Compress**: Frame is compressed to JPEG (quality 80%)
3. **Packetize**: Large frames split into ~60KB UDP chunks
4. **Identify**: Each packet prefixed with `client_id`
5. **Send**: All chunks sent to server via UDP
6. **Relay**: Server broadcasts to all other clients
7. **Receive**: Clients reassemble chunks and decode JPEG
8. **Display**: Frame shown in video grid

**Packet Format:**
```
[client_id_len(1 byte)][client_id][chunk_idx(2)][total_chunks(2)][jpeg_data]
```

### Audio Conferencing (UDP - Port 5001)

**Client → Server (Mixing) → All Clients**

1. **Capture**: Client captures microphone input (44.1kHz, 16-bit)
2. **Chunk**: Audio divided into 2048-sample chunks
3. **Send**: Chunks sent to server with client_id
4. **Mix**: Server collects audio from all clients
5. **Average**: Server mixes by averaging samples (prevents clipping)
6. **Broadcast**: Mixed audio sent to all clients every 20ms
7. **Playback**: Clients play received mixed audio

**Why Mixing on Server?**
- Clients don't need to handle multiple audio streams
- Reduces bandwidth (1 stream instead of N)
- Prevents echo (client's own voice excluded)

**Packet Format:**
```
[client_id_len(1 byte)][client_id][audio_data]
```

### Screen Sharing (TCP - Port 5002)

**Presenter → Server → Viewers**

1. **Capture**: Presenter captures screen region
2. **Compress**: Screen converted to JPEG
3. **Frame**: Data size sent first (4 bytes)
4. **Send**: Complete frame sent via TCP
5. **Relay**: Server forwards to all other clients
6. **Display**: Viewers show in dedicated area

**Packet Format:**
```
[data_size(4 bytes)][client_id_len(1)][client_id][screen_jpeg]
```

### Group Chat (TCP - Port 5003)

**Client → Server → All Clients**

1. **Type**: User types message
2. **Format**: Message wrapped in JSON with username, timestamp
3. **Send**: Sent to server via TCP
4. **Broadcast**: Server forwards to all connected chat clients
5. **Display**: Received messages shown in chat box

**Message Format:**
```json
{
  "type": "chat",
  "username": "John",
  "message": "Hello!",
  "timestamp": 1234567890
}
```

### File Sharing (TCP - Port 5004)

**Upload Flow:**
1. User selects file
2. Client sends upload command with metadata
3. File transmitted in 64KB chunks
4. Server stores in `shared_files/` directory
5. Server notifies all clients of new file

**Download Flow:**
1. User double-clicks file in list
2. Client sends download request with file_id
3. Server sends file size and data
4. Client saves to downloads

**Commands:**
```json
// Upload
{"type": "upload", "file_id": "...", "filename": "...", "filesize": 123456, "uploader": "..."}

// Download
{"type": "download", "file_id": "..."}

// List files
{"type": "list"}
```

### Session Management (TCP - Port 5005)

**Control Socket** - Long-lived TCP connection for:

1. **Join**: Client sends username and client_id
2. **Acknowledge**: Server sends current client list
3. **Updates**: Server pushes join/leave notifications
4. **File Notifications**: New files announced
5. **Keepalive**: Periodic pings to detect disconnections

## 🎨 Client GUI Architecture

### Main Window Layout

```
┌─────────────────────────────────────────────────────┐
│ 👤 Username    [Join] [Leave] [Video] [Mute] [...]  │  ← Top Bar
├──────────────────────────────┬──────────────────────┤
│                              │  💬 Group Chat       │
│                              │  ┌────────────────┐  │
│       Video Grid             │  │ messages       │  │
│   ┌────┬────┬────┐          │  │                │  │
│   │You │User│User│          │  └────────────────┘  │
│   │    │ 2  │ 3  │          │  [input] [Send]      │
│   └────┴────┴────┘          │                      │
│                              │  📁 Shared Files     │
│                              │  • file1.pdf         │
│                              │  • image.jpg         │
└──────────────────────────────┴──────────────────────┘
│ Status: Connected to server                         │  ← Status Bar
└─────────────────────────────────────────────────────┘
```

### Video Grid Logic

- **Dynamic Layout**: Grid adjusts based on participants
  - 1 user: 1x1
  - 2-4 users: 2x2
  - 5-9 users: 3x3
  - 10-16 users: 4x4
- **Aspect Ratio**: Each box maintains 4:3 ratio
- **Placeholder**: Shows when user has no video
- **Username Label**: Displayed on each box

## 🔄 Threading Model

### Server Threads

1. **Control Accept Thread**: Accepts new client connections
2. **Control Handler Threads**: One per client for control messages
3. **Video Relay Thread**: UDP relay for video packets
4. **Audio Relay Thread**: UDP relay + mixing for audio
5. **Screen Relay Thread**: TCP relay for screen sharing
6. **Chat Server Thread**: TCP chat message relay
7. **File Server Thread**: Handles file upload/download
8. **File Handler Threads**: One per file operation

### Client Threads

1. **Main GUI Thread**: Tkinter event loop
2. **Control Message Handler**: Receives server updates
3. **Video Send Thread**: Captures and sends video
4. **Video Receive Thread**: Receives and queues video frames
5. **Audio Send Thread**: Captures and sends audio
6. **Audio Receive Thread**: Receives and plays audio
7. **Update GUI Thread**: 30 FPS display updates

## 🔒 Thread Safety

### Locks Used:

- **Server**: `clients_lock` - Protects client dictionary
- **Server**: `audio_buffer_lock` - Protects audio mixing buffer
- **Client**: Queues for inter-thread communication
  - `video_frames` - Video frame queue
  - `chat_queue` - Chat message queue
  - `control_queue` - Control message queue

## 📊 Data Flow Summary

```
Video/Audio (Real-time):
  Client → Compress → UDP → Server → Relay → Clients → Decompress → Display

Chat/Files (Reliable):
  Client → JSON → TCP → Server → Broadcast → Clients → Parse → Display

Session (Control):
  Client ←→ TCP (persistent) ←→ Server
```

## 🎯 Key Design Decisions

1. **Centralized Server**: Simpler than P2P, easier NAT traversal
2. **UDP for Media**: Low latency > perfect reliability
3. **TCP for Data**: Chat and files need guaranteed delivery
4. **Server-Side Audio Mixing**: Reduces client bandwidth
5. **Client ID in Packets**: Server can identify and route correctly
6. **JPEG Compression**: Good quality/size ratio for video
7. **Multiple Sockets**: Isolation and protocol optimization

## 🚀 Scalability Considerations

### Current Limitations:
- **Single Server**: Bottleneck for many clients
- **No Load Balancing**: All traffic through one instance
- **Memory**: Video/audio buffers grow with clients

### Potential Improvements:
- **Multiple Servers**: Geographic distribution
- **P2P for Media**: Direct streams between clients
- **WebRTC**: Industry-standard real-time communication
- **Compression**: Better codecs (H.264, Opus)
- **Rate Limiting**: Prevent bandwidth saturation

## 📝 Protocol Specification

See individual modules for detailed packet formats:
- `src/video_conferencing/video_stream.py` - Video protocol
- `src/audio_conferencing/audio_stream.py` - Audio protocol
- `src/server.py` - Server relay logic
