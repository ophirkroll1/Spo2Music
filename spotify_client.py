import requests
import base64
import os

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

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

def get_spotify_playlist_tracks(playlist_id):
    access_token = get_access_token()
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"limit": 100}
    results = []

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data["items"]:
            track = item["track"]
            if not track:
                continue
            results.append({
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "id": track["id"]
            })
        url = data.get("next")

    return results
