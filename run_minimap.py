"""
Standalone Minimap Detector with Visual Status Indicator

Continuously monitors your screen for the League of Legends minimap.
Shows a small indicator in top-left corner:
- RED = Minimap not detected
- GREEN = Minimap detected and monitoring
Press Ctrl+C to stop.
"""

import time
import tkinter as tk
import numpy as np
from datetime import datetime
from minimap_detector import MinimapDetector
from jungler_tracker import JunglerTracker


class MinimapStatusIndicator:
    """Small overlay showing minimap detection status"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Minimap Status")
        self.window.geometry("150x50+10+10")
        self.window.configure(bg='red')
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)

        self.label = tk.Label(
            self.window,
            text="NO MINIMAP",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="red",
            pady=10
        )
        self.label.pack(expand=True, fill='both')

    def set_detected(self, detected: bool):
        """Update status based on minimap detection"""
        if detected:
            self.window.configure(bg='green')
            self.label.config(text="MINIMAP OK", bg='green')
        else:
            self.window.configure(bg='red')
            self.label.config(text="NO MINIMAP", bg='red')
        self.window.update()

    def close(self):
        """Close the indicator window"""
        try:
            self.window.destroy()
        except:
            pass


def is_minimap_visible(minimap_img: np.ndarray) -> bool:
    """
    Check if the captured image looks like a League of Legends minimap.

    Args:
        minimap_img: Captured image from screen region

    Returns:
        True if minimap is detected, False otherwise
    """
    if minimap_img is None or minimap_img.size == 0:
        return False

    # Check image size (minimap should be roughly square)
    height, width = minimap_img.shape[:2]
    if width < 100 or height < 100:
        return False

    # Check for characteristic minimap colors
    if len(minimap_img.shape) == 3:
        # Sample center and corners
        center = minimap_img[height//2, width//2]
        top_left = minimap_img[height//4, width//4]
        bottom_right = minimap_img[3*height//4, 3*width//4]

        # Minimap typically has dark/grayish background
        for pixel in [center, top_left, bottom_right]:
            r, g, b = pixel
            avg_brightness = (r + g + b) / 3
            if avg_brightness < 20 or avg_brightness > 240:
                return False

        # Check for color variation (minimap has terrain, not solid color)
        std_dev = np.std(minimap_img)
        if std_dev < 10:
            return False

        return True

    return False


def main():
    print("=" * 60)
    print("   MINIMAP DETECTOR WITH STATUS INDICATOR")
    print("=" * 60)
    print()

    # Initialize status indicator
    print("Initializing status indicator...")
    status = MinimapStatusIndicator()
    print("[OK] Status indicator ready! (check top-left corner)")

    # Initialize detector
    print("Initializing minimap detector...")
    detector = MinimapDetector()
    print("[OK] Detector ready!")

    # Initialize jungler tracker
    print("Initializing jungler tracker overlay...")
    tracker = JunglerTracker()
    print("[OK] Jungler tracker ready!")

    print("Monitoring screen for minimap... (Press Ctrl+C to stop)")
    print()

    try:
        while True:
            # Capture minimap region
            minimap_img = detector.capture_minimap()

            # Check if minimap is visible
            minimap_detected = is_minimap_visible(minimap_img)

            # Update status indicator
            status.set_detected(minimap_detected)

            # Only detect champions if minimap is visible
            if minimap_detected:
                detections = detector.detect_champions(minimap_img)
                tracker.update(detections)

                # Display results
                timestamp = datetime.now().strftime("%H:%M:%S")

                if detections:
                    print(f"[{timestamp}] Detected {len(detections)} champion(s):")
                    for i, det in enumerate(detections, 1):
                        print(f"  {i}. Position: ({det['x']:.2f}, {det['y']:.2f}) | Confidence: {det['confidence']:.2f}")
                else:
                    print(f"[{timestamp}] No champions detected on minimap")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Minimap not detected")
                tracker.update([])  # Update tracker with no detections

            # Wait before next check
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[!] Detector stopped by user")
        status.close()
        tracker.close()
        print("Goodbye!")


if __name__ == "__main__":
    main()
