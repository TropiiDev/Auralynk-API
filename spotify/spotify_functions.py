import base64
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from requests import post, get

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

time_file = "./spotify/time.txt"

def save_future_time(future_time):
    with open(time_file, 'w') as file:
        file.write(future_time.isoformat())

def get_spotify_token():
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_res = json.loads(result.content)
    token = json_res['access_token']
    expires_in = json_res['expires_in']

    future_time = datetime.now() + timedelta(seconds=expires_in)
    save_future_time(future_time)

    return token

def spotify_refresh_token(token):
    url = "https://accounts.spotify.com/api/token"
    data = {"grant_type": "refresh_token", "refresh_token": token}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    result = post(url, headers=headers, data=data)

    if result.status_code == 200:
        json_res = json.loads(result.content)
        token = json_res['access_token']
        return token
    else:
        print(f"Error: {result.status_code}")
        return None

def get_valid_spotify_token(token):
    if os.path.exists(time_file):
        with open(time_file, 'r') as file:
            future_time_str = file.read()
            time =  datetime.fromisoformat(future_time_str)

            current_time = datetime.now()

            if current_time > time:
                new_token = spotify_refresh_token(token)
                return new_token
            else:
                return token

    else:
        token = get_spotify_token()
        return token

def get_spotify_header(token):
    return {"Authorization": "Bearer " + token}

def spotify_search_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_spotify_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_res = json.loads(result.content)['artists']['items']
    if len(json_res) == 0:
        print("No artist with this name exists...")
        return None

    return json_res[0]

def spotify_search_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_spotify_header(token)
    query = f"?q={track_name}&type=track&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_res = json.loads(result.content)['tracks']['items']
    if len(json_res) == 0:
        print("No track with this name exists...")
        return None

    return json_res[0]

def spotify_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_spotify_header(token)
    result = get(url, headers=headers)
    json_res = json.loads(result.content)["tracks"]

    return json_res