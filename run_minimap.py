"""
Standalone Minimap Champion Detector with Jungler Tracker

Continuously monitors your minimap and shows detected champions in real-time.
Also displays a jungler tracker overlay in top-left corner.
Press Ctrl+C to stop.
"""

import time
from datetime import datetime
from minimap_detector import MinimapDetector
from jungler_tracker import JunglerTracker

def main():
    print("=" * 60)
    print("   MINIMAP CHAMPION DETECTOR + JUNGLER TRACKER")
    print("=" * 60)
    print()

    # Initialize detector
    print("Initializing minimap detector...")
    detector = MinimapDetector()
    print("[OK] Detector ready!")

    # Initialize jungler tracker
    print("Initializing jungler tracker overlay...")
    tracker = JunglerTracker()
    print("[OK] Jungler tracker ready! (check top-left corner)\n")

    print("Monitoring minimap... (Press Ctrl+C to stop)\n")

    try:
        while True:
            # Detect champions
            detections = detector.detect_champions()

            # Update jungler tracker overlay
            tracker.update(detections)

            # Display results
            timestamp = datetime.now().strftime("%H:%M:%S")

            if detections:
                print(f"[{timestamp}] 👁️ Detected {len(detections)} champion(s):")
                for i, det in enumerate(detections, 1):
                    print(f"  {i}. Position: ({det['x']:.2f}, {det['y']:.2f}) | Confidence: {det['confidence']:.2f}")
            else:
                print(f"[{timestamp}] No champions detected on minimap")

            # Wait before next detection
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[!] Detector stopped by user")
        tracker.close()
        print("Goodbye!")

if __name__ == "__main__":
    main()
