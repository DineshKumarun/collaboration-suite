# 🎨 System Diagrams

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COLLABORATION SERVER                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Video Relay │  │ Audio Mixer  │  │  Chat Server │      │
│  │   UDP:5000   │  │   UDP:5001   │  │   TCP:5003   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Screen Relay  │  │ File Server  │  │   Control    │      │
│  │   TCP:5002   │  │   TCP:5004   │  │   TCP:5005   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
            │              │              │              │
            └──────────────┴──────────────┴──────────────┘
                              ▼
                         LAN/Internet
                              ▼
            ┌──────────────┬──────────────┬──────────────┐
            │              │              │              │
   ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
   │   CLIENT 1     │ │   CLIENT 2     │ │   CLIENT 3     │
   │   (Alice)      │ │    (Bob)       │ │   (Carol)      │
   │                │ │                │ │                │
   │  ┌──────────┐  │ │  ┌──────────┐  │ │  ┌──────────┐  │
   │  │Video Grid│  │ │  │Video Grid│  │ │  │Video Grid│  │
   │  │ ┌──┬──┐  │  │ │  │ ┌──┬──┐  │  │ │  │ ┌──┬──┐  │  │
   │  │ │Me│Bo│  │  │ │  │ │Al│Me│  │  │ │  │ │Al│Bo│  │  │
   │  │ └──┴──┘  │  │ │  │ └──┴──┘  │  │ │  │ └──┴──┘  │  │
   │  │ ┌──┬──┐  │  │ │  │ ┌──┬──┐  │  │ │  │ ┌──┬──┐  │  │
   │  │ │Ca│  │  │  │ │  │ │Ca│  │  │  │ │  │ │Me│  │  │  │
   │  │ └──┴──┘  │  │ │  │ └──┴──┘  │  │ │  │ └──┴──┘  │  │
   │  └──────────┘  │ │  └──────────┘  │ │  └──────────┘  │
   │                │ │                │ │                │
   │  💬 Chat       │ │  💬 Chat       │ │  💬 Chat       │
   │  📁 Files      │ │  📁 Files      │ │  📁 Files      │
   └────────────────┘ └────────────────┘ └────────────────┘
```

## Data Flow: Video

```
Alice's Client
     │
     │ 1. Capture webcam frame (640x480)
     ▼
  [OpenCV VideoCapture]
     │
     │ 2. Compress to JPEG (quality 80)
     ▼
  [cv2.imencode]
     │
     │ 3. Add client_id prefix
     ▼
  [client_id_len | client_id | chunk_idx | total | jpeg_data]
     │
     │ 4. Send via UDP to server:5000
     ▼
═══════════════════════════════════════
     SERVER - Video Relay
═══════════════════════════════════════
     │
     │ 5. Receive packet, parse client_id
     ▼
  [Extract: sender = "alice"]
     │
     │ 6. Relay to all OTHER clients
     ▼
  ┌─────────────────────┬─────────────────────┐
  │                     │                     │
  ▼                     ▼                     ▼
Bob's Client      Carol's Client       (not Alice)
  │                     │
  │ 7. Receive chunks   │
  ▼                     ▼
[Reassemble JPEG]   [Reassemble JPEG]
  │                     │
  │ 8. Decode image     │
  ▼                     ▼
[cv2.imdecode]      [cv2.imdecode]
  │                     │
  │ 9. Display in grid[alice]
  ▼                     ▼
┌─────────┐         ┌─────────┐
│ Alice   │         │ Alice   │
│ (video) │         │ (video) │
└─────────┘         └─────────┘
```

## Data Flow: Audio

```
Alice          Bob           Carol
  │             │              │
  │ Mic input   │ Mic input    │ Mic input
  ▼             ▼              ▼
[Capture]    [Capture]      [Capture]
  │             │              │
  │ PCM 16-bit  │ PCM 16-bit   │ PCM 16-bit
  ▼             ▼              ▼
