# Katarina AI Coach

Real-time next-action predictor for League of Legends Katarina gameplay.

## What It Does

The AI Coach watches your live Katarina game and predicts what action you should take next based on patterns learned from 1,500+ high-level Katarina games.

**Predictions include:**
- 🔪 Use Q (Bouncing Blade)
- ⚡ Use W (Preparation)
- ⚔️ Use E (Shunpo)
- 💀 Use R (Death Lotus)
- 🏃 Move/reposition
- 🛒 Back and buy items

## Requirements

1. **Trained model** at `D:\katarina_dataset\model\best_model.pt`
2. **Active League of Legends game** (Practice Tool or real game)
3. **Python packages**: `torch`, `requests`, `urllib3`

## Installation

```bash
# Install required packages if not already installed
pip install torch requests urllib3
```

## Usage

### Step 1: Start a League of Legends game
- Play as **Katarina** (any game mode)
- The Live Client API is automatically available when in-game

### Step 2: Run the AI Coach
```bash
python katarina_coach.py
```

### Step 3: Play and watch predictions
The coach will display real-time predictions like:

```
[14:23:45] ⚔️ Use E (Shunpo) (78.3% confidence)
           Alternatives: Use Q (12.4%), Move/reposition (5.2%)
           Cooldowns: Q:✓ W:✓ E:✓ R:✗ | Gold: 1250g

[14:23:47] 🔪 Use Q (82.1% confidence)
           Alternatives: Move/reposition (10.3%), Use W (4.1%)
           Cooldowns: Q:✓ W:✓ E:✗ R:✗ | Gold: 1250g

[14:23:50] 🛒 Back and buy (91.5% confidence)
           Alternatives: Move/reposition (5.2%), Use Q (2.1%)
           Cooldowns: Q:✓ W:✓ E:✓ R:✓ | Gold: 1250g
```

## How It Works

1. **Polls Live Client API** (`https://127.0.0.1:2999/liveclientdata/allgamedata`) every 0.5 seconds
2. **Tracks your actions**: position, ability usage, cooldowns
3. **Maintains a sliding window** of the last 32 actions
4. **Feeds to trained LSTM model** which predicts the next action
5. **Displays prediction** with confidence percentage every 2 seconds

## Features

- ✅ Real-time predictions (updates every 2 seconds)
- ✅ Shows confidence percentages
- ✅ Displays alternative suggestions
- ✅ Shows cooldown status for Q/W/E/R
- ✅ Warns when suggesting spells on cooldown
- ✅ Shows current gold amount
- ✅ 100% safe and Riot-approved (uses official Live Client API)

## Limitations

- **Only tracks your actions** - doesn't see enemy positions yet (coming soon with computer vision)
- **Basic movement tracking** - only detects significant position changes
- **No item recommendations** - just says "buy" but doesn't specify which item
- **Katarina only** - model was trained exclusively on Katarina gameplay

## Model Performance

- **Training data**: 1,500+ Katarina games from high-level replays
- **Validation accuracy**: ~55-58% overall
- **Best predictions**:
  - Buy decisions: 81% accuracy
  - Ultimate (R) timing: 67% accuracy
  - E (Shunpo) usage: 64% accuracy

## Troubleshooting

**"Waiting for game to start..."**
- Make sure you're in an active League game (not in champion select or lobby)
- The Live Client API only works during actual gameplay

**"Waiting for Katarina game..."**
- You must be playing as Katarina
- Check that you're not spectating

**"Failed to load model"**
- Make sure the trained model exists at `D:\katarina_dataset\model\best_model.pt`
- Run `train_katarina.py` first to train the model

**No predictions showing**
- The coach needs a few seconds to build action history
- Make sure you're moving around in the game

## Next Steps

### Planned features:
1. **Computer vision integration** - Detect enemy positions using LeagueAI/YOLO models
2. **Enemy cooldown tracking** - Manual timer system for enemy abilities
3. **Item recommendations** - Suggest specific items to buy
4. **Overlay UI** - Visual overlay on top of the game window
5. **Multi-champion support** - Train models for other champions

## Legal & ToS

✅ **100% Safe**: This tool only uses:
- Riot's official Live Client API (approved for third-party tools)
- Screen reading from your own client (no memory injection)
- No automation (you still control the champion)

This is equivalent to coaching apps like Blitz.gg, Mobalytics, and Porofessor.

## Credits

Built using:
- League of Legends replay dataset: `maknee/league-of-legends-decoded-replay-packets`
- PyTorch LSTM model
- Riot Games Live Client API

---

**Enjoy your AI coach!** 🎮⚔️
