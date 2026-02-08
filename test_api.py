"""
Quick test script to check if Live Client API is accessible
Run this while in a League of Legends game to verify connectivity
"""

import requests
import urllib3
import json

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "https://127.0.0.1:2999/liveclientdata/allgamedata"

print("=" * 60)
print("   Testing League of Legends Live Client API")
print("=" * 60)
print()
print(f"Attempting to connect to: {API_URL}")
print()

try:
    response = requests.get(API_URL, verify=False, timeout=5)

    if response.status_code == 200:
        data = response.json()

        print("✓ SUCCESS! Connected to Live Client API")
        print()
        print("Game Information:")
        print("-" * 60)

        # Game mode
        game_data = data.get("gameData", {})
        print(f"  Game Mode: {game_data.get('gameMode', 'Unknown')}")
        print(f"  Game Time: {game_data.get('gameTime', 0):.1f}s")

        # Active player
        active_player = data.get("activePlayer", {})
        champ_stats = active_player.get("championStats", {})
        print(f"  Your Champion: {champ_stats.get('championName', 'Unknown')}")
        print(f"  Level: {active_player.get('level', 0)}")
        print(f"  Gold: {active_player.get('currentGold', 0)}g")

        # Abilities
        abilities = active_player.get("abilities", {})
        print()
        print("Ability Cooldowns:")
        for spell in ['Q', 'W', 'E', 'R']:
            ability = abilities.get(spell, {})
            cd = ability.get('cooldown', 0)
            level = ability.get('abilityLevel', 0)
            status = "Ready" if cd == 0 and level > 0 else f"{cd:.1f}s" if level > 0 else "Not learned"
            print(f"  {spell}: {status}")

        # Position
        position = active_player.get("position", {})
        print()
        print(f"Position: ({position.get('x', 0):.1f}, {position.get('z', 0):.1f})")

        print()
        print("=" * 60)
        print("✓ API is working! You can now run katarina_coach.py")
        print("=" * 60)

    else:
        print(f"✗ API returned status code: {response.status_code}")
        print("  Make sure you're in an active game")

except requests.exceptions.ConnectionError:
    print("✗ CONNECTION FAILED")
    print()
    print("Possible reasons:")
    print("  1. You're not in an active League of Legends game")
    print("  2. You're in champion select or lobby (API only works during gameplay)")
    print("  3. League client is not running")
    print()
    print("To test:")
    print("  1. Start a Practice Tool game")
    print("  2. Run this script again")

except Exception as e:
    print(f"✗ ERROR: {e}")

print()
