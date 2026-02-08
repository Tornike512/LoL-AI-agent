# LoL AI Agent - Katarina Next-Action Predictor

AI-powered real-time coach for League of Legends that predicts optimal next actions for Katarina gameplay.

## 🎯 Project Overview

This project trains a deep learning model on 1,500+ high-level Katarina games to predict what action a player should take next in real-time. It includes:

1. **Data extraction pipeline** - Downloads and processes League of Legends replay data
2. **LSTM-based predictor** - Neural network trained on action sequences
3. **Real-time AI coach** - Live predictions during your games using Riot's official API

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

### 3. Use the AI Coach

```bash
python katarina_coach.py
```

Connects to your live League game and provides real-time action predictions!

See [COACH_README.md](COACH_README.md) for detailed usage instructions.

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
- **Python 3.x**: All scripts

## 📁 Project Structure

```
lol-jungler-tracker/
├── extract_katarina.py      # Data extraction pipeline
├── train_katarina.py         # Model training script
├── katarina_coach.py         # Real-time AI coach
├── test_api.py               # API connectivity test
├── COACH_README.md           # Detailed coach documentation
└── README.md                 # This file
```

## 🎮 Features

### Current Features
- ✅ Real-time next-action predictions
- ✅ Confidence percentages for each prediction
- ✅ Ability cooldown tracking (Q/W/E/R)
- ✅ Alternative action suggestions
- ✅ Gold and level monitoring
- ✅ 100% Riot ToS compliant

### Planned Features
- 🔄 Computer vision for enemy position detection
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

### Real-time Coach
```
Live Client API → Track actions → Build sequence → Model prediction → Display
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
pip install torch datasets huggingface_hub requests urllib3

# Run extraction (takes ~2-3 hours)
python extract_katarina.py

# Train the model (takes several hours on CPU)
python train_katarina.py

# Test API connectivity (requires active game)
python test_api.py

# Run the AI coach (requires active game)
python katarina_coach.py
```

## 🎯 Use Cases

- **Learning Katarina**: See what high-level players typically do in similar situations
- **Combo timing**: Learn when to engage with E-Q-W-R combos
- **Back timing**: Model predicts optimal times to recall and buy
- **Replay analysis**: Understand decision patterns
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
- **HuggingFace**: Dataset hosting

---

**Built with Claude Code** 🤖⚔️

For detailed AI coach usage, see [COACH_README.md](COACH_README.md)
