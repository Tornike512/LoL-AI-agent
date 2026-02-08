"""
Minimap Calibration Tool

Shows exactly where the minimap detector is capturing by drawing a red rectangle
on your screen. Adjust the coordinates in minimap_detector.py if needed.
"""

import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time

def show_minimap_region():
    """Display the minimap capture region with a red border"""

    # Default minimap region (same as in minimap_detector.py)
    minimap_region = {
        'top': 800,      # Minimap typically in bottom-right
        'left': 1650,
        'width': 250,
        'height': 250
    }

    print("=" * 60)
    print("   MINIMAP CALIBRATION TOOL")
    print("=" * 60)
    print()
    print("This will show you exactly where the detector is looking.")
    print()
    print(f"Current minimap region:")
    print(f"  Position: ({minimap_region['left']}, {minimap_region['top']})")
    print(f"  Size: {minimap_region['width']}x{minimap_region['height']}")
    print()
    print("Capturing screen with red rectangle overlay...")
    print("Press 'q' to close the preview window.")
    print()

    with mss.mss() as sct:
        # Capture full screen
        monitor = sct.monitors[1]

        while True:
            # Capture screen
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Draw red rectangle around minimap region
            top_left = (minimap_region['left'], minimap_region['top'])
            bottom_right = (
                minimap_region['left'] + minimap_region['width'],
                minimap_region['top'] + minimap_region['height']
            )

            # Draw thick red border
            cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 5)

            # Add text label
            label = "MINIMAP CAPTURE AREA"
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(label, font, 1, 2)[0]
            text_x = minimap_region['left'] + (minimap_region['width'] - text_size[0]) // 2
            text_y = minimap_region['top'] - 10

            # Draw text with background
            cv2.rectangle(img,
                         (text_x - 5, text_y - text_size[1] - 5),
                         (text_x + text_size[0] + 5, text_y + 5),
                         (0, 0, 255), -1)
            cv2.putText(img, label, (text_x, text_y), font, 1, (255, 255, 255), 2)

            # Resize to fit screen if needed
            scale = 0.7
            width = int(img.shape[1] * scale)
            height = int(img.shape[0] * scale)
            img_resized = cv2.resize(img, (width, height))

            # Show the image
            cv2.imshow('Minimap Calibration - Press Q to quit', img_resized)

            # Update every 500ms
            if cv2.waitKey(500) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()
    print("\n[OK] Calibration complete!")
    print()
    print("If the red rectangle is NOT on your minimap:")
    print("1. Open minimap_detector.py")
    print("2. Find the __init__ method (around line 32)")
    print("3. Adjust these values:")
    print("   - 'top': Y position (higher = up, lower = down)")
    print("   - 'left': X position (lower = left, higher = right)")
    print("   - 'width' and 'height': Size of capture area")
    print()
    print("Common resolutions:")
    print("  1920x1080: top=800,  left=1650, width=250, height=250")
    print("  2560x1440: top=1100, left=2200, width=330, height=330")
    print("  1280x720:  top=530,  left=1000, width=170, height=170")


if __name__ == "__main__":
    show_minimap_region()
