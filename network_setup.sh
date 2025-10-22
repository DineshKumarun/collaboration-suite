#!/bin/bash
# Network Setup Helper for LAN Collaboration Suite

echo "🌐 LAN Collaboration Suite - Network Setup"
echo "=========================================="
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "📡 Your Server IP Address: $SERVER_IP"
echo ""

# Check if server is configured correctly
CONFIG_HOST=$(grep -A1 '"server"' configs/config.json | grep '"host"' | cut -d'"' -f4)
echo "🔧 Server Configuration:"
echo "   Host binding: $CONFIG_HOST"

if [ "$CONFIG_HOST" = "0.0.0.0" ]; then
    echo "   ✅ Correct! Server will listen on all network interfaces"
else
    echo "   ⚠️  Warning: Should be '0.0.0.0' for LAN access"
    echo "   Current setting only allows local connections"
fi
echo ""

# Check if ports are in use
echo "🔍 Checking if ports are available..."
PORTS_BUSY=0
for port in 5000 5001 5002 5003 5004 5005; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || \
       netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "   ⚠️  Port $port is already in use"
        PORTS_BUSY=1
    fi
done

if [ $PORTS_BUSY -eq 0 ]; then
    echo "   ✅ All ports (5000-5005) are available"
fi
echo ""

# Check firewall
echo "🔥 Firewall Configuration:"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | grep -i "status:" | cut -d: -f2 | xargs)
    echo "   UFW Status: $UFW_STATUS"
    
    if [ "$UFW_STATUS" = "active" ]; then
        echo "   Checking if collaboration ports are allowed..."
        
        ALLOWED=0
        for port in 5000 5001 5002 5003 5004 5005; do
            if sudo ufw status | grep -q "$port"; then
                ALLOWED=$((ALLOWED + 1))
            fi
        done
        
        if [ $ALLOWED -eq 6 ]; then
            echo "   ✅ All ports are allowed"
        else
            echo "   ⚠️  Some ports may be blocked"
            echo ""
            echo "   Run these commands to open ports:"
            echo "   sudo ufw allow 5000:5005/tcp"
            echo "   sudo ufw allow 5000:5001/udp"
        fi
    fi
elif command -v firewall-cmd &> /dev/null; then
    echo "   Detected: firewalld"
    echo "   Run: sudo firewall-cmd --list-ports"
else
    echo "   No firewall detected (or unable to check)"
fi
echo ""

# Network interfaces
echo "🌍 Network Interfaces:"
ip -4 addr show | grep -E "^[0-9]+" | while read line; do
    IFACE=$(echo $line | awk '{print $2}' | sed 's/://')
    IP=$(ip -4 addr show $IFACE | grep "inet " | awk '{print $2}' | cut -d/ -f1)
    if [ ! -z "$IP" ]; then
        if [ "$IP" = "127.0.0.1" ]; then
            echo "   🏠 $IFACE: $IP (localhost - not accessible from other machines)"
        else
            echo "   ✅ $IFACE: $IP (accessible from LAN)"
        fi
    fi
done
echo ""

# Instructions
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "On THIS machine (Server):"
echo "  1. Run: python3 run_server.py"
echo ""
echo "On OTHER machines (Clients):"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Run: python3 gui_client.py"
echo "  3. Enter Username: (any name)"
echo "  4. Enter Server IP: $SERVER_IP"
echo "  5. Click 'Connect' then 'Join Session'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test command
echo "🧪 Test Connectivity (from client machine):"
echo "   ping $SERVER_IP"
echo "   telnet $SERVER_IP 5005"
echo ""

# Quick firewall setup
echo "🔧 Quick Firewall Setup (if needed):"
if command -v ufw &> /dev/null; then
    echo "   sudo ufw allow 5000:5005/tcp"
    echo "   sudo ufw allow 5000:5001/udp"
    echo "   sudo ufw enable"
elif command -v firewall-cmd &> /dev/null; then
    echo "   sudo firewall-cmd --permanent --add-port=5000-5005/tcp"
    echo "   sudo firewall-cmd --permanent --add-port=5000-5001/udp"
    echo "   sudo firewall-cmd --reload"
else
    echo "   Check your system's firewall documentation"
fi
echo ""

echo "✨ Ready to start! Run: python3 run_server.py"
echo ""
