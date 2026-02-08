"""
Train a next-action predictor for Katarina using extracted replay data.

Model: LSTM sequence model
Input: Window of recent actions (type, position, timing, cooldowns, etc.)
Output: Predicted next action type + parameters

Usage:
    python train_katarina.py                    # train from scratch
    python train_katarina.py --resume           # resume from checkpoint
    python train_katarina.py --eval             # evaluate only
"""

import json
import gzip
import zlib
import os
import sys
import random
import math
import argparse
from collections import Counter

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# ============================================================
# Configuration
# ============================================================

DATA_FILE = r"D:\katarina_dataset\katarina_training_data.jsonl.gz"
MODEL_DIR = r"D:\katarina_dataset\model"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Action types the model predicts
ACTION_TYPES = [
    "spell_Q", "spell_W", "spell_E", "spell_R",
    "spell_other",  # summoner spells, item actives
    "move",
    "attack",
    "buy",
]
NUM_ACTIONS = len(ACTION_TYPES)

# Spell name -> action type mapping
SPELL_SLOTS = {
    "KatarinaQ": "spell_Q",
    "KatarinaW": "spell_W",
    "KatarinaEWrapper": "spell_E",
    "KatarinaE": "spell_E",
    "KatarinaR": "spell_R",
}

# Training params
SEQ_LEN = 32          # number of past actions to look at
FEATURE_DIM = 18      # features per action step
HIDDEN_DIM = 128      # LSTM hidden size
NUM_LAYERS = 2        # LSTM layers
BATCH_SIZE = 256
LEARNING_RATE = 0.001
EPOCHS = 20
VAL_SPLIT = 0.1       # 10% validation


# ============================================================
# Feature Engineering
# ============================================================

# Map coordinates: LoL map is roughly -7000 to 7000 on each axis
MAP_MIN = -7500.0
MAP_MAX = 7500.0

def norm_pos(val):
    """Normalize a map coordinate to [0, 1]."""
    return max(0.0, min(1.0, (val - MAP_MIN) / (MAP_MAX - MAP_MIN)))

def norm_time(dt):
    """Normalize time delta (seconds) — cap at 60s."""
    return min(dt / 60.0, 1.0)

def action_to_type_idx(action):
    """Convert an action dict to its action type index."""
    t = action["type"]
    if t == "spell":
        spell_name = action.get("name", "")
        mapped = SPELL_SLOTS.get(spell_name, "spell_other")
        return ACTION_TYPES.index(mapped)
    elif t == "move":
        return ACTION_TYPES.index("move")
    elif t == "attack":
        return ACTION_TYPES.index("attack")
    elif t == "buy":
        return ACTION_TYPES.index("buy")
    else:
        return -1  # skip dmg_out, dmg_in, cooldown, death, kill as prediction targets

def action_to_features(action, prev_time, cooldowns):
    """Convert a single action to a fixed-size feature vector.

    Features (18 total):
        [0-7]   one-hot action type (8 classes)
        [8-9]   normalized source position (x, z)
        [10-11] normalized target position (x, z)
        [12]    time delta from previous action (normalized)
        [13]    absolute game time (normalized to 0-1 over 40 min)
        [14-17] cooldown state for Q, W, E, R (normalized remaining cd)
    """
    feat = [0.0] * FEATURE_DIM

    # Action type one-hot
    idx = action_to_type_idx(action)
    if idx >= 0:
        feat[idx] = 1.0
    else:
        # For non-predictable events, encode type info
        t = action["type"]
        if t == "dmg_out":
            feat[0] = 0.3  # partial activation to signal damage
        elif t == "dmg_in":
            feat[1] = 0.3
        elif t in ("death", "kill"):
            feat[2] = 0.3
        elif t == "cooldown":
            feat[3] = 0.3

    # Source position
    feat[8] = norm_pos(action.get("x", 0))
    feat[9] = norm_pos(action.get("z", 0))

    # Target position
    if "tx" in action:
        feat[10] = norm_pos(action["tx"])
        feat[11] = norm_pos(action["tz"])
    elif "waypoints" in action and action["waypoints"]:
        last_wp = action["waypoints"][-1]
        feat[10] = norm_pos(last_wp["x"])
        feat[11] = norm_pos(last_wp["z"])
    else:
        feat[10] = feat[8]
        feat[11] = feat[9]

    # Time features
    current_time = action.get("t", 0)
    dt = current_time - prev_time if prev_time is not None else 0
    feat[12] = norm_time(dt)
    feat[13] = min(current_time / 2400.0, 1.0)  # normalize to 40 min game

    # Cooldown state: update from cooldown events and decay over time
    if action["type"] == "cooldown":
        slot = action.get("slot", -1)
        if 0 <= slot <= 3:
            cooldowns[slot] = action.get("cd", 0)
    elif action["type"] == "spell":
        slot_name = SPELL_SLOTS.get(action.get("name", ""), "")
        slot_map = {"spell_Q": 0, "spell_W": 1, "spell_E": 2, "spell_R": 3}
        if slot_name in slot_map:
            cooldowns[slot_map[slot_name]] = action.get("cd", 0)

    # Decay cooldowns by time delta
    for i in range(4):
        cooldowns[i] = max(0, cooldowns[i] - dt)
        feat[14 + i] = min(cooldowns[i] / 20.0, 1.0)  # normalize to 20s max cd

    return feat


