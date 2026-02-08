"""Quick test to verify coach can start up"""
import torch
import torch.nn as nn

# Model configuration (must match training script)
ACTION_TYPES = ["spell_Q", "spell_W", "spell_E", "spell_R", "spell_other", "move", "attack", "buy"]
NUM_ACTIONS = len(ACTION_TYPES)
SEQ_LEN = 32
FEATURE_DIM = 18
HIDDEN_DIM = 128
NUM_LAYERS = 2

MODEL_PATH = r"D:\katarina_dataset\model\best_model.pt"

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

print("=" * 60)
print("TESTING COACH STARTUP")
print("=" * 60)
print()

# Test voice
try:
    import pyttsx3
    print("[OK] pyttsx3 installed")
except ImportError:
    print("[ERROR] pyttsx3 NOT installed")

# Test model loading
print(f"\nLoading model from {MODEL_PATH}...")
try:
    model = KatarinaPredictor()
    checkpoint = torch.load(MODEL_PATH, map_location='cpu', weights_only=False)

    # Handle both checkpoint formats
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
        val_acc = checkpoint.get('best_val_acc', 0)
    elif 'model_state' in checkpoint:
        model.load_state_dict(checkpoint['model_state'])
        val_acc = checkpoint.get('val_acc', 0)
    else:
        model.load_state_dict(checkpoint)
        val_acc = 0

    model.eval()
    print(f"[OK] Model loaded successfully (Epoch {checkpoint.get('epoch', '?')})")
    print(f"  Validation accuracy: {val_acc*100:.1f}%")
    print(f"  Model has {sum(p.numel() for p in model.parameters())} parameters")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("STARTUP TEST COMPLETE")
print("=" * 60)
