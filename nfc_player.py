from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import time
import json
import controls

# Initialize PN532
pn532 = Pn532_i2c()
pn532.SAMconfigure()

def load_card_map():
    """Load card mappings from JSON file"""
    try:
        with open('/home/volumio/nfc/cards.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_card_map(card_map):
    """Save card mappings to JSON file"""
    with open('/home/volumio/nfc/cards.json', 'w') as f:
        json.dump(card_map, f, indent=2)

# Load the card map
card_map = load_card_map()

last_uid = None
last_action_time = None
COOLDOWN_TIME = 2  # seconds between play/toggle actions

# Wait for Volumio to be ready
print("Starting up - waiting for Volumio to be ready...")
controls.wait_for_ready()

print("Waiting for NFC tags...")

while True:
    frame = pn532.read_mifare()
    if frame:
        uid_bytes = frame.get_data()  # Correct extraction
        uid_str = "".join("{:02X}".format(x) for x in uid_bytes)
        print(f"Card detected: {uid_str}")
        if uid_str != last_uid:
            # New card detected
            if uid_str in card_map:
                card_info = card_map[uid_str]
                spotify_uri = card_info["uri"]
                alias = card_info.get("alias", "Unknown")
                print(f"\n ^v  Playing: {alias}\n")
                controls.play(uri=spotify_uri)
                last_action_time = time.time()
            else:
                # Unknown card - ask user to add it
                print(f"Unknown card: {uid_str}")
                uri = input("Enter Spotify URI (or press Enter to skip): ").strip()
                if uri:
                    alias = input("Enter alias for this card (optional, press Enter to skip): ").strip()
                    if not alias:
                        alias = "Unknown Track"
                    # Add to card map and save
                    card_map[uid_str] = {"uri": uri, "alias": alias}
                    save_card_map(card_map)
                    print(f"Card saved as: {alias}")
                    # Play the song
                    controls.play(uri=uri)
                    last_action_time = time.time()
            last_uid = uid_str
        else:
            # Same card detected - check if cooldown has passed
            if last_action_time and (time.time() - last_action_time) >= COOLDOWN_TIME:
                print("Toggling playback")
                controls.toggle()
                last_action_time = time.time()
    else:
        last_uid = None

    time.sleep(1)