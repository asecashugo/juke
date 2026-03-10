from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
import subprocess
import time
import controls

# Initialize PN532
pn532 = Pn532_i2c()
pn532.SAMconfigure()

# Map NFC UID (hex string) to Spotify URI
card_map = {
    "4B010100040804D1A82107": "spotify:track:6JIC3hbC28JZKZ8AlAqX8h",
    "04123456": "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp",
    # Add more cards here
}

last_uid = None

print("Waiting for NFC tags...")

while True:
    frame = pn532.read_mifare()
    if frame:
        uid_bytes = frame.get_data()  # Correct extraction
        uid_str = "".join("{:02X}".format(x) for x in uid_bytes)

        if uid_str != last_uid:
            print("Tag detected:", uid_str)
            if uid_str in card_map:
                spotify_uri = card_map[uid_str]
                subprocess.run([
                    "curl", "-X", "POST",
                    "http://localhost:3000/api/v1/replaceAndPlay",
                    "-H", "Content-Type: application/json",
                    "-d", f'{{"uri":"{spotify_uri}"}}'
                ])
            last_uid = uid_str
    else:
        last_uid = None

    time.sleep(1)