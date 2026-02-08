"""
Katarina AI Coach - Real-time next-action predictor with VOICE

Connects to League of Legends Live Client API and uses the trained LSTM model
to predict Katarina's next action in real-time during a game.

NOW WITH VOICE ANNOUNCEMENTS! The coach will speak predictions to you.

Requirements:
- Must be in an active League of Legends game
- Trained model at D:\katarina_dataset\model\best_model.pt
- Live Client API available at https://127.0.0.1:2999/liveclientdata/allgamedata
- pyttsx3 for text-to-speech (install: pip install pyttsx3)

Usage:
    python katarina_coach.py
    python katarina_coach.py --no-voice  (disable voice)
"""

import torch
import torch.nn as nn
import requests
import urllib3
import time
import json
import sys
import threading
from collections import deque
from datetime import datetime

# Text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not installed. Voice disabled. Install with: pip install pyttsx3")

# Suppress SSL warnings (Live Client API uses self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Model configuration (must match training script)
ACTION_TYPES = ["spell_Q", "spell_W", "spell_E", "spell_R", "spell_other", "move", "attack", "buy"]
NUM_ACTIONS = len(ACTION_TYPES)
SEQ_LEN = 32
FEATURE_DIM = 18
HIDDEN_DIM = 128
NUM_LAYERS = 2

# Live Client API endpoint
API_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"

# Model path
MODEL_PATH = r"D:\katarina_dataset\model\best_model.pt"

# Spell slot mapping
SPELL_SLOTS = {
    "KatarinaQ": "Q",
    "KatarinaW": "W",
    "KatarinaEWrapper": "E",
    "KatarinaE": "E",
    "KatarinaR": "R"
}


class KatarinaPredictor(nn.Module):
    """LSTM model for predicting next action"""
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=FEATURE_DIM,
            hidden_size=HIDDEN_DIM,
            num_layers=NUM_LAYERS,
            batch_first=True,
            dropout=0.2
        )
        self.fc = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, NUM_ACTIONS)
        )

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        return self.fc(last_output)


class ActionHistory:
    """Maintains a sliding window of recent actions"""
    def __init__(self, seq_len=SEQ_LEN):
        self.seq_len = seq_len
        self.history = deque(maxlen=seq_len)
        self.last_game_time = 0

    def add_action(self, action_type, source_pos, target_pos, game_time, cooldowns):
        """Add an action to the history"""
        # Calculate time delta
        time_delta = game_time - self.last_game_time if self.last_game_time > 0 else 0
        self.last_game_time = game_time

        # Create feature vector (18 features)
        # One-hot action type (8) + source pos (2) + target pos (2) + time delta (1) + game time (1) + cooldowns (4)
        features = [0.0] * FEATURE_DIM

        # One-hot encode action type
        if action_type in ACTION_TYPES:
            idx = ACTION_TYPES.index(action_type)
            features[idx] = 1.0

        # Normalize positions (League map is ~15000 units)
        features[8] = source_pos[0] / 15000.0
        features[9] = source_pos[1] / 15000.0
        features[10] = target_pos[0] / 15000.0
        features[11] = target_pos[1] / 15000.0

        # Time features (normalize to reasonable ranges)
        features[12] = min(time_delta / 10.0, 1.0)  # Cap at 10 seconds
        features[13] = game_time / 3600.0  # Normalize by 1 hour

        # Cooldown states (1 = ready, 0 = on cooldown)
        features[14] = 1.0 if cooldowns.get('Q', True) else 0.0
        features[15] = 1.0 if cooldowns.get('W', True) else 0.0
        features[16] = 1.0 if cooldowns.get('E', True) else 0.0
        features[17] = 1.0 if cooldowns.get('R', True) else 0.0

        self.history.append(features)

    def get_sequence(self):
        """Get the current sequence as a tensor"""
        # Pad if we don't have enough history yet
        if len(self.history) < self.seq_len:
            padding = [[0.0] * FEATURE_DIM] * (self.seq_len - len(self.history))
            sequence = list(padding) + list(self.history)
        else:
            sequence = list(self.history)

        return torch.tensor([sequence], dtype=torch.float32)


