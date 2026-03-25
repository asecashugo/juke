#!/usr/bin/env python3
"""Update RIFF INFO chunk in WAV files."""

import struct
from pathlib import Path

def write_riff_info_item(tag_name, value):
    """Create a RIFF INFO subchunk item."""
    value_bytes = value.encode('utf-8') + b'\x00'  # Null-terminated
    size = len(value_bytes)
    data = tag_name.encode('ascii') + struct.pack('<I', size) + value_bytes
    # Pad to word boundary if needed
    if size % 2:
        data += b'\x00'
    return data

def create_info_chunk(filename):
    """Create INFO chunk with proper metadata."""
    info_items = b''
    info_items += write_riff_info_item('INAM', filename)  # Title
    info_items += write_riff_info_item('IART', '')        # Artist - blank
    info_items += write_riff_info_item('IGNR', '')        # Genre - blank
    
    # Create LIST chunk
    list_type = b'INFO'
    list_data = list_type + info_items
    list_size = len(list_data)
    list_chunk = b'LIST' + struct.pack('<I', list_size) + list_data
    
    return list_chunk

# Directory with WAV files
wav_directory = Path("Hércules de Tirinto")
wav_files = sorted(wav_directory.glob("*.wav"))
print(f"Found {len(wav_files)} WAV files\n")

for wav_file in wav_files:
    try:
        # Read entire file
        with open(wav_file, 'rb') as f:
            data = bytearray(f.read())
        
        # Find and remove old LIST/INFO chunk
        list_pos = data.find(b'LIST')
        if list_pos != -1:
            # Get size of old LIST chunk
            old_size = struct.unpack('<I', data[list_pos+4:list_pos+8])[0]
            old_chunk_size = 8 + old_size
            # Pad to word boundary
            if old_size % 2:
                old_chunk_size += 1
            
            # Remove old LIST chunk
            data = data[:list_pos] + data[list_pos+old_chunk_size:]
        
        # Create new INFO chunk
        new_info = create_info_chunk(wav_file.stem)
        
        # Insert new LIST chunk before the 'id3 ' chunk or at the end
        id3_pos = data.find(b'id3 ')
        if id3_pos != -1:
            insert_pos = id3_pos
        else:
            insert_pos = len(data)
        
        data = data[:insert_pos] + new_info + data[insert_pos:]
        
        # Update RIFF size
        riff_size = len(data) - 8
        data[4:8] = struct.pack('<I', riff_size)
        
        # Write file
        with open(wav_file, 'wb') as f:
            f.write(data)
        
        print(f"[OK] Updated: {wav_file.name} (title: {wav_file.stem})")
        
    except Exception as e:
        print(f"[ERROR] {wav_file.name}: {e}")

print("\nDone!")
