# LAN Network Setup Guide
# How to Connect Clients from Other Machines

## 🎯 Overview

By default, the server runs on `0.0.0.0` which listens on ALL network interfaces. This is already correct! You just need to:
1. Find your server machine's IP address
2. Configure firewall rules
3. Clients use that IP to connect

---

## 📡 Step 1: Find Your Server Machine's IP Address

### On Linux:
```bash
# Method 1: Using ip command
ip addr show | grep "inet " | grep -v 127.0.0.1

# Method 2: Using hostname
hostname -I

# Method 3: Using ifconfig (if installed)
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### On Windows:
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (WiFi or Ethernet).

### On macOS:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Example Output:**
```
192.168.1.100  ← This is your server's IP
```

---

## 🔥 Step 2: Configure Firewall

### Ubuntu/Debian (UFW):
```bash
# Allow the required ports
sudo ufw allow 5000/udp comment "Collaboration - Video"
sudo ufw allow 5001/udp comment "Collaboration - Audio"
sudo ufw allow 5002/tcp comment "Collaboration - Screen"
sudo ufw allow 5003/tcp comment "Collaboration - Chat"
sudo ufw allow 5004/tcp comment "Collaboration - Files"
sudo ufw allow 5005/tcp comment "Collaboration - Control"

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Fedora/RHEL/CentOS (firewalld):
```bash
# Add ports
sudo firewall-cmd --permanent --add-port=5000/udp
sudo firewall-cmd --permanent --add-port=5001/udp
sudo firewall-cmd --permanent --add-port=5002/tcp
sudo firewall-cmd --permanent --add-port=5003/tcp
sudo firewall-cmd --permanent --add-port=5004/tcp
sudo firewall-cmd --permanent --add-port=5005/tcp

# Reload firewall
sudo firewall-cmd --reload

# Check
sudo firewall-cmd --list-ports
```

### Manual iptables:
```bash
# Allow UDP ports
sudo iptables -A INPUT -p udp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 5001 -j ACCEPT

# Allow TCP ports
sudo iptables -A INPUT -p tcp --dport 5002 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5003 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5004 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5005 -j ACCEPT

# Save rules (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4
```

### Windows Firewall:
```powershell
# Run PowerShell as Administrator

# Allow UDP ports
New-NetFirewallRule -DisplayName "Collaboration-Video" -Direction Inbound -Protocol UDP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "Collaboration-Audio" -Direction Inbound -Protocol UDP -LocalPort 5001 -Action Allow

# Allow TCP ports
New-NetFirewallRule -DisplayName "Collaboration-Screen" -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow
New-NetFirewallRule -DisplayName "Collaboration-Chat" -Direction Inbound -Protocol TCP -LocalPort 5003 -Action Allow
New-NetFirewallRule -DisplayName "Collaboration-Files" -Direction Inbound -Protocol TCP -LocalPort 5004 -Action Allow
New-NetFirewallRule -DisplayName "Collaboration-Control" -Direction Inbound -Protocol TCP -LocalPort 5005 -Action Allow
```

---

## 🖥️ Step 3: Client Configuration

### On Client Machines:

When starting the client GUI, enter:
- **Username**: Any name (e.g., "John", "Sarah")
- **Server IP**: Your server's IP address (e.g., `192.168.1.100`)

**DO NOT USE:**
- ❌ `127.0.0.1` (this is localhost, only works on same machine)
- ❌ `localhost` (same as above)