[Add ID]     [Add ID]       [Add ID]
  │             │              │
  │ UDP:5001    │ UDP:5001     │ UDP:5001
  └─────────────┴──────────────┘
                │
                ▼
    ═══════════════════════════
         SERVER - Audio Mixer
    ═══════════════════════════
                │
                │ 1. Collect audio from all
                ▼
         ┌──────────────┐
         │ Buffer:      │
         │  alice: [..] │
         │  bob:   [..] │
         │  carol: [..] │
         └──────────────┘
                │
                │ 2. Mix (average samples)
                ▼
         [mixed = mean(all)]
                │
                │ 3. Broadcast to all
                ▼
    ┌───────────┴───────────┐
    │           │           │
    ▼           ▼           ▼
  Alice       Bob        Carol
    │           │           │
    │ Play      │ Play      │ Play
    ▼           ▼           ▼
 Speakers    Speakers   Speakers
 (hears      (hears     (hears
  Bob+Carol)  Alice+Car) Alice+Bob)
```

## Data Flow: Chat

```
Alice types: "Hello!"
     │
     │ Press Enter
     ▼
[Create message with timestamp]
     │
     ▼
{"sender": "Alice", "message": "Hello!", "time": 12345}
     │
     │ Send to server TCP:5003
     ▼
═══════════════════════════════════════
     SERVER - Chat Broadcast
═══════════════════════════════════════
     │
     │ Relay to all connected chat clients
     ▼
  ┌─────────────────────┬─────────────────────┐
  │                     │                     │
  ▼                     ▼                     ▼
Alice               Bob                 Carol
  │                     │                     │
  │ Display locally     │ Receive & display   │ Receive & display
  ▼                     ▼                     ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│[14:30] Alice:│  │[14:30] Alice:│  │[14:30] Alice:│
│  Hello!      │  │  Hello!      │  │  Hello!      │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Data Flow: File Sharing

```
Alice: "Share report.pdf"
     │
     │ 1. Select file
     ▼
┌─────────────────┐
│ report.pdf      │
│ Size: 2.5 MB    │
└─────────────────┘
     │
     │ 2. Send upload command
     ▼
TCP:5004 → SERVER
═══════════════════════════════════════
     SERVER - File Upload
═══════════════════════════════════════
     │
     │ 3. Receive file data
     ▼
┌─────────────────────┐
│ shared_files/       │
│   abc123_report.pdf │
└─────────────────────┘
     │
     │ 4. Store metadata
     ▼
files["abc123"] = {
  "filename": "report.pdf",
  "size": 2621440,
  "uploader": "Alice"
}
     │
     │ 5. Notify ALL clients
     ▼
  ┌─────────────────────┬─────────────────────┐
  │                     │                     │
  ▼                     ▼                     ▼
Alice               Bob                 Carol
  │                     │                     │
  │                     │ Add to file list    │
  ▼                     ▼                     ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│📁 Files:     │  │📁 Files:     │  │📁 Files:     │
│• report.pdf  │  │• report.pdf  │  │• report.pdf  │
│  (2.5 MB)    │  │  (2.5 MB)    │  │  (2.5 MB)    │
│  - from Alice│  │  - from Alice│  │  - from Alice│
└──────────────┘  └──────────────┘  └──────────────┘
                        │                     │
                        │ Double-click        │
                        ▼                     ▼
                  Download request      Download request
                        │                     │
                        └──────────┬──────────┘
                                   ▼
                             SERVER sends file
```

## Session Management Flow

```
Client Startup
     │
     ▼
┌─────────────────┐
│ Login Dialog    │
│ Username: Alice │
│ Server: 192...  │
└─────────────────┘
     │
     │ Click Connect
     ▼
TCP:5005 → SERVER
═══════════════════════════════════════
     SERVER - Control
═══════════════════════════════════════
     │
     │ 1. Receive client info
     ▼
clients["alice"] = {
  "username": "Alice",
  "address": ("192.168.1.10", 5432),
  "control_conn": <socket>
}
     │
     │ 2. Send current client list
     ▼
{"status": "connected", "clients": [
  {"id": "bob", "username": "Bob"},
  {"id": "carol", "username": "Carol"}
]}
     │
     │ 3. Notify others of new client
     ▼
  ┌─────────────────────┬─────────────────────┐
  │                     │                     │
  ▼                     ▼                     ▼
Bob                 Carol              (not Alice)
  │                     │
  │ Receive join event  │
  ▼                     ▼
{"type": "client_update",
 "action": "joined",
 "client_id": "alice",
 "username": "Alice"}
  │                     │
  │ Add to client list  │
  ▼                     ▼
clients["alice"] = {...}
  │                     │
  │ Update video grid   │
  ▼                     ▼
Add new video box for Alice
```

