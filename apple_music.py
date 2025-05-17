# apple_music.py
import requests
import difflib

APPLE_MUSIC_API = "https://itunes.apple.com/search"

def search_apple_music(title, artist, isrc=None):
    if isrc:
        response = requests.get(APPLE_MUSIC_API, params={"term": isrc, "entity": "song", "limit": 1})
        if response.ok:
            results = response.json().get("results", [])
            if results:
                return {
                    "name": results[0].get("trackName"),
                    "artist": results[0].get("artistName"),
                    "url": results[0].get("trackViewUrl")
                }

    query = f"{title} {artist}"
    response = requests.get(APPLE_MUSIC_API, params={"term": query, "entity": "song", "limit": 5})
    if response.ok:
        results = response.json().get("results", [])
        if results:
            best = results[0]
            return {
                "name": best.get("trackName"),
                "artist": best.get("artistName"),
                "url": best.get("trackViewUrl")
            }
    return None

def artist_similarity(original, found):
    original = original.lower().strip()
    found = found.lower().strip()
    similarity = difflib.SequenceMatcher(None, original, found).ratio()
    return similarity >= 0.7
