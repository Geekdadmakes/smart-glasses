#!/bin/bash
# Setup script for Smart Glasses on Raspberry Pi

echo "================================"
echo "Smart Glasses Setup Script"
echo "================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    echo "Some features may not work properly"
    echo ""
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "Installing Python dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev

# Install audio dependencies
echo "Installing audio dependencies..."
sudo apt-get install -y portaudio19-dev python3-pyaudio
sudo apt-get install -y alsa-utils libasound2-dev

# Install TTS dependencies
echo "Installing text-to-speech dependencies..."
sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev

# Install media libraries
echo "Installing media libraries..."
sudo apt-get install -y ffmpeg libav-tools

# Install Bluetooth dependencies
echo "Installing Bluetooth dependencies..."
sudo apt-get install -y bluetooth bluez libbluetooth-dev
sudo apt-get install -y pulseaudio pulseaudio-module-bluetooth

# Install camera dependencies
echo "Installing camera dependencies..."
sudo apt-get install -y python3-picamera2 python3-libcamera

# Install OpenCV dependencies
echo "Installing OpenCV dependencies..."
sudo apt-get install -y python3-opencv libopencv-dev

# Create directories
echo "Creating project directories..."
mkdir -p logs photos videos

# Install Python packages
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env and add your API keys!"
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Configure your audio device indices in config/config.yaml"
echo "3. Test audio: python3 -c 'from src.audio.audio_manager import AudioManager; AudioManager({}).list_audio_devices()'"
echo "4. Run the application: python3 src/main.py"
echo ""
