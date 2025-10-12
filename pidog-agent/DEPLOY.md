# 🚀 FINAL DEPLOYMENT GUIDE - Hybrid Architecture

## 🎯 Solution Overview

**Problem**: LiveKit doesn't support ARM64 Raspberry Pi  
**Solution**: Split into two parts:

```
User ←→ LiveKit Cloud ←→ Agent (Mac) ←→ HTTP API ←→ Hardware Server (Pi)
```

- **Agent** runs on your Mac (handles AI/LiveKit)
- **Hardware Server** runs on Pi (controls PiDog)
- They communicate via HTTP API

---

## 📦 Part 1: Setup Raspberry Pi Hardware Server

**On your Raspberry Pi:**

```bash
# 1. Go to project
cd ~/jlais/pidog-agent

# 2. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-numpy python3-flask

# 3. Install PiDog hardware libraries
cd ~
git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
cd robot-hat
sudo python3 setup.py install

cd ~
git clone https://github.com/sunfounder/pidog.git
cd pidog
sudo python3 setup.py install

cd ~
git clone -b picamera2 https://github.com/sunfounder/vilib.git --depth 1
cd vilib
sudo python3 install.py

# 4. Install Python packages
cd ~/jlais/pidog-agent
pip3 install flask requests python-dotenv

# 5. Start hardware server
python3 pidog_hardware_server.py
```

**Expected output:**
```
✅ PiDog hardware initialized
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

**Leave this running!** Note the IP address (e.g., 192.168.1.100)

---

## 💻 Part 2: Setup Mac Agent

**On your Mac:**

```bash
# 1. Go to project
cd /Users/has/Desktop/Dev/AgentX/pidog-agent

# 2. Make sure venv is active
source ../agent/.venv/bin/activate

# 3. Install requests (for HTTP communication)
pip install requests

# 4. Configure Pi connection
nano .env
```

Add these lines to `.env`:
```bash
PIDOG_PI_HOST=192.168.1.100  # Use your Pi's actual IP
PIDOG_PI_PORT=5000
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# 5. Run agent
python pidog_agent_remote.py dev
```

**Expected output:**
```
🐕 Connecting to PiDog at 192.168.1.100:5000...
✅ Connected to Pi
✅ PiDog camera streaming started
✅ PiDog agent running
```

---

## 🎮 Part 3: Test It!

1. **Open browser**: https://agents-playground.livekit.io
2. **Select your LiveKit project**
3. **Click "Connect"**
4. **Start talking!**

### Try These:

**Conversation:**
- "Hello PiDog!"
- "What can you see?"

**Actions (Pi will physically move!):**
- "Sit down" → PiDog sits on Pi
- "Wag your tail" → Tail wags
- "Stand up" → Stands
- "Give me a high five" → Raises paw

---

## 🔧 Troubleshooting

### Pi Hardware Server Issues

**"Hardware not available":**
```bash
# Test hardware directly
python3 -c "from pidog import Pidog; dog = Pidog(); print('OK')"
```

**Port already in use:**
```bash
# Kill old process
sudo lsof -t -i:5000 | xargs kill -9
```

### Mac Agent Issues

**"Cannot connect to Pi":**
```bash
# Test connection
curl http://192.168.1.100:5000/health

# If fails, check:
# 1. Is hardware server running on Pi?
# 2. Are Mac and Pi on same network?
# 3. Is IP address correct in .env?
```

**"No camera frames":**
- Check Pi terminal for camera errors
- Verify camera is enabled: `sudo raspi-config` → Interface → Camera

---

## ✅ Success Checklist

**On Pi:**
- ✅ Hardware server running
- ✅ Shows "Running on http://..."
- ✅ PiDog initialized

**On Mac:**
- ✅ Agent connected to Pi
- ✅ Camera streaming
- ✅ Agent running

**In Browser:**
- ✅ Connected to LiveKit
- ✅ Video shows PiDog's view
- ✅ Voice conversation works
- ✅ Commands make Pi physically move

---

## 🎯 Architecture Benefits

**Advantages:**
- ✅ Works immediately (no ARM64 issues)
- ✅ Agent runs on powerful Mac/cloud
- ✅ Pi only handles hardware (simpler)
- ✅ Easy to debug (separate processes)
- ✅ Production-ready architecture

**Disadvantages:**
- Requires network connection between Mac and Pi
- Slight latency for actions (~50-100ms over local network)

---

## 🚀 Making It Production

**Option 1: Keep Mac as server**
- Leave Mac running 24/7
- Works great for home use

**Option 2: Move agent to cloud**
- Deploy to AWS/GCP/DigitalOcean
- Pi connects to public server
- Most scalable

**Option 3: Use same network always**
- Set static IP for Pi
- Update `.env` once
- Reliable for home/office

---

## 📊 Summary

**You now have:**
- ✅ Working AI agent on Mac
- ✅ Working hardware control on Pi
- ✅ Clean HTTP API between them
- ✅ Full Gemini + LiveKit integration
- ✅ Real PiDog physical actions

**This is a production-ready architecture!** 🎉
