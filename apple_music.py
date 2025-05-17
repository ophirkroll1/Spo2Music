# apple_music.py
import requests
import difflib

APPLE_MUSIC_API = "https://itunes.apple.com/search"

# 🔍 Search for a song in Apple Music by ISRC or by title and artist

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

# 🎭 Compare artist names or check if the given artist is included

def artist_similarity(original, found):
    original = original.lower().strip()
    found = found.lower().strip()

    similarity = difflib.SequenceMatcher(None, original, found).ratio()
    return original in found or similarity >= 0.7
