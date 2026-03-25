#!/usr/bin/env python3
"""Generate updated hercules.json with new pattern"""

import json

# Spanish number names
spanish_numbers = [
    "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
    "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
    "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve", "treinta",
    "treinta y uno", "treinta y dos", "treinta y tres", "treinta y cuatro", "treinta y cinco", "treinta y seis", "treinta y siete", "treinta y ocho", "treinta y nueve", "cuarenta",
    "cuarenta y uno", "cuarenta y dos", "cuarenta y tres", "cuarenta y cuatro", "cuarenta y cinco", "cuarenta y seis", "cuarenta y siete", "cuarenta y ocho", "cuarenta y nueve", "cincuenta",
    "cincuenta y uno", "cincuenta y dos", "cincuenta y tres", "cincuenta y cuatro", "cincuenta y cinco", "cincuenta y seis", "cincuenta y siete", "cincuenta y ocho", "cincuenta y nueve", "sesenta",
    "sesenta y uno", "sesenta y dos", "sesenta y tres", "sesenta y cuatro", "sesenta y cinco", "sesenta y seis", "sesenta y siete"
]

playlist = []

for i in range(1, 68):
    # Add MP3 chapter file
    chapter_num = str(i).zfill(2)
    chapter_name = spanish_numbers[i-1]
    mp3_filename = f"{chapter_num}_capitulo {chapter_name}.mp3"
    
    mp3_entry = {
        "service": "mpd",
        "uri": f"mnt/INTERNAL/hercules/numeros_capitulos/{mp3_filename}",
        "title": mp3_filename,
        "artist": "",
        "album": "",
        "albumart": "/albumart?cacheid=205&web=//extralarge&path=%2Fmnt%2FINTERNAL%2Fhercules%2Fnumeros_capitulos&icon=fa-tags&metadata=false"
    }
    playlist.append(mp3_entry)
    
    # Add WAV file
    wav_filename = f"hercules_{i}"
    wav_entry = {
        "service": "mpd",
        "uri": f"mnt/INTERNAL/hercules/{wav_filename}.wav",
        "title": wav_filename,
        "artist": "",
        "album": "",
        "albumart": "/albumart?cacheid=205&web=//extralarge&path=%2Fmnt%2FINTERNAL%2Fhercules&icon=fa-tags&metadata=false"
    }
    playlist.append(wav_entry)

# Write to file
with open('hercules_con_capitulos.json', 'w', encoding='utf-8') as f:
    json.dump(playlist, f, ensure_ascii=False, indent=0, separators=(',', ':'))

print(f"Generated {len(playlist)} entries in hercules_con_capitulos.json")
print(f"Total: {len(playlist)//2} chapters with {len(playlist)//2} wav files")
