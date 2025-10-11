#!/bin/bash
# Quick setup script for Raspberry Pi

set -e  # Exit on error

echo "================================"
echo "🐕 PiDog Agent - Pi Setup"
echo "================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev git

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Install PiDog hardware libraries
echo "🤖 Installing PiDog hardware libraries..."
pip install pidog robot-hat

# Install vilib (camera library)
echo "📷 Installing vilib camera library..."
if [ ! -d "$HOME/vilib" ]; then
    cd ~
    git clone -b picamera2 https://github.com/sunfounder/vilib.git --depth 1
    cd vilib
    sudo python3 install.py
    cd - > /dev/null
else
    echo "✅ vilib already installed"
fi

# Check for .env file
cd "$(dirname "$0")"
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   nano .env"
    echo ""
    echo "   You need:"
    echo "   - LiveKit credentials from https://cloud.livekit.io"
    echo "   - Google Gemini API key from https://aistudio.google.com/app/apikey"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "3. Test the setup:"
echo "   python test_local.py"
echo ""
echo "4. Run the agent:"
echo "   python pidog_agent.py dev"
echo ""