## Client GUI State Machine

```
┌──────────────┐
│ Not Connected│
└──────┬───────┘
       │
       │ Click "Join Session"
       ▼
┌──────────────┐
│  Connecting  │────────┐ Error
└──────┬───────┘        │
       │                ▼
       │ Success   ┌─────────┐
       ▼           │ Failed  │
┌──────────────┐   └─────────┘
│  Connected   │
│  (Session    │
│   Active)    │
└──────┬───────┘
       │
       │ Auto-start features
       ▼
┌──────────────────────────┐
│ • Video streaming        │
│ • Audio capturing/playing│
│ • Chat connected         │
│ • File server connected  │
│ • Video grid populated   │
└──────┬───────────────────┘
       │
       │ Features active
       │
       │ User clicks "Leave Session"
       │
       ▼
┌──────────────┐
│ Disconnecting│
└──────┬───────┘
       │
       │ Stop all services
       ▼
┌──────────────┐
│ Not Connected│
└──────────────┘
```

## Threading Architecture

```
CLIENT PROCESS
│
├─ Main Thread (GUI)
│  └─ Tkinter event loop
│     • Handle button clicks
│     • Update display
│     • Process queues
│
├─ Control Thread
│  └─ Handle server messages
│     • Join/leave events
│     • File notifications
│     • Client updates
│
├─ Video Send Thread
│  └─ Capture → Compress → Send
│     • 30 FPS loop
│     • JPEG encoding
│     • UDP transmission
│
├─ Video Receive Thread
│  └─ Receive → Decode → Queue
│     • UDP reception
│     • Chunk assembly
│     • Frame queueing
│
├─ Audio Send Thread
│  └─ Capture → Send
│     • Microphone capture
│     • UDP transmission
│
└─ Audio Receive Thread
   └─ Receive → Play
      • UDP reception
      • Speaker playback

SERVER PROCESS
│
├─ Main Thread
│  └─ Keep server running
│
├─ Control Accept Thread
│  └─ Accept new clients
│
├─ Control Handler Threads (N)
│  └─ One per client
│     • Handle commands
│     • Send updates
│
├─ Video Relay Thread
│  └─ UDP relay loop
│     • Receive from any
│     • Send to all others
│
├─ Audio Relay Thread
│  └─ UDP relay + mix
│     • Collect from all
│     • Mix audio
│     • Broadcast mixed
│
├─ Screen Relay Thread
│  └─ TCP relay
│
├─ Chat Server Thread
│  └─ TCP broadcast
│
└─ File Server Thread
   └─ Handle uploads/downloads
```

## Network Packet Visualization

### Video Packet
```
┌────┬─────────────┬──────┬───────┬─────────────┐
│ 1B │   N bytes   │  2B  │  2B   │   M bytes   │
├────┼─────────────┼──────┼───────┼─────────────┤
│ ID │  client_id  │chunk │ total │ jpeg_data   │
│len │   "alice"   │ idx  │chunks │ [binary]    │
└────┴─────────────┴──────┴───────┴─────────────┘
  ▲        ▲          ▲       ▲         ▲
  │        │          │       │         │
  5        alice      0       3      [chunk 0]
```

### Audio Packet
```
┌────┬─────────────┬─────────────────────┐
│ 1B │   N bytes   │     M bytes         │
├────┼─────────────┼─────────────────────┤
│ ID │  client_id  │   PCM audio data    │
│len │   "bob"     │   [binary samples]  │
└────┴─────────────┴─────────────────────┘
```

### Chat Message (JSON)
```json
{
  "type": "chat",
  "sender": "Alice",
  "message": "Hello everyone!",
  "timestamp": 1698765432
}
```

## File Storage Structure

```
collaboration-suite/
└── shared_files/
    ├── abc123_presentation.pdf
    ├── def456_report.docx
    └── ghi789_image.jpg

In-memory:
shared_files = {
  "abc123": {
    "filename": "presentation.pdf",
    "size": 2621440,
    "path": "shared_files/abc123_presentation.pdf",
    "uploader": "Alice"
  },
  "def456": {...},
  "ghi789": {...}
}
```

---

**These diagrams show the complete data flow and architecture of the collaboration suite!**
