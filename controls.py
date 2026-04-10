import subprocess
import time
import json

HOST="Juke"
URI="spotify:track:6JIC3hbC28JZKZ8AlAqX8h"
VALE_URI="music-library/INTERNAL/listo.mp3"

def get_state(host:str=HOST):
    result = subprocess.run(["curl", f"http://{host}:3000/api/v1/getState"], capture_output=True, text=True)
    return result.stdout
def play(host:str=HOST,uri:str=URI):
    # if uri contains "playlist_", use playplaylist endpoint instead
    if "playlist_" in uri:
        return play_playlist(uri, host)
    else:
        result = subprocess.run(["curl", "-X", "POST", f"http://{host}:3000/api/v1/replaceAndPlay", "-H", "Content-Type: application/json", "-d", f'{{"uri":"{uri}"}}'], capture_output=True, text=True)
        return result.stdout

def play_playlist(list_name:str,host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=playplaylist&name={list_name}"], capture_output=True, text=True)
    return result.stdout
def pause(host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=pause"], capture_output=True, text=True)
    return result.stdout
def toggle(host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=toggle"], capture_output=True, text=True)
    return result.stdout
def stop(host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=stop"], capture_output=True, text=True)
    return result.stdout
def next(host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=next"], capture_output=True, text=True)
    return result.stdout
def previous(host:str=HOST):
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=previous"], capture_output=True, text=True)
    return result.stdout
def volume(host:str=HOST, volume_perc:int=50):
    volume_perc = max(0, min(100, volume_perc))
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/commands/?cmd=volume&volume={volume_perc}"], capture_output=True, text=True)
    return result.stdout
def get_queue(host:str=HOST):
    """Get the current playback queue"""
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/getQueue"], capture_output=True, text=True)
    return result.stdout
def add_to_queue(host:str=HOST, uri:str=""):
    """Add a track to the queue"""
    result = subprocess.run(["curl", "-X", "POST", f"http://{host}:3000/api/v1/addToQueue", "-H", "Content-Type: application/json", "-d", f'{{"uri":"{uri}"}}'], capture_output=True, text=True)
    return result.stdout
def wait_for_ready(host:str=HOST, max_retries:int=30, retry_delay:int=1, startup_sound:str=""):
    """
    Wait for Volumio to be ready by polling the API.
    Optionally plays a sound directly (bypassing Volumio API) while waiting.
    
    Args:
        host: Volumio host
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        startup_sound: Path to sound file to play when ready (optional)
    
    Returns:
        True if ready, False if timeout
    """
    for attempt in range(max_retries):
        try:
            result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/getState", "-m", "2"], capture_output=True, text=True, timeout=3)
            if result.returncode == 0 and result.stdout:
                # Try to parse as JSON to ensure valid response
                json.loads(result.stdout)
                print(f"Volumio ready after {attempt} attempts")
                # Play startup sound to indicate device is ready
                print("Device ready - playing startup sound...")
                play(uri=VALE_URI)
                time.sleep(2)  # Wait for sound to finish
                return True
        except (json.JSONDecodeError, subprocess.TimeoutExpired):
            pass
        
        if attempt < max_retries - 1:
            print(f"Waiting for Volumio... ({attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
    
    return False
def browse(host:str=HOST, uri:str="music-library/INTERNAL"):
    """Browse a URI (e.g. local library)"""
    result = subprocess.run(["curl", "-X", "GET", f"http://{host}:3000/api/v1/browse?uri={uri}"], capture_output=True, text=True)
    return result.stdout
def load_aventura_map():
    """Load adventure paths from JSON file"""
    try:
        with open('/home/volumio/nfc/aventura.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: aventura.json not found")
        return None
def aventura(starting_card: str, pn532_reader, card_map: dict):
    """
    Play choose-your-own-adventure game.
    
    Args:
        starting_card: Starting card identifier ('A', 'B', or 'C')
        pn532_reader: PN532 NFC reader object
        card_map: Dictionary mapping special card UIDs to A/B/C
    
    Returns:
        True if adventure completed, False if interrupted
    """
    aventura_data = load_aventura_map()
    if not aventura_data:
        return False
    
    paths = aventura_data.get("paths", {})
    current_path = starting_card
    
    print(f"\n{'='*50}")
    print(f"Adventure started with card {starting_card}")
    print(f"{'='*50}\n")
    
    while True:
        # Check if current path exists
        if current_path not in paths:
            print(f"ERROR: Path '{current_path}' not found in aventura.json")
            return False
        
        path_data = paths[current_path]
        audio_uri = path_data.get("audio", "")
        is_end = path_data.get("end", False)
        
        # Play the audio for this path
        print(f"Playing: {audio_uri}")
        play(uri=audio_uri)
        
        # If this is the end, exit adventure
        if is_end:
            print(f"\nAdventure ended at path: {current_path}")
            print(f"{'='*50}\n")
            return True
        
        # Wait for user to choose next option
        print(f"\nWaiting for choice (A/B/C)... (5 seconds)")
        start_time = time.time()
        choice = None
        
        while time.time() - start_time < 5:
            frame = pn532_reader.read_mifare()
            if frame:
                uid_bytes = frame.get_data()
                uid_str = "".join("{:02X}".format(x) for x in uid_bytes)
                
                # Check if this is a special card (A/B/C or STOP)
                card_choice = card_map.get(uid_str)
                
                # Check if STOP card was presented
                if card_choice == "STOP":
                    print(f"\nStop card detected - exiting adventure")
                    return False
                
                if card_choice in ['A', 'B', 'C']:
                    print(f"Choice selected: {card_choice}")
                    current_path += card_choice
                    choice = card_choice
                    break
            time.sleep(0.1)
        
        if choice is None:
            print(f"No choice detected - adventure timed out")
            return False