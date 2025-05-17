
import os
import json
import difflib
import requests
from spotify_client import get_spotify_playlist_tracks
from utils import sanitize_filename, add_to_missing_songs

# === Apple Music Search ===
def search_apple_music(title, artist):
    query = f"{title} {artist}"
    print(f"🔍 Searching Apple Music for: {query}")
    url = "https://itunes.apple.com/search"
    params = {"term": query, "entity": "song", "limit": 3}
    response = requests.get(url, params=params)

    if response.ok:
        results = response.json().get("results", [])
        if results:
            return results[0]  # Return first result
    return None

# === Artist Similarity Check ===
def artist_similarity(original, found):
    if not found:
        return False
    similarity = difflib.SequenceMatcher(None, original.lower(), found.lower()).ratio()
    return similarity >= 0.7

# === Main Logic ===
PLAYLIST_ID = os.environ.get("SPOTIFY_PLAYLIST_ID") or "5fgMIR1fLgyXRlrCtoK6kO"
print(f"🎧 Loading playlist: {PLAYLIST_ID}")

tracks = get_spotify_playlist_tracks(PLAYLIST_ID)
apple_matches = []
missing_songs = []

for idx, track in enumerate(tracks, 1):
    title = track.get("title")
    artist = track.get("artist")
    spotify_id = track.get("id")

    if not title or not artist:
        print(f"⚠️ Missing info: {track}")
        continue

    print(f"{idx}. 🎵 {title} — {artist}")

    apple_result = search_apple_music(title, artist)

    if apple_result:
        found_artist = apple_result.get("artistName")
        url = apple_result.get("trackViewUrl")

        if found_artist and url:
            if artist_similarity(artist, found_artist):
                print(f"  ✅ Found on Apple Music: {title} — {found_artist}")
                apple_matches.append({
                    "title": title,
                    "artist": artist,
                    "url": url
                })
                continue
            else:
                print(f"  ⚠️ Artist mismatch: {artist} vs {found_artist}")
        else:
            print(f"  ⚠️ Missing artistName or trackViewUrl in Apple Music result.")
    else:
        print(f"  ❌ Not found on Apple Music: {title}")

    # Add to missing list
    filename = sanitize_filename(f"{artist} - {title}.mp3")
    missing_songs.append({
        "title": title,
        "artist": artist,
        "spotify_url": f"https://open.spotify.com/track/{spotify_id}",
        "download_url": f"https://spotidownloader.com/en?url=https://open.spotify.com/track/{spotify_id}",
        "filename": filename
    })
    add_to_missing_songs(title, artist, filename)

# === Save Output ===
with open("apple_matches.json", "w", encoding="utf-8") as f:
    json.dump(apple_matches, f, ensure_ascii=False, indent=2)

with open("missing_songs.json", "w", encoding="utf-8") as f:
    json.dump(missing_songs, f, ensure_ascii=False, indent=2)

print("\n✅ Done. JSON files written.")
