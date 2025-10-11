# 🚀 PiDog Agent - Quick Start Guide

Get your AI-powered PiDog running in **under 10 minutes**!

## 📋 Prerequisites

- SunFounder PiDog robot (assembled)
- Raspberry Pi 4B with internet
- LiveKit Cloud account (free)
- Google Gemini API key (free)

---

## 🎯 Step 1: Get API Keys (5 min)

### LiveKit Cloud
1. Go to https://cloud.livekit.io
2. Sign up (free)
3. Create project
4. Go to **Settings → Keys**
5. Copy: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`

### Google Gemini
1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API Key**
3. Copy: `GOOGLE_API_KEY`

✅ **Save these somewhere safe - you'll need them in Step 3**

---

## 🔧 Step 2: Install on Raspberry Pi (3 min)

SSH into your PiDog:

```bash
ssh pi@<your-pidog-ip>
```

Clone and setup:

```bash
# Clone your repo
git clone <your-github-repo-url>
cd <repo-name>/pidog-agent

# Run setup script
chmod +x setup_pi.sh
./setup_pi.sh
```

The script installs everything automatically!

---

## ⚙️ Step 3: Configure (1 min)

Edit the config file:

```bash
nano .env
```

Paste your API keys from Step 1:

```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxx
LIVEKIT_API_SECRET=xxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxx
```

Save: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 🧪 Step 4: Test (1 min)

```bash
source .venv/bin/activate
python test_local.py
```

✅ **All tests should pass**

---

## 🎤 Step 5: Run! (30 seconds)

Start the agent:

```bash
python pidog_agent.py dev
```

You should see:

```
🐕 PiDog agent starting (mode: hardware)
✅ PiDog hardware initialized
✅ PiDog camera streaming started
✅ PiDog agent running
```

---

## 💬 Step 6: Connect & Talk!

1. Open https://agents-playground.livekit.io
2. Select your LiveKit project
3. Click **Connect**
4. **Start talking!**

### Try These:

- "Hello PiDog!"
- "Sit down"
- "What can you see?"
- "Wag your tail"
- "Give me a high five"

---

## 🐛 Troubleshooting

**Camera not working?**
```bash
sudo raspi-config
# → Interface Options → Camera → Enable
sudo reboot
```

**PiDog not moving?**
```bash
# Test hardware
python -c "from pidog import Pidog; dog = Pidog(); dog.do_action('sit')"

# Try with sudo
sudo $(which python) pidog_agent.py dev
```

**Connection error?**
- Check your `.env` file has correct API keys
- Verify internet connection: `ping google.com`

---

## ✅ Success!

Your PiDog is now AI-powered! 🎉

**Next steps:**
- Customize personality in `pidog_agent.py`
- Add new actions in `pidog_actions.py`
- See full README for advanced features

---

## 📚 Need Help?

- Full docs: See `README.md`
- Test local: `python test_local.py`
- Check logs: Look for error messages
- Community: LiveKit Discord, SunFounder Forum