# ============================================================
# Dataset
# ============================================================

class KatarinaActionDataset(Dataset):
    """Generates (sequence, next_action) pairs from Katarina games."""

    def __init__(self, games):
        self.samples = []
        self._build_samples(games)

    def _build_samples(self, games):
        for game in games:
            actions = game["actions"]
            if len(actions) < SEQ_LEN + 1:
                continue

            # Build feature sequences and find predictable actions
            features = []
            cooldowns = [0.0, 0.0, 0.0, 0.0]
            prev_time = 0.0

            for action in actions:
                feat = action_to_features(action, prev_time, cooldowns)
                features.append(feat)
                prev_time = action.get("t", 0)

            # Create training samples: for each predictable action, use previous SEQ_LEN actions as input
            for i in range(SEQ_LEN, len(actions)):
                target_idx = action_to_type_idx(actions[i])
                if target_idx < 0:
                    continue  # skip non-predictable actions as targets

                seq = features[i - SEQ_LEN:i]
                self.samples.append((seq, target_idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        seq, target = self.samples[idx]
        return torch.tensor(seq, dtype=torch.float32), torch.tensor(target, dtype=torch.long)


# ============================================================
# Model
# ============================================================

class KatarinaPredictor(nn.Module):
    """LSTM-based next-action predictor."""

    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=FEATURE_DIM,
            hidden_size=HIDDEN_DIM,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=0.2,
        )
        self.fc = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, NUM_ACTIONS),
        )

    def forward(self, x):
        # x: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]  # take last timestep
        return self.fc(last_hidden)


# ============================================================
# Training
# ============================================================

def load_games():
    """Load all Katarina games from the compressed file.
    Handles truncated gzip (e.g. if extraction is still running)."""
    print(f"Loading data from {DATA_FILE}...")
    games = []
    try:
        with gzip.open(DATA_FILE, "rt") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        games.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (EOFError, zlib.error, OSError):
        print(f"  (file still being written — loaded what's available)")
    print(f"Loaded {len(games)} Katarina games")
    return games


