from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import time
import json
import os
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

def load_aventura_map():
    """Load adventure special cards from JSON file"""
    try:
        with open('/home/volumio/nfc/aventura.json', 'r') as f:
            data = json.load(f)
            # Return inverted mapping: UID -> letter (A/B/C)
            special_cards = data.get("special_cards", {})
            return {uid: letter for uid, letter in special_cards.items()}
    except FileNotFoundError:
        return {}

# Load the card maps
card_map = load_card_map()
aventura_special_cards = load_aventura_map()

last_uid = None
last_action_time = None
COOLDOWN_TIME = 2  # seconds between play/toggle actions
PLAYBACK_CHECK_INITIAL_DELAY = 0.5  # seconds to wait before checking playback state
PLAYBACK_CHECKS = 10
PLAYBACK_CHECK_DELAY = 0.3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def alias_to_filename(alias):
    """Convert an alias to the matching local MP3 filename."""
    name = alias.lower().replace(' ', '_')
    name = ''.join(ch for ch in name if ch.isalnum() or ch == '_')
    return name + '.mp3'


def local_media_uri(alias):
    return f"music-library/INTERNAL/mp3/{alias_to_filename(alias)}"


def local_media_exists(alias):
    filename = alias_to_filename(alias)
    return any(os.path.isfile(os.path.join(directory, filename))
               for directory in ('/data/INTERNAL/mp3', '/mnt/mp3'))


def spotify_played(uri):
    """Play a URI and confirm Volumio reports that playback started."""
    controls.play(uri=uri)
    time.sleep(PLAYBACK_CHECK_INITIAL_DELAY)
    for _ in range(PLAYBACK_CHECKS):
        time.sleep(PLAYBACK_CHECK_DELAY)
        try:
            state = json.loads(controls.get_state())
        except (json.JSONDecodeError, TypeError):
            continue
        if state.get("status") == "play":
            print(f"Spotify playback started: {uri}")
            return True
        if state.get("status") == "stop":
            print(f"Volumio stopped URI: {uri}")
            return False
    print(f"Could not confirm playback for: {uri}")
    return False


def is_radio_card(card_info, uri):
    media_type = str(card_info.get("type", "")).lower()
    uri_lower = uri.lower()
    return media_type in ("radio", "webradio", "stream") or \
        "radiotime" in uri_lower or "opml.radiotime.com" in uri_lower


def is_playlist_card(card_info, uri):
    media_type = str(card_info.get("type", "")).lower()
    return media_type == "playlist" or uri.lower().startswith("playlist_")


def play_card(card_info, alias):
    """Play playlists/radio directly, otherwise try Spotify and local MP3 fallbacks."""
    source_uri = card_info.get("source_uri") or card_info.get("uri", "")
    if is_playlist_card(card_info, source_uri):
        print(f"Playing local playlist: {source_uri}")
        controls.play_playlist(list_name=source_uri)
        return

    if is_radio_card(card_info, source_uri):
        print(f"Playing radio stream: {source_uri}")
        controls.play(uri=source_uri)
        return

    spotify_uri = source_uri
    if spotify_uri.startswith("spotify:") and spotify_played(spotify_uri):
        return

    mp3_uri = local_media_uri(alias)
    if local_media_exists(alias):
        print(f"Playing local fallback: {mp3_uri}")
        controls.play(uri=mp3_uri)
        return

    print(f"{alias_to_filename(alias)} not found; playing mp3_not_found.mp3")
    controls.play(uri="music-library/INTERNAL/mp3/mp3_not_found.mp3")

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
        
        # Check if this is a STOP card (highest priority)
        if uid_str in aventura_special_cards and aventura_special_cards[uid_str] == "STOP":
            print("\n STOP card detected - stopping playback")
            controls.stop()
            last_uid = None
            last_action_time = None
            continue
        
        # Check if this is an adventure card (A, B, or C)
        if uid_str in aventura_special_cards:
            adventure_letter = aventura_special_cards[uid_str]
            print(f"\n Adventure card detected: {adventure_letter}")
            controls.aventura(adventure_letter, pn532, aventura_special_cards)
            last_uid = None
            last_action_time = None
            continue
        
        if uid_str != last_uid:
            # New card detected
            if uid_str in card_map:
                card_info = card_map[uid_str]
                alias = card_info.get("alias", "Unknown")
                print(f"\n ^v  Playing: {alias}\n")
                play_card(card_info, alias)
                last_action_time = time.time()
            else:
                # Unknown card - ask user to add it
                print(f"Unknown card: {uid_str}")
                uri = input("Enter Spotify URI or radio stream URL (or press Enter to skip): ").strip()
                if uri:
                    alias = input("Enter alias for this card (optional, press Enter to skip): ").strip()
                    if not alias:
                        alias = "Unknown Track"
                    mp3_filename = alias_to_filename(alias)
                    card_info = {
                        "uri": uri,
                        "alias": alias,
                        "mp3_file": f"mp3/{mp3_filename}",
                        "source_uri": uri,
                    }
                    if is_radio_card(card_info, uri):
                        card_info["type"] = "radio"
                    elif is_playlist_card(card_info, uri):
                        card_info["type"] = "playlist"
                    card_map[uid_str] = card_info
                    save_card_map(card_map)
                    print(f"Card saved as: {alias} -> {mp3_filename}")
                    play_card(card_map[uid_str], alias)
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