# 🐕 PiDog LiveKit + Gemini Agent

Transform your SunFounder PiDog into an AI-powered companion with vision, voice, and real-time physical interaction!

## ✨ Features

- **Real-time Voice Conversations**: Natural dialogue via Gemini 2.0 Flash (<500ms latency)
- **Vision**: See through PiDog's camera and understand the environment  
- **Physical Actions**: Voice commands trigger robot movements (sit, bark, wag tail, 20+ actions)
- **Mock Mode**: Test locally without hardware before deploying to Pi
- **WebRTC Streaming**: Low-latency video/audio via LiveKit

## 🎯 Quick Start

### Test Locally (Mac/Linux/Windows)

```bash
# Clone and navigate
cd pidog-agent

# Install dependencies (without hardware libs)
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your LiveKit & Gemini API keys

# Run in mock mode
python pidog_agent.py dev
```

Connect via [LiveKit Agents Playground](https://agents-playground.livekit.io) and talk to PiDog!

### Deploy to Raspberry Pi

```bash
# On your Pi
git clone <your-repo-url>
cd pidog-agent

# Install all dependencies including hardware
pip install -r requirements.txt
pip install pidog robot-hat

# Install vilib (camera library)
cd ~
git clone -b picamera2 https://github.com/sunfounder/vilib.git --depth 1
cd vilib
sudo python3 install.py

# Configure
cd ~/pidog-agent
cp .env.example .env
nano .env  # Add your API keys

# Run
python pidog_agent.py dev
```

## 🔑 Get API Keys

### LiveKit Cloud (Free)
1. Sign up: https://cloud.livekit.io
2. Create project
3. Go to Settings → Keys
4. Copy: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`

### Google Gemini (Free tier: 1500 requests/day)
1. Get key: https://aistudio.google.com/app/apikey
2. Copy: `GOOGLE_API_KEY`

## 🎮 Usage

Once running, connect via the [Agents Playground](https://agents-playground.livekit.io):

1. Select your LiveKit project
2. Click "Connect"
3. **Start talking!**

### Example Commands

**Conversation:**
- "Hello PiDog!"
- "What can you see?"
- "Tell me about yourself"

**Actions:**
- "Sit down"
- "Wag your tail"
- "Give me a high five"
- "Do a push up"
- "Bark"
- "Stretch"

**Vision:**
- "What color is my shirt?"
- "Can you see this?" (show object)
- "Describe what's around you"

## 🏗️ Architecture

```
User (Browser) ←→ LiveKit Cloud ←→ PiDog Agent (Pi)
      ↓                                    ↓
  Audio/Video                      Gemini 2.0 Flash
                                           ↓
                                   PiDog Controller
                                           ↓
                                   Hardware Actions
```

### Why It's Fast

**Traditional (OpenAI approach):**
```
Speech → Whisper STT → GPT-4 → OpenAI TTS → Audio
         ~500ms         ~1s       ~500ms
Total: 2-3 seconds delay
```

**LiveKit + Gemini:**
```
Audio/Video → Gemini Multimodal → Audio/Actions
              ~200-400ms
Total: <500ms delay
```

## 📁 Project Structure

```
pidog-agent/
├── pidog_agent.py          # Main agent (LiveKit + Gemini integration)
├── pidog_controller.py     # Hardware abstraction (auto-detects mock vs real)
├── pidog_actions.py        # Action definitions for function calling
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🎨 Customization

### Change Personality

Edit `pidog_agent.py`, modify the `instructions` parameter:

```python
instructions="""You are RoboDog, a tough guard dog.
Be serious, protective, and loyal. Bark at strangers!"""
```

### Add Custom Actions

In `pidog_actions.py`:

```python
PIDOG_ACTIONS = {
    # ... existing actions ...
    "dance": "Do a little dance",
    "patrol": "Walk in a patrol pattern",
}
```

### Adjust Camera Quality

In `pidog_agent.py`, change `_start_pidog_camera()`:

```python
# High quality (slower)
self._video_source = rtc.VideoSource(1920, 1080)
await asyncio.sleep(0.1)  # 10 FPS

# Low latency (recommended)
self._video_source = rtc.VideoSource(640, 480)
await asyncio.sleep(0.2)  # 5 FPS
```

## 🐛 Troubleshooting

### Mock mode not working locally

**Issue**: Import errors for opencv/numpy

**Solution**:
```bash
pip install opencv-python numpy
```

### PiDog doesn't move on Pi

**Issue**: Hardware not responding

**Check**:
```bash
# Test PiDog library
python -c "from pidog import Pidog; dog = Pidog(); dog.do_action('sit', speed=50)"

# Check permissions (might need sudo)
sudo python pidog_agent.py dev
```

### Camera not working on Pi

**Issue**: No video stream

**Check**:
```bash
# Test camera
python -c "from vilib import Vilib; Vilib.camera_start(); Vilib.camera_close()"

# Enable camera in raspi-config
sudo raspi-config
# → Interface Options → Camera → Enable
```

### High latency / Slow responses

**Solution**: Reduce camera quality in code (see Customization section)

### "Connection refused" error

**Check**: Your `.env` file has correct credentials
```bash
cat .env | grep LIVEKIT
# Should show wss:// URL and API keys
```

## 🔒 Security

- Never commit `.env` to git
- Set proper file permissions: `chmod 600 .env`
- Use LiveKit room tokens for production
- Keep API keys secret

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

## 🤝 Contributing

Found a bug? Want to add features?

1. Fork the repo
2. Create a branch
3. Make changes
4. Submit PR

## 📄 License

MIT License - See LICENSE file

## 🔗 Resources

- **LiveKit Agents**: https://docs.livekit.io/agents
- **Gemini API**: https://ai.google.dev/gemini-api
- **PiDog Docs**: https://docs.sunfounder.com/projects/pidog
- **Vilib**: https://github.com/sunfounder/vilib

## 💬 Support

- LiveKit Discord: https://discord.gg/livekit
- SunFounder Forum: https://forum.sunfounder.com
- Issues: GitHub Issues tab

---

**Made with ❤️ using LiveKit, Gemini, and PiDog**