def train(resume=False):
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Load data
    games = load_games()
    random.shuffle(games)

    # Split into train/val
    val_size = max(1, int(len(games) * VAL_SPLIT))
    val_games = games[:val_size]
    train_games = games[val_size:]
    print(f"Train: {len(train_games)} games, Val: {len(val_games)} games")

    # Build datasets
    print("Building training samples...")
    train_dataset = KatarinaActionDataset(train_games)
    val_dataset = KatarinaActionDataset(val_games)
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")

    if len(train_dataset) == 0:
        print("ERROR: No training samples generated. Check your data.")
        return

    # Print class distribution
    train_labels = [s[1] for s in train_dataset.samples]
    label_counts = Counter(train_labels)
    print("\nAction distribution in training set:")
    for i, name in enumerate(ACTION_TYPES):
        count = label_counts.get(i, 0)
        pct = 100 * count / len(train_labels) if train_labels else 0
        print(f"  {name:15s}: {count:>8d} ({pct:5.1f}%)")

    # Compute class weights for imbalanced data
    total = sum(label_counts.values())
    weights = []
    for i in range(NUM_ACTIONS):
        c = label_counts.get(i, 1)
        weights.append(total / (NUM_ACTIONS * c))
    class_weights = torch.tensor(weights, dtype=torch.float32).to(DEVICE)
    print(f"\nClass weights: {[f'{w:.2f}' for w in weights]}")

    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Model
    model = KatarinaPredictor().to(DEVICE)
    start_epoch = 0

    if resume:
        ckpt_path = os.path.join(MODEL_DIR, "checkpoint.pt")
        if os.path.exists(ckpt_path):
            checkpoint = torch.load(ckpt_path, map_location=DEVICE)
            model.load_state_dict(checkpoint["model_state"])
            start_epoch = checkpoint.get("epoch", 0)
            print(f"Resumed from epoch {start_epoch}")

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)

    param_count = sum(p.numel() for p in model.parameters())
    print(f"\nModel parameters: {param_count:,}")
    print(f"Device: {DEVICE}")
    print(f"{'='*60}")

    best_val_acc = 0.0

    for epoch in range(start_epoch, EPOCHS):
        # Training
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item() * inputs.size(0)
            preds = outputs.argmax(dim=1)
            train_correct += (preds == targets).sum().item()
            train_total += inputs.size(0)

            if (batch_idx + 1) % 50 == 0:
                batch_acc = 100 * train_correct / train_total
                print(f"  Epoch {epoch+1} [{batch_idx+1}/{len(train_loader)}] "
                      f"Loss: {train_loss/train_total:.4f} Acc: {batch_acc:.1f}%")

        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / train_total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        per_class_correct = [0] * NUM_ACTIONS
        per_class_total = [0] * NUM_ACTIONS

        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
                outputs = model(inputs)
                loss = criterion(outputs, targets)

                val_loss += loss.item() * inputs.size(0)
                preds = outputs.argmax(dim=1)
                val_correct += (preds == targets).sum().item()
                val_total += inputs.size(0)

                for i in range(NUM_ACTIONS):
                    mask = targets == i
                    per_class_correct[i] += (preds[mask] == i).sum().item()
                    per_class_total[i] += mask.sum().item()

        val_acc = 100 * val_correct / val_total if val_total else 0
        avg_val_loss = val_loss / val_total if val_total else 0

        scheduler.step(avg_val_loss)

        print(f"\nEpoch {epoch+1}/{EPOCHS}: "
              f"Train Loss={avg_train_loss:.4f} Acc={train_acc:.1f}% | "
              f"Val Loss={avg_val_loss:.4f} Acc={val_acc:.1f}%")

        # Per-class accuracy
        print("  Per-class validation accuracy:")
        for i, name in enumerate(ACTION_TYPES):
            if per_class_total[i] > 0:
                acc = 100 * per_class_correct[i] / per_class_total[i]
                print(f"    {name:15s}: {acc:5.1f}% ({per_class_correct[i]}/{per_class_total[i]})")
        print()

        # Save checkpoint
        checkpoint = {
            "epoch": epoch + 1,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "val_acc": val_acc,
            "train_acc": train_acc,
        }
        torch.save(checkpoint, os.path.join(MODEL_DIR, "checkpoint.pt"))

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(checkpoint, os.path.join(MODEL_DIR, "best_model.pt"))
            print(f"  >> New best model! Val accuracy: {val_acc:.1f}%")

    print(f"\n{'='*60}")
    print(f"Training complete! Best validation accuracy: {best_val_acc:.1f}%")
    print(f"Model saved to: {MODEL_DIR}")


def evaluate():
    """Load the best model and show detailed evaluation."""
    model_path = os.path.join(MODEL_DIR, "best_model.pt")
    if not os.path.exists(model_path):
        print("No trained model found. Run training first.")
        return

    games = load_games()
    val_size = max(1, int(len(games) * VAL_SPLIT))

    # Use same split as training (need same seed)
    random.seed(42)
    random.shuffle(games)
    val_games = games[:val_size]

    val_dataset = KatarinaActionDataset(val_games)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = KatarinaPredictor().to(DEVICE)
    checkpoint = torch.load(model_path, map_location=DEVICE)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    print(f"\nLoaded best model (val acc: {checkpoint.get('val_acc', '?'):.1f}%)")
    print(f"Evaluating on {len(val_dataset)} samples...\n")

    # Confusion matrix
    confusion = [[0] * NUM_ACTIONS for _ in range(NUM_ACTIONS)]

    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(DEVICE), targets.to(DEVICE)
            outputs = model(inputs)
            preds = outputs.argmax(dim=1)

            for true, pred in zip(targets.cpu().numpy(), preds.cpu().numpy()):
                confusion[true][pred] += 1

    # Print confusion matrix
    print("Confusion Matrix (rows=true, cols=predicted):")
    header = "              " + " ".join(f"{n[:7]:>7s}" for n in ACTION_TYPES)
    print(header)
    for i, name in enumerate(ACTION_TYPES):
        row = " ".join(f"{confusion[i][j]:>7d}" for j in range(NUM_ACTIONS))
        total = sum(confusion[i])
        acc = 100 * confusion[i][i] / total if total else 0
        print(f"  {name:12s} {row}  ({acc:.1f}%)")

    total_correct = sum(confusion[i][i] for i in range(NUM_ACTIONS))
    total_samples = sum(sum(row) for row in confusion)
    print(f"\nOverall accuracy: {100*total_correct/total_samples:.1f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Katarina next-action predictor")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--eval", action="store_true", help="Evaluate only")
    args = parser.parse_args()

    if args.eval:
        evaluate()
    else:
        train(resume=args.resume)
