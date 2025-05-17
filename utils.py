import json
import re
import os

MISSING_JSON = "missing_songs.json"

def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "", text)

def add_to_missing_songs(title, artist, filename):
    url = f"https://example.com/{filename.replace(' ', '%20')}"  # החלף לפי המערכת שלך

    try:
        with open(MISSING_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    for item in data:
        if item["title"] == title and item["artist"] == artist:
            return

    data.append({
        "title": title,
        "artist": artist,
        "download_url": url
    })

    with open(MISSING_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_apple_matches_json(matches, output_file="apple_matches.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
