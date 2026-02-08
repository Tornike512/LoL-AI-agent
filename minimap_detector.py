"""
Minimap Champion Detection Module

Captures the League of Legends minimap from screen and detects champion positions
using computer vision (YOLO-based object detection).

This provides the critical missing context for the AI coach - knowing where
enemies are visible on the minimap enables much better predictions.
"""

import mss
import numpy as np
from PIL import Image
import torch
from ultralytics import YOLO
import time
from typing import List, Dict, Tuple, Optional


class MinimapDetector:
    """Detects champions on League of Legends minimap using computer vision"""

    def __init__(self, minimap_region: Optional[Dict] = None, use_pretrained: bool = True):
        """
        Initialize the minimap detector

        Args:
            minimap_region: Dict with 'top', 'left', 'width', 'height' for minimap location
                          If None, uses default 1920x1080 bottom-right location
            use_pretrained: Whether to use a pretrained YOLO model (will download if needed)
        """
        self.minimap_region = minimap_region or {
            'top': 800,      # Minimap typically in bottom-right
            'left': 1650,
            'width': 250,
            'height': 250
        }

        self.screen_capture = mss.mss()

        # Initialize YOLO model
        # For now, use a lightweight YOLOv11n model
        # TODO: Fine-tune on League minimap dataset from Roboflow
        if use_pretrained:
            print("[INFO] Loading YOLO11n model for minimap detection...")
            self.model = YOLO('yolo11n.pt')  # Lightweight nano model
            print("[OK] Model loaded")
        else:
            self.model = None
            print("[WARNING] No model loaded - detection disabled")

        self.last_detection_time = 0
        self.detection_cache = []

    def capture_minimap(self) -> np.ndarray:
        """
        Capture the minimap region from screen

        Returns:
            numpy array of the minimap image (RGB)
        """
        screenshot = self.screen_capture.grab(self.minimap_region)
        img = np.array(screenshot)
        # Convert BGRA to RGB
        img = img[:, :, :3]
        return img

    def detect_champions(self, minimap_img: Optional[np.ndarray] = None,
                        confidence_threshold: float = 0.3) -> List[Dict]:
        """
        Detect champions on the minimap

        Args:
            minimap_img: Optional pre-captured minimap image. If None, captures now
            confidence_threshold: Minimum confidence for detections

        Returns:
            List of detected champions with positions:
            [
                {
                    'champion': 'unknown',  # Will be 'unknown' until model is fine-tuned
                    'x': 0.5,  # Normalized x position (0-1)
                    'y': 0.5,  # Normalized y position (0-1)
                    'confidence': 0.85,
                    'is_ally': False,  # Will be False until we can distinguish
                    'visible': True
                },
                ...
            ]
        """
        if self.model is None:
            return []

        # Capture minimap if not provided
        if minimap_img is None:
            minimap_img = self.capture_minimap()

        # Run YOLO detection
        results = self.model(minimap_img, verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                if confidence < confidence_threshold:
                    continue

                # Get bounding box
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Calculate center and normalize to 0-1 range
                center_x = (x1 + x2) / 2 / minimap_img.shape[1]
                center_y = (y1 + y2) / 2 / minimap_img.shape[0]

                # Class ID (will need to map to champion names after fine-tuning)
                class_id = int(box.cls[0])

                detections.append({
                    'champion': 'unknown',  # Generic until fine-tuned
                    'class_id': class_id,
                    'x': center_x,
                    'y': center_y,
                    'confidence': confidence,
                    'is_ally': False,  # Can't determine yet
                    'visible': True
                })

        self.detection_cache = detections
        self.last_detection_time = time.time()

        return detections

    def get_enemy_count_nearby(self, player_x: float, player_y: float,
                               radius: float = 0.3) -> int:
        """
        Count enemies near player position

        Args:
            player_x: Player's normalized x position (0-1)
            player_y: Player's normalized y position (0-1)
            radius: Search radius (normalized, default 0.3 = 30% of map)

        Returns:
            Number of detected champions near player (excluding player)
        """
        if not self.detection_cache:
            return 0

        nearby_count = 0
        for detection in self.detection_cache:
            # Calculate distance
            dx = detection['x'] - player_x
            dy = detection['y'] - player_y
            distance = (dx*dx + dy*dy) ** 0.5

            if distance < radius and distance > 0.05:  # Exclude very close (likely player)
                nearby_count += 1

        return nearby_count

    def get_detections_summary(self) -> Dict:
        """
        Get a summary of current detections

        Returns:
            Dict with detection statistics
        """
        if not self.detection_cache:
            return {
                'total_detected': 0,
                'avg_confidence': 0.0,
                'positions': []
            }

        return {
            'total_detected': len(self.detection_cache),
            'avg_confidence': sum(d['confidence'] for d in self.detection_cache) / len(self.detection_cache),
            'positions': [(d['x'], d['y']) for d in self.detection_cache]
        }

    def calibrate_minimap_region(self):
        """
        Helper to calibrate minimap region for different screen resolutions

        Captures full screen and helps identify minimap location
        """
        print("\n=== Minimap Region Calibration ===")
        print("This will help you find the correct minimap coordinates.")
        print()

        # Capture full screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            print(f"Screen resolution: {monitor['width']}x{monitor['height']}")
            print()
            print("Common minimap locations (adjust for your resolution):")
            print(f"  1920x1080: top=800, left=1650, width=250, height=250")
            print(f"  2560x1440: top=1100, left=2200, width=330, height=330")
            print(f"  1280x720:  top=530, left=1000, width=170, height=170")
            print()
            print("Current setting:", self.minimap_region)
            print()
            print("To update, modify minimap_region parameter when creating MinimapDetector")


def test_minimap_detection():
    """Test the minimap detector"""
    print("=== Minimap Detector Test ===\n")

    detector = MinimapDetector()

    print("Capturing minimap...")
    minimap = detector.capture_minimap()
    print(f"[OK] Captured minimap: {minimap.shape}")

    print("\nRunning champion detection...")
    detections = detector.detect_champions(minimap)
    print(f"[OK] Detected {len(detections)} objects")

    if detections:
        print("\nDetections:")
        for i, det in enumerate(detections, 1):
            print(f"  {i}. Position: ({det['x']:.2f}, {det['y']:.2f}), "
                  f"Confidence: {det['confidence']:.2f}")
    else:
        print("[INFO] No champions detected (this is normal without game running)")

    print("\nSummary:", detector.get_detections_summary())
    print("\n[OK] Test complete!")


if __name__ == "__main__":
    test_minimap_detection()