def get_game_data():
    """Fetch data from Live Client API"""
    try:
        response = requests.get(API_URL, verify=False, timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None


def get_player_data(game_data, champion_name="Katarina"):
    """Extract player-specific data from game state"""
    if not game_data:
        return None

    # Find the active player (should be Katarina)
    active_player = game_data.get("activePlayer", {})

    # Verify we're playing Katarina
    if active_player.get("championStats", {}).get("championName") != champion_name:
        return None

    # Extract relevant data
    abilities = active_player.get("abilities", {})
    position = active_player.get("position", {"x": 0, "z": 0})

    # Get cooldown states for Q, W, E, R
    cooldowns = {}
    for ability_key in ["Q", "W", "E", "R"]:
        ability = abilities.get(ability_key, {})
        # Ability is ready if abilityLevel > 0 and cooldown is 0
        is_ready = (ability.get("abilityLevel", 0) > 0 and
                   ability.get("cooldown", 1) == 0)
        cooldowns[ability_key] = is_ready

    return {
        "position": (position.get("x", 0), position.get("z", 0)),
        "cooldowns": cooldowns,
        "game_time": game_data.get("gameData", {}).get("gameTime", 0),
        "level": active_player.get("level", 1),
        "current_gold": active_player.get("currentGold", 0)
    }


def predict_next_action(model, action_history):
    """Use the model to predict the next action"""
    sequence = action_history.get_sequence()

    with torch.no_grad():
        output = model(sequence)
        probabilities = torch.softmax(output, dim=1)
        predicted_idx = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_idx].item()

    return ACTION_TYPES[predicted_idx], confidence, probabilities[0]


def format_prediction(action, confidence, cooldowns):
    """Format the prediction for display"""
    # Map action to human-readable format
    action_display = {
        "spell_Q": "🔪 Use Q",
        "spell_W": "⚡ Use W",
        "spell_E": "⚔️ Use E (Shunpo)",
        "spell_R": "💀 Use R (Death Lotus)",
        "spell_other": "✨ Use ability",
        "move": "🏃 Move/reposition",
        "attack": "⚔️ Auto attack",
        "buy": "🛒 Back and buy"
    }

    display = action_display.get(action, action)

    # Add cooldown warning if suggesting a spell that's on cooldown
    spell_map = {
        "spell_Q": "Q",
        "spell_W": "W",
        "spell_E": "E",
        "spell_R": "R"
    }

    if action in spell_map:
        spell = spell_map[action]
        if not cooldowns.get(spell, True):
            display += " ⏳ (ON COOLDOWN)"

    return f"{display} ({confidence*100:.1f}% confidence)"


def get_voice_message(action, confidence, cooldowns):
    """Convert action to spoken message"""
    # Map action to voice-friendly phrases
    voice_messages = {
        "spell_Q": "Use Q",
        "spell_W": "Use W",
        "spell_E": "Use E, Shunpo",
        "spell_R": "Use ultimate",
        "spell_other": "Use ability",
        "move": "Reposition",
        "attack": "Auto attack",
        "buy": "Back and buy"
    }

    message = voice_messages.get(action, action)

    # Check if spell is on cooldown
    spell_map = {
        "spell_Q": "Q",
        "spell_W": "W",
        "spell_E": "E",
        "spell_R": "R"
    }

    if action in spell_map:
        spell = spell_map[action]
        if not cooldowns.get(spell, True):
            message = f"{message}, but it's on cooldown"

    # Add confidence for high-confidence predictions
    if confidence > 0.75:
        return message
    else:
        return f"Consider {message}"


class VoiceCoach:
    """Handles text-to-speech in a separate thread"""
    def __init__(self, enabled=True):
        self.enabled = enabled and TTS_AVAILABLE
        self.engine = None
        self.lock = threading.Lock()

        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                # Set properties for better gaming experience
                self.engine.setProperty('rate', 175)  # Speed (default 200)
                self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

                # Try to use a female voice if available (sounds less robotic)
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break

                print("✓ Voice coach enabled")
            except Exception as e:
                print(f"✗ Voice initialization failed: {e}")
                self.enabled = False

    def speak(self, message):
        """Speak a message (non-blocking)"""
        if not self.enabled:
            return

        def _speak():
            with self.lock:
                try:
                    self.engine.say(message)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Voice error: {e}")

        # Run in separate thread so it doesn't block predictions
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()


