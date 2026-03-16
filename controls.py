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
    result = subprocess.run(["curl", "-X", "POST", f"http://{host}:3000/api/v1/replaceAndPlay", "-H", "Content-Type: application/json", "-d", f'{{"uri":"{uri}"}}'], capture_output=True, text=True)
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