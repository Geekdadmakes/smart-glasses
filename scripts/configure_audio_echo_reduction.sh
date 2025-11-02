#!/bin/bash
# Configure WM8960 Audio HAT for echo reduction
# Uses hardware features to minimize echo feedback

echo "Configuring WM8960 Audio HAT for echo reduction..."

# Enable Noise Gate (reduces background noise and echo)
amixer -c 0 sset 'Noise Gate' on
amixer -c 0 sset 'Noise Gate Threshold' 31  # Maximum threshold

# Enable ADC High Pass Filter (removes low frequency echo)
amixer -c 0 sset 'ADC High Pass Filter' on

# Configure ALC (Automatic Level Control) for better dynamic range
amixer -c 0 sset 'ALC Function' 'Stereo'
amixer -c 0 sset 'ALC Mode' 'ALC'
amixer -c 0 sset 'ALC Target' 11  # Mid-range target
amixer -c 0 sset 'ALC Hold Time' 2  # Hold time
amixer -c 0 sset 'ALC Decay' 3  # Decay time
amixer -c 0 sset 'ALC Attack' 2  # Attack time

# Lower speaker volume to reduce echo pickup
amixer -c 0 sset 'Speaker' 80%  # Reduced from default
amixer -c 0 sset 'Headphone' 70%  # Reduced from default

# Increase microphone sensitivity slightly to compensate
amixer -c 0 sset 'Capture' 85%

echo "Audio configuration complete!"
echo ""
echo "Settings applied:"
echo "  ✓ Noise Gate: ON (threshold: 31)"
echo "  ✓ ADC High Pass Filter: ON"
echo "  ✓ ALC: Enabled"
echo "  ✓ Speaker Volume: 80%"
echo "  ✓ Headphone Volume: 70%"
echo "  ✓ Microphone Capture: 85%"
echo ""
echo "These settings should help reduce echo feedback and improve interruption detection."
