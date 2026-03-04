import subprocess
HOST="Juke"
URI="spotify:track:6JIC3hbC28JZKZ8AlAqX8h"

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