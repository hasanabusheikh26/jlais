# 🐕 PiDog LiveKit + Gemini Agent (Hybrid Architecture)

Transform your SunFounder PiDog into an AI-powered companion with vision, voice, and real-time physical interaction!

## 🎯 Architecture

This uses a **hybrid approach** to work around LiveKit's ARM64 incompatibility:

```
User (Browser) ←→ LiveKit Cloud ←→ AI Agent (Mac/Cloud) ←→ HTTP API ←→ Hardware Server (Pi)
```

**Two components:**
1. **AI Agent** (`pidog_agent_remote.py`) - Runs on Mac/Cloud, handles LiveKit + Gemini
2. **Hardware Server** (`pidog_hardware_server.py`) - Runs on Pi, controls PiDog hardware

---

## ✨ Features

- **🎙️ Voice Conversations**: Natural dialogue via Gemini 2.0 Flash (<500ms latency)
- **👁️ Vision**: See through PiDog's camera and understand the environment
- **🦾 Physical Actions**: Voice commands trigger robot movements (sit, bark, wag tail, 20+ actions)
- **☁️ Cloud-Ready**: Agent can run anywhere (Mac, AWS, GCP, etc.)
- **🔌 Simple API**: Clean HTTP API between agent and hardware

---

## 🚀 Quick Start

### Part 1: Start Hardware Server on Pi

```bash
# On Raspberry Pi
cd ~/jlais/pidog-agent

# Install dependencies
pip3 install flask requests python-dotenv
sudo apt install -y python3-opencv python3-numpy

# Install PiDog hardware (see DEPLOY.md for details)
# Then run:
python3 pidog_hardware_server.py
```

Server will start on `http://0.0.0.0:5000`

### Part 2: Start AI Agent on Mac

```bash
# On your Mac
cd /Users/has/Desktop/Dev/AgentX/pidog-agent
source ../agent/.venv/bin/activate

# Install dependencies
pip install requests

# Configure .env with Pi's IP
nano .env
# Add: PIDOG_PI_HOST=192.168.1.100

# Run agent
python pidog_agent_remote.py dev
```

### Part 3: Connect and Play!

1. Open https://agents-playground.livekit.io
2. Select your LiveKit project
3. Click **Connect**
4. Start talking: "Hello PiDog!", "Sit down", "What do you see?"

---

## 📁 Files

| File | Runs On | Purpose |
|------|---------|---------|
| `pidog_hardware_server.py` | **Raspberry Pi** | Flask API server, controls hardware |
| `pidog_agent_remote.py` | **Mac/Cloud** | LiveKit + Gemini AI agent |
| `pidog_controller_remote.py` | **Mac/Cloud** | HTTP client for remote control |
| `pidog_actions.py` | **Both** | Action definitions for function calling |
| `requirements.txt` | **Mac/Cloud** | Python packages for agent |
| `requirements-pi.txt` | **Raspberry Pi** | Python packages for hardware server |
| `DEPLOY.md` | - | **Complete deployment guide** |

---

## 🔑 Configuration

Edit `.env` file:

```bash
# LiveKit credentials
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxx
LIVEKIT_API_SECRET=xxxxxxxx

# Gemini API
GOOGLE_API_KEY=AIzaSyxxxxxx

# Pi hardware server
PIDOG_PI_HOST=192.168.1.100  # Your Pi's IP
PIDOG_PI_PORT=5000
```

---

## 📚 Available Actions

| Category | Actions |
|----------|---------|
| **Basic** | sit, stand, lie |
| **Walking** | forward, backward, turn_left, turn_right |
| **Sounds** | bark, bark_harder, pant, howling |
| **Tricks** | high_five, handshake, push_up, stretch, scratch |
| **Head** | nod, shake_head, relax_neck |
| **Emotions** | wag_tail, think, waiting |

See `pidog_actions.py` for complete list.

---

## 🐛 Troubleshooting

**Can't connect to Pi:**
```bash
# Test connection
curl http://192.168.1.100:5000/health

# Check Pi's actual IP
# On Pi: hostname -I
```

**Hardware not responding on Pi:**
```bash
# Test hardware directly
python3 -c "from pidog import Pidog; dog = Pidog(); print('OK')"
```

**Agent can't see camera:**
- Verify hardware server is running on Pi
- Check network connectivity
- Look at Pi terminal for camera errors

---

## 🎨 Why Hybrid Architecture?

**Problem**: LiveKit's Python SDK doesn't ship ARM64 binaries for Raspberry Pi

**Solution**: 
- ✅ Agent runs on Mac/Cloud (has LiveKit support)
- ✅ Pi only handles hardware (simpler, works great)
- ✅ HTTP API connects them (clean, production-ready)
- ✅ Can scale to multiple Pis, cloud hosting, etc.

**This is actually how production robotics systems work!**

---

## 🚀 Production Deployment

**Run agent in cloud:**
- AWS EC2, Google Cloud Run, DigitalOcean
- Set Pi's public IP or use VPN
- Scale horizontally

**Or keep agent on Mac:**
- Works great for home/office use
- Low latency on local network
- Easy to debug

See `DEPLOY.md` for complete guide!

---

## 📖 Full Documentation

- **Quick Setup**: See above
- **Detailed Deployment**: `DEPLOY.md`
- **Troubleshooting**: This README + `DEPLOY.md`

---

## 🤝 Contributing

Found a bug? Want to add features?
1. Fork the repo
2. Create a branch
3. Make changes
4. Submit PR

---

## 📄 License

MIT License

---

## 🔗 Resources

- **LiveKit**: https://docs.livekit.io/agents
- **Gemini**: https://ai.google.dev/gemini-api
- **PiDog**: https://docs.sunfounder.com/projects/pidog

---

**Made with ❤️ using LiveKit, Gemini, and PiDog**
