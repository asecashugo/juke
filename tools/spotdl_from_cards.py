#!/usr/bin/env python3
"""Download tracks listed in a remote cards.json using spotdl and upload them to Volumio.

Usage: run from workspace root. It will:
 - scp volumio@juke.local:/home/volumio/nfc/cards.json ./nfc/cards.json
 - parse entries and for each non-local URI run `spotdl <uri>` into a temp folder
 - rename downloads to alias-based filenames (lowercase, spaces->_, keep alnum/_)
 - scp resulting mp3s to volumio@juke.local:/data/INTERNAL/mp3/
 - set ownership on remote and restart mpd

Requires: `spotdl` available on PATH, `scp` and `ssh` available.
Be sure you have the right to download the tracks.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import argparse

JUKE = os.environ.get('JUKE_HOST', 'juke.local')
JUKE_USER = os.environ.get('JUKE_USER', 'volumio')
REMOTE_CARDS = '/home/volumio/nfc/cards.json'
LOCAL_CARDS = Path('nfc') / 'cards.json'
DOWNLOAD_DIR = Path('downloads')
FINAL_DIR = DOWNLOAD_DIR / 'final'


def alias_to_filename(alias: str) -> str:
    name = alias.lower()
    name = name.replace(' ', '_')
    name = ''.join(ch for ch in name if ch.isalnum() or ch == '_')
    return name + '.mp3'


def run(cmd, check=True, **kwargs):
    print('>', ' '.join(cmd))
    return subprocess.run(cmd, check=check, **kwargs)


def fetch_cards():
    if LOCAL_CARDS.exists():
        print(f"Using existing {LOCAL_CARDS}")
        return
    print('Fetching remote cards.json...')
    run(['scp', f'{JUKE_USER}@{JUKE}:{REMOTE_CARDS}', str(LOCAL_CARDS)])


def load_cards():
    with open(LOCAL_CARDS, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_dirs():
    # Allow overriding the final output directory via env var
    global FINAL_DIR
    dest = os.environ.get('SPOTDL_FINAL_DIR')
    if dest:
        FINAL_DIR = Path(dest)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)


def download_track(uri, alias):
    # skip local URIs or playlists
    if not uri or uri.startswith('music-library/') or uri.startswith('mp3/') or uri.startswith('/'):
        print('Skipping local URI:', uri)
        return None

    # skip playlists (user requested)
    low = uri.lower()
    if 'playlist' in low or uri.startswith('playlist_'):
        print('Skipping playlist URI:', uri)
        return None

    # Convert spotify:... URIs to open.spotify.com URLs
    if uri.startswith('spotify:'):
        parts = uri.split(':')
        if len(parts) >= 3:
            if parts[1] == 'track':
                uri = f'https://open.spotify.com/track/{parts[2]}'
            elif parts[1] == 'album':
                uri = f'https://open.spotify.com/album/{parts[2]}'
            elif parts[1] == 'playlist':
                uri = f'https://open.spotify.com/playlist/{parts[2]}'

    tmpdir = tempfile.mkdtemp(dir=str(DOWNLOAD_DIR))
    try:
        # call spotdl to download into tmpdir
        try:
            run(['spotdl', uri, '--output', tmpdir])
        except FileNotFoundError:
            # fallback to running as a module with the current python
            try:
                run([sys.executable, '-m', 'spotdl', uri, '--output', tmpdir])
            except subprocess.CalledProcessError as e:
                print('spotdl failed for', uri, 'error:', e)
                return None
        except subprocess.CalledProcessError as e:
            print('spotdl failed for', uri, 'error:', e)
            return None
        # find mp3 file(s)
        mp3s = list(Path(tmpdir).rglob('*.mp3'))
        if not mp3s:
            print('No mp3 found for', uri)
            return None
        # pick first mp3
        src = mp3s[0]
        dest_name = alias_to_filename(alias)
        dest = FINAL_DIR / dest_name
        print(f'Renaming {src} -> {dest}')
        shutil.move(str(src), str(dest))
        return dest
    finally:
        # cleanup tmpdir except moved file
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass


def upload_to_juke(files):
    if not files:
        print('No files to upload')
        return
    remote_dir = '/data/INTERNAL/mp3/'
    for f in files:
        print('Uploading', f)
        run(['scp', str(f), f'{JUKE_USER}@{JUKE}:{remote_dir}'])
    # set ownership and restart mpd
    ssh_cmd = f"sudo chown -R volumio:volumio {remote_dir} && sudo systemctl restart mpd"
    run(['ssh', f'{JUKE_USER}@{JUKE}', ssh_cmd])


def main():
    fetch_cards()
    card_map = load_cards()
    prepare_dirs()

    uploaded = []
    for uid, info in card_map.items():
        uri = info.get('uri') or info.get('mp3_file')
        alias = info.get('alias') or f'card_{uid}'
        print('Processing', uid, alias, uri)
        result = download_track(uri, alias)
        if result:
            uploaded.append(result)

    upload_to_juke(uploaded)


if __name__ == '__main__':
    main()
