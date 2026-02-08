# Jungler Tracker Overlay Guide

The Katarina AI Coach now includes a **jungler tracker overlay** that shows if the enemy jungler is visible or invisible on your minimap!

## 🎯 What It Does

The jungler tracker:
- 🔍 **Detects enemy jungler** by identifying who has Smite summoner spell
- 👁️ **Tracks visibility** using minimap detection to see if jungler is visible
- 🖼️ **Shows overlay** in top-left corner of screen with real-time status
- 🚨 **Color-coded alerts**:
  - 🟢 **GREEN "VISIBLE"** - Enemy jungler detected on minimap (you can see them!)
  - 🔴 **RED "INVISIBLE"** - Enemy jungler not visible (danger - they could be anywhere!)
  - 🟡 **YELLOW "SEARCHING..."** - Still looking for who the enemy jungler is

## 🎮 Usage

### Enable jungler tracker (default):
```bash
python katarina_coach.py
```

The overlay will appear in the **top-left corner** of your screen when the coach starts.

### Disable jungler tracker:
```bash
python katarina_coach.py --no-jungler
```

### Combine with other options:
```bash
python katarina_coach.py --no-voice       # Jungler tracker + predictions only
python katarina_coach.py --no-minimap     # Voice only (no jungler tracker)
```

## 🔧 How It Works

### 1. **Jungler Detection**
The tracker uses the Live Client API to check all enemy players and find who has Smite:

```python
# Example API data
{
  "summonerName": "Enemy Player",
  "championName": "Pantheon",
  "summonerSpells": {
    "summonerSpellOne": {"displayName": "Flash"},
    "summonerSpellTwo": {"displayName": "Smite"}  # <- This player is the jungler!
  }
}
```

### 2. **Visibility Tracking**
Once the jungler is identified, the tracker uses minimap detection:
- Captures minimap screenshot every 2 seconds
- Runs YOLO object detection to find champions
- If ANY champion detected → jungler might be visible → **GREEN**
- If NO champions detected → jungler definitely invisible → **RED**

### 3. **Real-time Overlay**
The overlay uses tkinter to create an always-on-top window:
```
┌─────────────────┐
│   INVISIBLE     │  <- Red text (danger!)
│   Pantheon      │  <- Jungler champion name
└─────────────────┘
```

## 🎨 Overlay Customization

You can customize the overlay by editing `jungler_tracker.py`:

### Change Size and Position
```python
# In __init__ method
self.window.geometry("200x80+10+10")  # widthxheight+x+y
# Example: "300x100+50+50" for bigger overlay at position (50, 50)
```

### Change Font and Colors
```python
# Status label
self.status_label = tk.Label(
    self.window,
    text="SEARCHING...",
    font=("Arial", 16, "bold"),  # Change font, size, weight
    fg="yellow",                 # Change text color
    bg="black"                   # Change background color
)
```

## 📊 Limitations & Future Improvements

### Current Limitations
1. **Generic detection** - Can't specifically identify which detected champion is the jungler
   - Shows "VISIBLE" if ANY enemy is on minimap
   - This creates false positives (shows visible even if it's not the jungler)

2. **No support role detection** - Only detects junglers via Smite
   - Won't detect if someone takes Smite top/mid (rare but possible)

3. **Fixed overlay position** - Always shows in top-left corner
   - May overlap with other UI elements

### Planned Improvements
1. ✨ **Champion identification** - Fine-tune YOLO to recognize specific champions
   - Only show "VISIBLE" when the actual jungler champion is detected
   - 95%+ accuracy instead of current ~60-70%

2. ✨ **Position tracking** - Remember last known position
   - Show arrow indicating where jungler was last seen
   - Timer showing "Last seen: 15s ago"

3. ✨ **Path prediction** - ML model to predict jungler pathing
   - Show likely next jungle camp
   - Warn about potential ganks

4. ✨ **Draggable overlay** - Allow user to reposition overlay
   - Save position preference to config file

## 🐛 Troubleshooting

### Overlay not showing?

1. **Check if tkinter is installed**:
   ```bash
   python -c "import tkinter; print('OK')"
   ```

2. **Make sure game is running**:
   - Tracker needs Live Client API to detect jungler
   - Start a Practice Tool or real game

3. **Verify minimap detection is enabled**:
   ```bash
   python katarina_coach.py  # Should NOT have --no-minimap flag
   ```

### Shows "SEARCHING..." forever?

- Enemy team might not have a jungler (Practice Tool with only 1 enemy)
- Enemy jungler hasn't loaded in yet (early game)
- API connection issue - check if other features work

### Always shows "VISIBLE" even when jungler not visible?

- This is a known limitation - generic YOLO can't identify specific champions
- Any detected enemy champion triggers "VISIBLE" status
- Will be fixed when we fine-tune YOLO on LoL minimap dataset

### Overlay blocks other UI?

- Edit `jungler_tracker.py` and change `geometry` parameter:
  ```python
  self.window.geometry("200x80+10+10")  # Change +10+10 to new position
  ```

## 📚 Technical Details

### Architecture
```
Live Client API → Detect Jungler (Smite check) →
Minimap Detector → Champion Detection (YOLO) →
JunglerTracker → Update Overlay (tkinter)
```

### Files
- **jungler_tracker.py** - Main tracker module
- **katarina_coach.py** - Integration with coach
- **minimap_detector.py** - Computer vision for minimap

### Dependencies
- `tkinter` - GUI overlay (built-in with Python)
- `requests` - Live Client API calls
- `urllib3` - SSL handling
- Minimap detection dependencies: `ultralytics`, `pillow`, `mss`

## 🎯 Example Scenarios

### Scenario 1: Safe Farming
```
┌─────────────────┐
│   VISIBLE       │  <- GREEN (safe!)
│   Lee Sin       │
└─────────────────┘
```
**Meaning**: Enemy jungler (Lee Sin) is showing on minimap, likely on the other side of map. Safe to farm aggressively!

### Scenario 2: Danger Zone
```
┌─────────────────┐
│   INVISIBLE     │  <- RED (danger!)
│   Kha'Zix       │
└─────────────────┘
```
**Meaning**: Enemy jungler (Kha'Zix) not visible on minimap. Could be anywhere - play safe, ward, stay near tower!

### Scenario 3: Early Game
```
┌─────────────────┐
│   SEARCHING...  │  <- YELLOW
│                 │
└─────────────────┘
```
**Meaning**: Still identifying who the enemy jungler is. Wait for game to load or for more API data.

## 🔗 Related Guides

- [MINIMAP_SETUP.md](MINIMAP_SETUP.md) - Minimap detection setup
- [COACH_README.md](COACH_README.md) - Full coach documentation
- [README.md](README.md) - Project overview

---

**Stay one step ahead of the enemy jungler!** 🎯👁️🌲
