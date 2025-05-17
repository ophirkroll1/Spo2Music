# main.py

import requests
import base64
import os
import json
import re
import difflib
from ytmusicapi import YTMusic
import yt_dlp

# --- Settings ---
PLAYLIST_ID = "5fgMIR1fLgyXRlrCtoK6kO"
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
MISSING_JSON = "missing_songs.json"
APPLE_JSON = "apple_matches.json"
REPLIT_BASE_URL = "https://raw.githubusercontent.com/ophirkroll1/Spo2Music/main/downloads/"
DOWNLOAD_DIR = "downloads"

# --- Spotify ---
def get_access_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_spotify_playlist_tracks():
    access_token = get_access_token()
    url = f"https://api.spotify.com/v1/playlists/{PLAYLIST_ID}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    results = []
    while url:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        for item in data["items"]:
            track = item["track"]
            results.append({
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "id": track["id"]
            })
        url = data.get("next")
    return results


import requests
import difflib

APPLE_MUSIC_API = "https://itunes.apple.com/search"

# 🔍 חיפוש שיר באפל מיוזיק לפי ISRC או לפי שם ואמן
def search_apple_music(title, artist, isrc=None):
    if isrc:
        response = requests.get(APPLE_MUSIC_API, params={"term": isrc, "entity": "song", "limit": 1})
        if response.ok:
            results = response.json().get("results", [])
            if results:
                return results[0]

    query = f"{title} {artist}"
    response = requests.get(APPLE_MUSIC_API, params={"term": query, "entity": "song", "limit": 5})
    if response.ok:
        results = response.json().get("results", [])
        if results:
            return results[0]

    return None

# 🎭 בדיקת התאמה בין שמות אמנים בצורה חכמה יותר
def artist_similarity(original, found):
    original = original.lower().strip()
    found = found.lower().strip()

    # אם האמן שחיפשנו נמצא כחלק מהתוצאה — קבל
    if original in found:
        return True

    # אחרת, בדיקת דמיון באחוזים
    similarity = difflib.SequenceMatcher(None, original, found).ratio()
    return similarity >= 0.65
# --- Download if not found ---
def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "", text)

def download_from_soundcloud(title, artist):
    search_query = f"scsearch1:{title} {artist}"
    filename = sanitize_filename(f"{artist} - {title}")
    output_path = os.path.join(DOWNLOAD_DIR, f"{filename}.%(ext)s")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([search_query])
        return filename + ".mp3"
    except:
        return None

def download_from_youtube(title, artist):
    query = f"ytsearch1:{title} {artist}"
    filename = sanitize_filename(f"{artist} - {title}")
    output_path = os.path.join(DOWNLOAD_DIR, f"{filename}.%(ext)s")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([query])
        return filename + ".mp3"
    except:
        return None

# --- Main Logic ---
tracks = get_spotify_playlist_tracks()
apple_matches = []
missing_songs = []

for track in tracks:
    title = track["title"]
    artist = track["artist"]
    print(f"🎧 {title} — {artist}")
    result = search_apple_music(title, artist)
    if result:
        found_artist = result["artistName"]
        if artist_similarity(artist, found_artist):
            apple_matches.append({
                "title": title,
                "artist": artist,
                "url": result["trackViewUrl"]
            })
            continue

    # Not found — try fallback
    print(f"❌ Not found on Apple Music: {title}")
    downloaded = download_from_soundcloud(title, artist)
    if not downloaded:
        downloaded = download_from_youtube(title, artist)
    if downloaded:
        missing_songs.append({
            "title": title,
            "artist": artist,
            "download_url": REPLIT_BASE_URL + downloaded.replace(" ", "%20")
        })

# --- Output ---
with open(APPLE_JSON, "w", encoding="utf-8") as f:
    json.dump(apple_matches, f, ensure_ascii=False, indent=2)

with open(MISSING_JSON, "w", encoding="utf-8") as f:
    json.dump(missing_songs, f, ensure_ascii=False, indent=2)

print("\n✅ Done. JSON files ready.")
