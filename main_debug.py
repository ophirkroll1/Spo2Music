import json
from spotify_client import get_spotify_playlist_tracks
from apple_music import search_apple_music, artist_similarity
from utils import sanitize_filename

PLAYLIST_ID = "5fgMIR1fLgyXRlrCtoK6kO"

print(f"🎵 Loading playlist: {PLAYLIST_ID}")
tracks = get_spotify_playlist_tracks(PLAYLIST_ID)

full_playlist = []

for idx, track in enumerate(tracks, 1):
    title = track.get("title")
    artist = track.get("artist")
    spotify_id = track.get("id")

    if not title or not artist:
        print(f"⚠️ Song with missing info: {track}")
        continue

    print(f"{idx}. 🎵 {title} — {artist}")

    # חיפוש באפל מיוזיק
    print(f"🔍 Searching Apple Music for: {title} {artist}")
    result = search_apple_music(title, artist)

    if result:
        found_artist = result.get("artist") or result.get("artistName", "").strip()
        url = result.get("trackViewUrl") or result.get("url", "")
        artwork = result.get("artworkUrl100") or "https://via.placeholder.com/100?text=%E2%99%AA"

        if artist_similarity(artist, found_artist):
            print(f"  ✅ Found on Apple Music: {title} — {found_artist}")
            full_playlist.append({
                "title": title,
                "artist": artist,
                "source": "apple",
                "url": url,
                "artworkUrl": artwork
            })
            continue
        else:
            print(f"  ⚠️ Artist mismatch: {artist} vs {found_artist}")
    else:
        print(f"  ❌ Not found on Apple Music: {title}")

    # אם לא נמצא או לא תאם
    filename = sanitize_filename(f"{artist} - {title}.mp3")
    download_url = f"https://spotidownloader.com/en?url=https://open.spotify.com/track/{spotify_id}"
    full_playlist.append({
        "title": title,
        "artist": artist,
        "source": "missing",
        "url": download_url,
        "artworkUrl": "https://via.placeholder.com/100?text=%E2%99%AA"
    })

# כתיבה לקובץ JSON אחיד
with open("full_playlist.json", "w", encoding="utf-8") as f:
    json.dump(full_playlist, f, ensure_ascii=False, indent=2)

print("✅ Done. full_playlist.json written.")