**USE:**
- ✅ `192.168.1.100` (your server's actual LAN IP)
- ✅ `10.0.0.5` (if server is on 10.x network)
- ✅ Whatever IP your server shows

---

## 🔍 Step 4: Verify Server Configuration

### Check configs/config.json:

```json
{
  "server": {
    "host": "0.0.0.0",  ← Should be 0.0.0.0 (listens on all interfaces)
    "video_port": 5000,
    "audio_port": 5001,
    "screen_port": 5002,
    "chat_port": 5003,
    "file_port": 5004,
    "control_port": 5005
  }
}
```

**✅ Correct:** `"host": "0.0.0.0"` - Listens on ALL network interfaces
**❌ Wrong:** `"host": "127.0.0.1"` - Only listens on localhost

---

## 🧪 Step 5: Test Connectivity

### From Client Machine:

```bash
# Test if server is reachable
ping 192.168.1.100

# Test specific ports (if telnet/nc installed)
telnet 192.168.1.100 5005
# or
nc -zv 192.168.1.100 5005

# Test all ports
for port in 5000 5001 5002 5003 5004 5005; do
  nc -zv 192.168.1.100 $port 2>&1 | grep -q succeeded && echo "Port $port: OPEN" || echo "Port $port: CLOSED"
done
```

Expected output if working:
```
Connection to 192.168.1.100 5005 port [tcp] succeeded!
Port 5000: OPEN
Port 5001: OPEN
Port 5002: OPEN
Port 5003: OPEN
Port 5004: OPEN
Port 5005: OPEN
```

---

## 📋 Quick Setup Checklist

On **Server Machine**:
- [ ] Server is running: `python3 run_server.py`
- [ ] Get IP address: `hostname -I` or `ip addr`
- [ ] Firewall allows ports 5000-5005
- [ ] Server config has `"host": "0.0.0.0"`

On **Client Machine**:
- [ ] Can ping server: `ping SERVER_IP`
- [ ] Ports are reachable (test with telnet/nc)
- [ ] Start client: `python3 gui_client.py`
- [ ] Enter server's IP (NOT 127.0.0.1)

---

## 🚀 Complete Example

### Server Machine (IP: 192.168.1.100)

```bash
# 1. Open firewall ports
sudo ufw allow 5000:5005/tcp
sudo ufw allow 5000:5001/udp

# 2. Start server
cd /path/to/collaboration-suite
python3 run_server.py

# Server should show:
# Server running on 0.0.0.0
# Control Port: 5005
# Video Port: 5000
# ...
```

### Client Machine 1 (Different computer)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start client
python3 gui_client.py

# 3. In login dialog:
# Username: Alice
# Server IP: 192.168.1.100  ← Server's IP

# 4. Click Connect
# 5. Click Join Session
```

### Client Machine 2 (Another computer)

```bash
# Same as Client 1, but:
# Username: Bob
# Server IP: 192.168.1.100  ← Same server IP
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused"

**Cause**: Firewall blocking ports or server not running

**Solution**:
```bash
# On server, check if ports are listening
sudo netstat -tulpn | grep python
# or
sudo ss -tulpn | grep python

# Should show something like:
# tcp  0.0.0.0:5005  LISTEN  python3
# tcp  0.0.0.0:5002  LISTEN  python3
# udp  0.0.0.0:5000  LISTEN  python3
```

### Problem: "No route to host"

**Cause**: Wrong IP or machines on different networks

**Solution**:
- Verify server IP: `ip addr`
- Ensure both machines on same network (WiFi/LAN)
- Check router settings

### Problem: "Connection timeout"

**Cause**: Firewall blocking

**Solution**:
```bash
# Temporarily disable firewall to test (NOT for production!)
sudo ufw disable

# If it works, firewall is the issue
# Re-enable and add proper rules
sudo ufw enable
sudo ufw allow 5000:5005/tcp
sudo ufw allow 5000:5001/udp
```

### Problem: Works on localhost but not from other machines

**Cause**: Server binding to 127.0.0.1 instead of 0.0.0.0

**Solution**: Check `configs/config.json`:
```json
{
  "server": {
    "host": "0.0.0.0"  ← Must be 0.0.0.0, not 127.0.0.1
  }
}
```

---

## 🌍 Network Types

### Same WiFi Network
- ✅ Works out of the box
- All devices connect to same router
- Use server's local IP (192.168.x.x or 10.x.x.x)

### Wired LAN
- ✅ Works out of the box
- Use server's local IP

### Different Networks (over Internet)
- ⚠️ Requires port forwarding on router
- ⚠️ Requires public IP or dynamic DNS
- ⚠️ Security concerns (no encryption)
- **Not recommended** without adding security!

---

## 📊 Port Summary

| Port | Protocol | Purpose |
|------|----------|---------|
| 5000 | UDP | Video streaming |
| 5001 | UDP | Audio streaming |
| 5002 | TCP | Screen sharing |
| 5003 | TCP | Text chat |
| 5004 | TCP | File transfer |
| 5005 | TCP | Control/coordination |

---

## ✅ Verification Commands

```bash
# On server machine
# 1. Get your IP
MY_IP=$(hostname -I | awk '{print $1}')
echo "Server IP: $MY_IP"

# 2. Check ports are listening
sudo netstat -tulpn | grep -E "500[0-5]"

# 3. Test from another terminal
python3 -c "import socket; s=socket.socket(); s.connect(('$MY_IP', 5005)); print('✅ Port 5005 working')"
```

---

## 🎯 Quick Start Script

Create this on client machines:

```bash
#!/bin/bash
# quick_connect.sh

SERVER_IP="192.168.1.100"  # Change to your server's IP

echo "Testing connection to $SERVER_IP..."

# Test ping
if ping -c 1 $SERVER_IP &>/dev/null; then
    echo "✅ Server is reachable"
else
    echo "❌ Cannot reach server"
    exit 1
fi

# Test control port
if nc -zv $SERVER_IP 5005 2>&1 | grep -q succeeded; then
    echo "✅ Control port (5005) is open"
    echo ""
    echo "Ready to connect! Starting client..."
    python3 gui_client.py
else
    echo "❌ Control port (5005) is closed"
    echo "Check:"
    echo "  1. Server is running"
    echo "  2. Firewall allows port 5005"
fi
```

---

## 📱 Summary

**No code changes needed!** Your server is already configured correctly with `0.0.0.0`.

**You only need to:**
1. ✅ Find server's IP address
2. ✅ Open firewall ports 5000-5005
3. ✅ Clients enter server's IP (not 127.0.0.1)

That's it! 🎉
