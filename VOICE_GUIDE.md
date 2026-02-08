# Voice Coach Quick Start Guide 🔊

The Katarina AI Coach now has **VOICE ANNOUNCEMENTS**! Here's how to set it up and use it.

## Quick Setup (1 minute)

### Step 1: Install the voice library
```bash
pip install pyttsx3
```

### Step 2: Test your voice setup
```bash
python test_voice.py
```

You should hear the coach speaking test messages like:
- "Use Q"
- "Use E, Shunpo"
- "Use ultimate"
- "Back and buy"

### Step 3: Run the coach in a game
```bash
python katarina_coach.py
```

## What You'll Hear

The coach will speak to you every 2 seconds with clear, concise commands:

### High Confidence Predictions (>75%)
- 🔊 **"Use Q"**
- 🔊 **"Use E, Shunpo"**
- 🔊 **"Use ultimate"**
- 🔊 **"Back and buy"**

### Lower Confidence Predictions
- 🔊 **"Consider repositioning"**
- 🔊 **"Consider using W"**

### Cooldown Warnings
- 🔊 **"Use E, Shunpo, but it's on cooldown"**
- 🔊 **"Use ultimate, but it's on cooldown"**

## Voice Settings

The voice is optimized for gameplay:
- **Speed**: 175 words per minute (fast but clear)
- **Volume**: 90% (loud enough to hear during gameplay)
- **Voice**: Female voice if available (less robotic)
- **Non-blocking**: Voice speaks in background, predictions continue

## Customizing the Voice

Edit `katarina_coach.py` to adjust settings:

```python
# Around line 258
self.engine.setProperty('rate', 175)    # Change to 150 (slower) or 200 (faster)
self.engine.setProperty('volume', 0.9)  # Change to 0.5 (quieter) or 1.0 (louder)
```

## Disable Voice

If you prefer text-only mode:
```bash
python katarina_coach.py --no-voice
```

## Typical Gameplay Example

```
Game starts → Coach: "Voice coach initialized"

[You're farming mid]
Coach: 🔊 "Reposition"
Coach: 🔊 "Use Q"

[Enemy appears]
Coach: 🔊 "Use E, Shunpo"
Coach: 🔊 "Use W"
Coach: 🔊 "Use ultimate"

[After a fight, low HP, 1300g]
Coach: 🔊 "Back and buy"

[You recall and buy items]
Coach: 🔊 "Reposition"

[Game continues...]
```

## Why Voice is Better Than Text

1. **Eyes on the game** - No need to look at terminal
2. **Faster reactions** - Hear suggestions instantly
3. **Immersive** - Feels like a real coach
4. **Multitasking** - Listen while focusing on mechanics

## Troubleshooting

### No sound at all
1. Check system volume is up
2. Test with `test_voice.py` first
3. Try running as administrator (Windows)
4. Make sure no other app is blocking audio

### Voice is too robotic
- The coach automatically picks the best voice available
- Windows: Should use "Microsoft Zira" (female, clearer)
- If still robotic, you're stuck with your system's default TTS

### Voice is delayed
- Normal! Voice runs in a separate thread
- Prediction continues while speaking
- Small delay is expected (0.5-1 second)

### Voice says wrong things
- This is a prediction - the AI might be wrong!
- The coach learns from 1,500+ games but isn't perfect
- Use your judgment - the coach is a suggestion tool

## Tips for Best Results

1. **Adjust game volume** - Lower in-game music so you can hear the coach
2. **Use headphones** - Clearer voice, less distraction
3. **Practice Tool first** - Get used to voice coaching without pressure
4. **Trust your instincts** - The coach suggests, you decide
5. **High confidence = stronger suggestion** - Pay more attention to >75% predictions

## Example Play Session

**Early game (laning):**
- Coach mostly says "Use Q" (poke) and "Reposition"
- Occasional "Back and buy" when you have enough gold

**Mid game (roaming):**
- More "Use E, Shunpo" for gap closing
- "Use ultimate" for all-ins
- "Reposition" for map movement

**Team fights:**
- Rapid suggestions: "Use E, Shunpo", "Use W", "Use ultimate"
- Coach tracks cooldowns and warns if suggesting on-CD abilities

## Advanced: Voice During Combos

The coach can help you learn Katarina's combo patterns:

**Classic assassination combo:**
1. Coach: "Use E, Shunpo" (dash to target)
2. Coach: "Use Q" (damage + mark)
3. Coach: "Use W" (damage + movement speed)
4. Coach: "Use ultimate" (finish)

Over time, you'll internalize these patterns and react faster!

## Next Level: Custom Voice Messages

Want more specific messages? Edit the `get_voice_message()` function in `katarina_coach.py`:

```python
voice_messages = {
    "spell_Q": "Poke with Q",           # More descriptive
    "spell_E": "Dash in",                # Shorter
    "spell_R": "Death Lotus now",        # Ability name
    "buy": "Recall for items"            # More specific
}
```

## Comparison: With vs Without Voice

| Feature | Text Only | With Voice |
|---------|-----------|------------|
| Need to look at terminal | ✓ Yes | ✗ No |
| Reaction speed | Slower | Faster |
| Immersion | Low | High |
| Multitasking | Hard | Easy |
| Cooldown warnings | Text | Spoken |
| Best for | Analysis | Live gameplay |

---

**Ready to try it?**

1. `pip install pyttsx3`
2. `python test_voice.py` (verify it works)
3. `python katarina_coach.py` (start a game and listen!)

🔊 **Your AI voice coach is ready to guide you to victory!** 🎮⚔️
