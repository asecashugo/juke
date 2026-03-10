# JUKE

No screen? No buttons? No problem! JUKE is a jukebox for kids powered by a Raspberry Pi and Volumio.

Just scan NFC tags to play music, pause, skip tracks, and adjust the volume.

## Requires
- Raspberry Pi 4
- NFC reader PN532
- Volumio installed on the Raspberry Pi
- Spotify plugin for Volumio
- Spotify account
- DAC
- Speakers
- Power supply
- NFC tags
- NFC tag writing software (e.g. NFC Tools)
- Phone or computer to write NFC tags

## Spotify URIs

Hold Ctrl while in the share menu in Spotify to copy the URI of a track, album, or playlist

## Volumio API sample calls

### Play a track by Spotify URI
curl -X POST http://localhost:3000/api/v1/replaceAndPlay \
     -H "Content-Type: application/json" \
     -d '{"uri":"spotify:track:6JIC3hbC28JZKZ8AlAqX8h"}'
### Get state
curl http://localhost:3000/api/v1/getState
### Pause playback
curl -X GET http://localhost:3000/api/v1/commands/?cmd=pause
### Resume playback
curl -X GET http://localhost:3000/api/v1/commands/?cmd=play
### Volume down
curl -X GET http://localhost:3000/api/v1/commands/?cmd=volume_down

## SSH

ssh volumio@juke