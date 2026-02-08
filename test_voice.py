"""
Test script for voice coach functionality
Tests text-to-speech without needing a League game
"""

import sys
import time

try:
    import pyttsx3
    print("[OK] pyttsx3 is installed")
except ImportError:
    print("[ERROR] pyttsx3 is NOT installed")
    print("\nInstall with: pip install pyttsx3")
    sys.exit(1)

print("\n" + "=" * 60)
print("   VOICE COACH TEST")
print("=" * 60)
print()

# Initialize TTS engine
print("Initializing text-to-speech engine...")
try:
    engine = pyttsx3.init()
    print("[OK] TTS engine initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize TTS: {e}")
    sys.exit(1)

# Set properties
engine.setProperty('rate', 175)  # Speed
engine.setProperty('volume', 0.9)  # Volume

# Try to use female voice
voices = engine.getProperty('voices')
print(f"\nAvailable voices: {len(voices)}")
for i, voice in enumerate(voices):
    print(f"  {i}: {voice.name}")
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        print(f"     ^ Using this voice")

print("\n" + "=" * 60)
print("Testing voice announcements...")
print("(You should hear the coach speaking)")
print("=" * 60)
print()

# Test messages
test_messages = [
    "Voice coach initialized",
    "Use Q",
    "Use W",
    "Use E, Shunpo",
    "Use ultimate",
    "Reposition",
    "Back and buy",
    "Use E, Shunpo, but it's on cooldown",
    "Consider repositioning"
]

for i, message in enumerate(test_messages, 1):
    print(f"[{i}/{len(test_messages)}] Speaking: \"{message}\"")
    engine.say(message)
    engine.runAndWait()
    time.sleep(0.5)

print()
print("=" * 60)
print("[SUCCESS] Voice test complete!")
print()
print("If you heard the announcements, voice coach is working.")
print("If not, check:")
print("  - System volume is up")
print("  - Other apps can play sound")
print("  - Try running as administrator (Windows)")
print("=" * 60)
