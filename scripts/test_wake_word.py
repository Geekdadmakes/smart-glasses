#!/usr/bin/env python3
"""
Test Wake Word Detection
"""

import os
import sys
import yaml
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from audio.wake_word import WakeWordDetector

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)


def test_wake_word():
    """Test wake word detection"""
    print("\n" + "=" * 60)
    print("WAKE WORD DETECTION TEST")
    print("=" * 60)

    # Load config
    config = load_config()

    print(f"\nConfiguration:")
    print(f"  Method: {config['wake_word'].get('method', 'porcupine')}")
    print(f"  Keyword: {config['wake_word'].get('keyword', 'hey glasses')}")
    print(f"  Sensitivity: {config['wake_word'].get('sensitivity', 0.5)}")
    print()

    # Check if using Porcupine
    method = config['wake_word'].get('method', 'porcupine')
    if method == 'porcupine':
        if not os.getenv('PORCUPINE_ACCESS_KEY'):
            print("WARNING: PORCUPINE_ACCESS_KEY not set in .env file")
            print("Get a free access key at: https://console.picovoice.ai/")
            print("\nFalling back to 'energy' detection mode for testing...")
            print("To use energy detection, you can:")
            print("1. Update config/config.yaml: set method to 'energy'")
            print("2. Or continue with this test (will auto-fallback)")
            print()

            response = input("Continue with test? (y/n): ").strip().lower()
            if response != 'y':
                print("Test cancelled")
                return

    try:
        # Initialize detector
        print("Initializing wake word detector...")
        detector = WakeWordDetector(
            config['wake_word'],
            audio_config=config['audio']
        )

        print(f"\n✓ Wake word detector initialized successfully!")
        print(f"  Using method: {detector.method}")
        print()

        # Start detection loop
        print("=" * 60)
        print("LISTENING FOR WAKE WORD")
        print("=" * 60)

        if detector.method == 'energy':
            print("\nUsing ENERGY detection (testing only)")
            print("Try speaking loudly or clapping to trigger detection")
            print("This is NOT the wake word - just loud sounds!")
        else:
            print(f"\nSay the wake word: '{config['wake_word'].get('keyword')}'")

        print("\nPress Ctrl+C to stop")
        print()

        detection_count = 0
        start_time = time.time()

        while True:
            try:
                if detector.detect():
                    detection_count += 1
                    elapsed = time.time() - start_time

                    print(f"\n{'='*60}")
                    print(f"✓ WAKE WORD DETECTED! (#{detection_count})")
                    print(f"  Time: {elapsed:.1f}s since start")
                    print(f"  Method: {detector.method}")
                    print(f"{'='*60}\n")

                    # Small delay to prevent immediate re-triggering
                    time.sleep(1)

                # Small delay to prevent CPU overload
                time.sleep(0.01)

            except KeyboardInterrupt:
                print("\n\nStopping...")
                break

        # Summary
        elapsed_total = time.time() - start_time
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total detections: {detection_count}")
        print(f"Total time: {elapsed_total:.1f}s")
        if detection_count > 0:
            print(f"Average time between detections: {elapsed_total/detection_count:.1f}s")
        print()

        # Cleanup
        detector.cleanup()
        print("✓ Cleanup complete")

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        print(f"\n✗ Test failed: {e}")
        return

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("Smart Glasses - Wake Word Detection Test")
    print("=" * 60)

    test_wake_word()


if __name__ == "__main__":
    main()
