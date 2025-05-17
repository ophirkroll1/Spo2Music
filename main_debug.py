# main_debug.py
from spotify_client import get_spotify_playlist_tracks
from apple_music import search_apple_music, artist_similarity
from utils import sanitize_filename
import json

PLAYLIST_ID = "5fgMIR1fLgyXRlrCtoK6kO"

print(f"🎵 Loading playlist: {PLAYLIST_ID}")
tracks = get_spotify_playlist_tracks(PLAYLIST_ID)

apple_matches = []
missing_songs = []

for idx, track in enumerate(tracks, 1):
    title = track.get("title")
    artist = track.get("artist")

    if not title or not artist:
        print(f"⚠️ Skipping track with missing info: {track}")
        continue

    print(f"{idx}. 🎵 {title} — {artist}")
    print(f"🔍 Searching Apple Music for: {title} {artist}")

    result = search_apple_music(title, artist)
    if result:
        found_artist = result.get("artist", "")
        url = result.get("url", "")

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
        print(f"  ❌ Not found on Apple Music: {title}")

    # Add to missing songs
    filename = sanitize_filename(f"{artist} - {title}.mp3")
    missing_songs.append({
        "title": title,
        "artist": artist,
        "spotify_url": f"https://open.spotify.com/track/{track['id']}",
        "download_url": f"https://spotidownloader.com/en?url=https://open.spotify.com/track/{track['id']}",
        "filename": filename
    })

# Save results
with open("apple_matches.json", "w", encoding="utf-8") as f:
    json.dump(apple_matches, f, ensure_ascii=False, indent=2)

with open("missing_songs.json", "w", encoding="utf-8") as f:
    json.dump(missing_songs, f, ensure_ascii=False, indent=2)

print("\n✅ Done. JSON files written.")