def main():
    # Check for --no-voice flag
    use_voice = "--no-voice" not in sys.argv

    print("=" * 60)
    print("   KATARINA AI COACH - Real-time Next-Action Predictor")
    if use_voice and TTS_AVAILABLE:
        print("                    🔊 WITH VOICE 🔊")
    print("=" * 60)
    print()

    # Initialize voice coach
    voice_coach = VoiceCoach(enabled=use_voice)

    # Load the trained model
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = KatarinaPredictor()
        checkpoint = torch.load(MODEL_PATH, map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        print(f"✓ Model loaded successfully (Epoch {checkpoint.get('epoch', '?')})")
        print(f"  Best validation accuracy: {checkpoint.get('best_val_acc', 0)*100:.1f}%")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return

    print()
    print("Waiting for game to start...")
    print("(Make sure you're in an active League of Legends game)")
    if use_voice:
        print("(Voice announcements will guide you during gameplay)")
    print()

    action_history = ActionHistory()
    last_position = None
    last_prediction_time = 0
    prediction_interval = 2.0  # Predict every 2 seconds

    game_started = False

    while True:
        try:
            # Get game data from API
            game_data = get_game_data()

            if not game_data:
                if game_started:
                    print("\n[!] Lost connection to game")
                    game_started = False
                time.sleep(2)
                continue

            # Extract player data
            player_data = get_player_data(game_data)

            if not player_data:
                print("\r[!] Waiting for Katarina game...", end="", flush=True)
                time.sleep(2)
                continue

            if not game_started:
                print("\n✓ Game detected! Katarina AI Coach is now active.\n")
                print("=" * 60)
                game_started = True

            # Track movement as an action
            current_pos = player_data["position"]
            game_time = player_data["game_time"]

            # Add movement action if position changed significantly
            if last_position:
                distance = ((current_pos[0] - last_position[0])**2 +
                           (current_pos[1] - last_position[1])**2)**0.5

                if distance > 50:  # Moved significantly
                    action_history.add_action(
                        "move",
                        last_position,
                        current_pos,
                        game_time,
                        player_data["cooldowns"]
                    )

            last_position = current_pos

            # Make prediction periodically
            current_time = time.time()
            if current_time - last_prediction_time >= prediction_interval:
                if len(action_history.history) > 5:  # Need some history
                    action, confidence, probs = predict_next_action(model, action_history)

                    # Display prediction
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    prediction_text = format_prediction(action, confidence, player_data["cooldowns"])

                    print(f"[{timestamp}] {prediction_text}")

                    # VOICE ANNOUNCEMENT - Speak the prediction
                    voice_message = get_voice_message(action, confidence, player_data["cooldowns"])
                    voice_coach.speak(voice_message)

                    # Show top 3 predictions
                    top3_indices = torch.topk(probs, 3).indices.tolist()
                    top3_probs = torch.topk(probs, 3).values.tolist()

                    alternatives = []
                    for idx, prob in zip(top3_indices[1:], top3_probs[1:]):
                        alternatives.append(f"{ACTION_TYPES[idx]} ({prob*100:.1f}%)")

                    if alternatives:
                        print(f"           Alternatives: {', '.join(alternatives)}")

                    # Show cooldown status
                    cd_status = []
                    for spell in ['Q', 'W', 'E', 'R']:
                        status = "✓" if player_data["cooldowns"][spell] else "✗"
                        cd_status.append(f"{spell}:{status}")
                    print(f"           Cooldowns: {' '.join(cd_status)} | Gold: {player_data['current_gold']}g")
                    print()

                last_prediction_time = current_time

            time.sleep(0.5)  # Poll every 0.5 seconds

        except KeyboardInterrupt:
            print("\n\n[!] AI Coach stopped by user")
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()
