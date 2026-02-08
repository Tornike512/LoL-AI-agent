"""
Jungler Tracker Overlay

Detects enemy jungler by identifying who has Smite summoner spell,
then displays a visual overlay showing if the jungler is visible on minimap.

Shows:
- "INVISIBLE" (red) when jungler not detected on minimap
- "VISIBLE" (green) when jungler appears on minimap
"""

import tkinter as tk
from typing import Optional, Dict, List
import requests
import urllib3

# Suppress SSL warnings (Live Client API uses self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JunglerTracker:
    """Tracks enemy jungler visibility and displays overlay"""

    def __init__(self, live_client_url: str = "https://127.0.0.1:2999/liveclientdata"):
        """
        Initialize the jungler tracker

        Args:
            live_client_url: Base URL for League Live Client API
        """
        self.live_client_url = live_client_url
        self.enemy_jungler = None
        self.is_visible = False

        # Create overlay window
        self.window = tk.Tk()
        self.window.title("Jungler Tracker")
        self.window.geometry("200x80+10+10")  # 200x80 size, position at (10, 10)
        self.window.configure(bg='black')
        self.window.attributes('-topmost', True)  # Always on top
        self.window.overrideredirect(True)  # Remove window border

        # Create label for status
        self.status_label = tk.Label(
            self.window,
            text="SEARCHING...",
            font=("Arial", 16, "bold"),
            fg="yellow",
            bg="black",
            pady=10
        )
        self.status_label.pack(expand=True, fill='both')

        # Create label for jungler name
        self.jungler_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 10),
            fg="white",
            bg="black"
        )
        self.jungler_label.pack()

    def detect_enemy_jungler(self) -> Optional[Dict]:
        """
        Detect enemy jungler by finding who has Smite

        Returns:
            Dict with jungler info or None if not found
        """
        try:
            response = requests.get(
                f"{self.live_client_url}/allplayers",
                verify=False,
                timeout=1
            )

            if response.status_code != 200:
                return None

            all_players = response.json()

            # Get active player's team
            active_response = requests.get(
                f"{self.live_client_url}/activeplayer",
                verify=False,
                timeout=1
            )

            if active_response.status_code != 200:
                return None

            active_player = active_response.json()
            player_team = active_player.get('team', 'ORDER')
            enemy_team = 'CHAOS' if player_team == 'ORDER' else 'ORDER'

            # Find enemy with Smite
            for player in all_players:
                if player.get('team') != enemy_team:
                    continue

                summoner_spells = player.get('summonerSpells', {})
                spell_one = summoner_spells.get('summonerSpellOne', {}).get('displayName', '')
                spell_two = summoner_spells.get('summonerSpellTwo', {}).get('displayName', '')

                # Check if player has Smite
                if 'Smite' in spell_one or 'Smite' in spell_two:
                    jungler_info = {
                        'summonerName': player.get('summonerName', 'Unknown'),
                        'championName': player.get('championName', 'Unknown'),
                        'team': player.get('team')
                    }
                    self.enemy_jungler = jungler_info
                    return jungler_info

            return None

        except Exception as e:
            # API not available or error
            return None

    def check_jungler_visibility(self, minimap_detections: List[Dict]) -> bool:
        """
        Check if enemy jungler is visible on minimap

        Args:
            minimap_detections: List of champion detections from MinimapDetector

        Returns:
            True if jungler appears to be visible, False otherwise
        """
        if not self.enemy_jungler:
            return False

        # For now, we assume any detection could be the jungler
        # TODO: Once we can identify specific champions from minimap,
        # we can check if detected champion matches self.enemy_jungler['championName']

        # Simple heuristic: if we detect ANY enemy champions, jungler might be visible
        # This will show false positives, but better than nothing
        return len(minimap_detections) > 0

    def update_overlay(self, is_visible: bool):
        """
        Update the overlay display

        Args:
            is_visible: True if jungler is visible on minimap
        """
        self.is_visible = is_visible

        if not self.enemy_jungler:
            self.status_label.config(text="SEARCHING...", fg="yellow")
            self.jungler_label.config(text="")
        elif is_visible:
            self.status_label.config(text="VISIBLE", fg="lime")
            self.jungler_label.config(
                text=f"{self.enemy_jungler['championName']}"
            )
        else:
            self.status_label.config(text="INVISIBLE", fg="red")
            self.jungler_label.config(
                text=f"{self.enemy_jungler['championName']}"
            )

    def update(self, minimap_detections: Optional[List[Dict]] = None):
        """
        Main update function - call this periodically

        Args:
            minimap_detections: Optional list of minimap detections
        """
        # Detect jungler if not yet found
        if not self.enemy_jungler:
            self.detect_enemy_jungler()

        # Check visibility
        if minimap_detections is not None and self.enemy_jungler:
            is_visible = self.check_jungler_visibility(minimap_detections)
            self.update_overlay(is_visible)
        else:
            self.update_overlay(False)

        # Update tkinter window
        self.window.update()

    def close(self):
        """Close the overlay window"""
        try:
            self.window.destroy()
        except:
            pass


def test_jungler_tracker():
    """Test the jungler tracker"""
    import time

    print("=== Jungler Tracker Test ===\n")
    print("Starting overlay... (Check top-left corner of screen)")

    tracker = JunglerTracker()

    print("\nDetecting enemy jungler...")
    jungler = tracker.detect_enemy_jungler()

    if jungler:
        print(f"[OK] Found enemy jungler: {jungler['championName']} ({jungler['summonerName']})")
    else:
        print("[INFO] No enemy jungler detected (game not running?)")

    print("\nRunning overlay for 10 seconds...")
    print("(The overlay will show INVISIBLE/VISIBLE status)")

    for i in range(10):
        # Simulate detection updates
        tracker.update(minimap_detections=[])  # Empty = invisible
        time.sleep(0.5)

        # Simulate jungler appearing
        if i % 4 == 0:
            tracker.update(minimap_detections=[{'champion': 'unknown'}])  # Detection = visible

        time.sleep(0.5)

    tracker.close()
    print("\n[OK] Test complete!")


if __name__ == "__main__":
    test_jungler_tracker()
