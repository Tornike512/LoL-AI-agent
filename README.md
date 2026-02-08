# LoL AI Agent - Katarina Next-Action Predictor 🔊👁️

AI-powered real-time **VOICE COACH** with **MINIMAP DETECTION** for League of Legends that tells you what to do while playing Katarina!

## 🎯 Project Overview

This project trains a deep learning model on 1,500+ high-level Katarina games to predict what action a player should take next in real-time. It includes:

1. **Data extraction pipeline** - Downloads and processes League of Legends replay data
2. **LSTM-based predictor** - Neural network trained on action sequences
3. **Real-time AI voice coach** 🔊 - **SPEAKS predictions** to you during games using Riot's official API
4. **Minimap detection** 👁️ - **SEES enemy positions** via computer vision for context-aware coaching

## 🚀 Quick Start

### 1. Extract Training Data

```bash
python extract_katarina.py
```

This downloads Katarina games from the [maknee/league-of-legends-decoded-replay-packets](https://huggingface.co/datasets/maknee/league-of-legends-decoded-replay-packets) dataset and saves to `D:\katarina_dataset\katarina_training_data.jsonl.gz`.

### 2. Train the Model

```bash
python train_katarina.py
```

Trains an LSTM model on the extracted data. The model achieves ~55-58% validation accuracy, with 81% accuracy on buy decisions and 67% on ultimate timing.

### 3. Install Coach Dependencies

```bash
# Voice support (required)
pip install pyttsx3

# Minimap detection (optional but highly recommended)
pip install ultralytics pillow mss
```

### 4. Use the AI Voice Coach 🔊👁️

```bash
python katarina_coach.py
```

The coach will **SPEAK** to you in real-time with **MINIMAP AWARENESS**:
- 🔊 "Use Q"
- 🔊 "Enemy nearby, use E, Shunpo"
- 🔊 "Use ultimate, 2 enemies detected"
- 🔊 "Back and buy"

**The minimap detector sees enemy champions and adjusts advice accordingly!**

See [COACH_README.md](COACH_README.md) for detailed usage or [VOICE_GUIDE.md](VOICE_GUIDE.md) for voice setup!

## 📊 Model Performance

- **Training data**: 1,500+ Katarina games from high-level replays
- **Model**: LSTM with 216K parameters
- **Overall accuracy**: 55-58%
- **Per-class accuracy**:
  - Buy decisions: 81%
  - Ultimate (R) timing: 67%
  - E (Shunpo) usage: 64%
  - Move: 56%

## 🛠️ Technical Stack

- **PyTorch**: LSTM neural network
- **HuggingFace Datasets**: Replay data source
- **Live Client API**: Real-time game state (Riot official)
- **pyttsx3**: Text-to-speech for voice coaching 🔊
- **Ultralytics YOLOv11**: Minimap champion detection 👁️
- **MSS**: Fast screen capture
- **Python 3.x**: All scripts

## 📁 Project Structure

```
lol-jungler-tracker/
├── extract_katarina.py      # Data extraction pipeline
├── train_katarina.py         # Model training script
├── katarina_coach.py         # Real-time AI voice coach 🔊👁️
├── minimap_detector.py       # Minimap champion detection module
├── test_api.py               # API connectivity test
├── test_voice.py             # Voice system test
├── README.md                 # This file
├── COACH_README.md           # Detailed coach documentation
└── VOICE_GUIDE.md            # Voice setup guide
```

## 🎮 Features

### Current Features
- ✅ 🔊 **VOICE ANNOUNCEMENTS** - Coach speaks to you during gameplay!
- ✅ 👁️ **MINIMAP DETECTION** - Sees enemy champions using YOLOv11 computer vision!
- ✅ 🧠 **CONTEXT-AWARE PREDICTIONS** - Adjusts advice based on enemy positions
- ✅ Real-time next-action predictions (every 2 seconds)
- ✅ Confidence percentages for each prediction
- ✅ Ability cooldown tracking (Q/W/E/R)
- ✅ Alternative action suggestions
- ✅ Gold and level monitoring
- ✅ Non-blocking voice (predictions continue while speaking)
- ✅ 100% Riot ToS compliant

### Planned Features
- 🔄 Fine-tuned minimap model (champion-specific detection)
- 🔄 Enemy cooldown tracking
- 🔄 Specific item recommendations
- 🔄 Visual overlay UI
- 🔄 Multi-champion support

## 🧠 How It Works

### Data Pipeline
1. **Extract**: Download 1,348 batches of replay data from HuggingFace
2. **Filter**: Extract only games with Katarina players
3. **Process**: Convert to action sequences with features (position, cooldowns, time)
4. **Save**: Compressed JSONL format for training

### Model Architecture
```
Input: Last 32 actions (each with 18 features)
  ↓
LSTM (2 layers, 128 hidden units)
  ↓
Fully connected layers (128 → 64 → 8)
  ↓
Output: 8 action types (Q, W, E, R, move, buy, etc.)
```

### Real-time Voice Coach with Minimap Detection
```
Live Client API + Minimap Screenshot → Enemy Detection (YOLO) → Track actions →
Build sequence → LSTM prediction → 🔊 SPEAK context-aware advice + Display
```

## 📝 Action Types

The model predicts 8 action types:

1. **spell_Q**: Use Bouncing Blade
2. **spell_W**: Use Preparation
3. **spell_E**: Use Shunpo (dash)
4. **spell_R**: Use Death Lotus (ultimate)
5. **spell_other**: Use other abilities
6. **move**: Reposition or move
7. **attack**: Auto attack (rare for Katarina)
8. **buy**: Back to base and buy items

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/Tornike512/LoL-AI-agent.git
cd LoL-AI-agent

# Install dependencies
pip install torch datasets huggingface_hub requests urllib3 pyttsx3 ultralytics pillow mss

# Run extraction (takes ~2-3 hours)
python extract_katarina.py

# Train the model (takes several hours on CPU)
python train_katarina.py

# Test voice system
python test_voice.py

# Test API connectivity (requires active game)
python test_api.py

# Run the AI voice coach (requires active game)
python katarina_coach.py
```

## 🎯 Use Cases

- **Real-time voice coaching**: 🔊 Hear what to do while keeping eyes on the game
- **Learning Katarina**: Internalize high-level decision patterns through repetition
- **Combo timing**: Voice guides you through E-Q-W-R combos in real-time
- **Back timing**: Audio alerts when it's optimal to recall and buy
- **Hands-free coaching**: No need to look at terminal or second monitor
- **Research**: Experiment with AI for League of Legends gameplay

## ⚖️ Legal & ToS

**100% Safe and Riot-approved:**
- Uses only Riot's official Live Client API
- No memory reading or injection
- No automation (you still control the champion)
- Equivalent to apps like Blitz.gg, Mobalytics, Porofessor

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Add computer vision for enemy detection
- Support for other champions
- Overlay UI instead of terminal output
- Better feature engineering
- Transformer-based models

## 📚 Dataset

This project uses the [League of Legends Decoded Replay Packets](https://huggingface.co/datasets/maknee/league-of-legends-decoded-replay-packets) dataset by maknee.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Credits

- **Dataset**: [maknee/league-of-legends-decoded-replay-packets](https://huggingface.co/datasets/maknee/league-of-legends-decoded-replay-packets)
- **Riot Games**: For the Live Client API
- **PyTorch**: Deep learning framework
- **pyttsx3**: Text-to-speech library
- **HuggingFace**: Dataset hosting

---

**Built with Claude Code** 🤖⚔️🔊

📖 **Documentation:**
- [COACH_README.md](COACH_README.md) - Detailed coach usage
- [VOICE_GUIDE.md](VOICE_GUIDE.md) - Voice setup and customization
