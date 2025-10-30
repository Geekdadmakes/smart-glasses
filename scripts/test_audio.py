#!/usr/bin/env python3
"""
Test audio devices and functionality
"""

import sys
import pyaudio

def list_audio_devices():
    """List all available audio devices"""
    print("\n" + "=" * 60)
    print("AUDIO DEVICES")
    print("=" * 60)

    audio = pyaudio.PyAudio()

    print("\nInput Devices (Microphones):")
    print("-" * 60)
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"[{i}] {info['name']}")
            print(f"    Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"    Input Channels: {info['maxInputChannels']}")
            print()

    print("\nOutput Devices (Speakers):")
    print("-" * 60)
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxOutputChannels'] > 0:
            print(f"[{i}] {info['name']}")
            print(f"    Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"    Output Channels: {info['maxOutputChannels']}")
            print()

    audio.terminate()

def test_microphone():
    """Test microphone input"""
    import speech_recognition as sr

    print("\n" + "=" * 60)
    print("MICROPHONE TEST")
    print("=" * 60)

    recognizer = sr.Recognizer()

    print("\nPlease speak into the microphone...")
    print("(Say something and press Ctrl+C when done)")

    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... (please remain quiet)")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Ready! Speak now...")

            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            print("\nProcessing speech...")

            try:
                text = recognizer.recognize_google(audio)
                print(f"\n✓ SUCCESS! Recognized: '{text}'")
            except sr.UnknownValueError:
                print("\n✗ Could not understand audio")
            except sr.RequestError as e:
                print(f"\n✗ Recognition error: {e}")

    except KeyboardInterrupt:
        print("\n\nTest cancelled")
    except Exception as e:
        print(f"\n✗ Error: {e}")

def test_speaker():
    """Test speaker output"""
    import pyttsx3

    print("\n" + "=" * 60)
    print("SPEAKER TEST")
    print("=" * 60)

    print("\nInitializing text-to-speech...")

    try:
        engine = pyttsx3.init()
        print("✓ TTS engine initialized")

        # Test speech
        print("\nPlaying test message...")
        engine.say("Smart glasses audio test. If you can hear this, the speaker is working correctly.")
        engine.runAndWait()

        print("✓ Speaker test complete")

    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("SMART GLASSES AUDIO TEST")
    print("=" * 60)

    # List devices
    list_audio_devices()

    # Test speaker
    test_speaker()

    # Test microphone
    print("\n\nWould you like to test the microphone? (y/n): ", end='')
    response = input().strip().lower()

    if response == 'y':
        test_microphone()

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
