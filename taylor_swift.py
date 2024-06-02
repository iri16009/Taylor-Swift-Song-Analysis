# Which keys is Taylor most interested on?
# What's Taylor Swift singing range?
# Most popular Taylor Swift Chord Progressions

import requests
import pandas as pd
from configparser import ConfigParser

### -------------------- GET CREDENTIALS ------------------------------------- ###
ini_file = ConfigParser()
ini_file.read("taylor_swift_songs.ini")
CLIENT_ID = ini_file["DEFAULT"]["CLIENT_ID"]
CLIENT_SECRET = ini_file["DEFAULT"]["CLIENT_SECRET"]

### -------------------- AUTHENTICATION AUTHORIZATION ------------------------###
AUTH_URL = 'https://accounts.spotify.com/api/token'

auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

### -------------- BASE VARIABLES 
BASE_URL  = "https://api.spotify.com/v1/"

# You can get Taylor's artist id from her Spotify URL: 
# https://open.spotify.com/intl-es/artist/06HL4z0CvFAxyc27GXpf02?si=muMWWV6XSK2YDMjkK3eLVw
ARTIST_ID = "06HL4z0CvFAxyc27GXpf02" # Taylor Swift
KEY_DICT = {0: "C", 
            1: "C#",
            2: "D",
            3: "Eb",
            4: "E",
            5: "F",
            6: "F#",
            7: "G",
            8: "Ab",
            9: "A",
            10: "Bb",
            11: "B",
            -1: "NO KEY FOUND"
            }

MODE_DICT ={
    0: "Minor",
    1: "Major",
    -1: "NO MODE FOUND"
}

TSIGNATURE_DICT = {
    3: "3/4",
    4: "4/4",
    5: "5/4",
    6: "6/4",
    7: "7/4",
    1: "1/4"
}

ALBUM_LIST = ["THE TORTURED POETS DEPARTMENT: THE ANTHOLOGY",
              "Midnights (The Til Dawn Edition)", 
              "evermore (deluxe version)", 
              "folklore (deluxe version)", 
              "Lover", "reputation", 
              "1989 (Taylor's Version) [Deluxe]", 
              "Red (Taylor's Version)", 
              "Speak Now (Taylor's Version)", 
              "Fearless (Taylor's Version)", 
              "Taylor Swift"]

additional_tracks_ids = {
    "3CWq0pAKKTWb0K4yiglDc4": "Midnights (The Til Dawn Edition)",
    "4axSuOg3BqsowKjRpj59RU": "Other",
    "6N1K5OVVCopBjGViHs2IvP": "Other",
    "6Q237Ts37YGYRIi5Vy5lVX": "Red (Taylor's Version)",
    "2NIBaWXdjaTDmytjjwbEfP": "Red (Taylor's Version)",
    "06zIBqLC9ZRm5i0iMf0kHI": "Other",
    "0kAZ3H6G9Zac4PMpmobMkj": "Fearless (Taylor's Version)",
    "2slqvGLwzZZYsT4K4Y1GBC": "Other",
    "2mvabkN1i2gLnGAPUVdwek": "Other",
    "4P9Q0GojKVXpRTJCaL3kyy": "Lover",
    "0RFCHlNuTeUHIB36VuVbOL": "Other"
}

### ----------------------------------- CODE --------------------------------- ###

##################################################################################
### ------------------------------ Get all albums ---------------------------- ###
def get_taylors_albums():
    response = requests.get(BASE_URL + 'artists/' + ARTIST_ID + '/albums', 
                    headers=headers, 
                    params={'include_groups': 'album', 'limit': 50})
    json_response = response.json()

    for album in json_response['items']:
        print(album['name'], ' - ', album['release_date'])
##################################################################################

"""
-------------------------------------------------
    We're interested in the following albums:
-------------------------------------------------
THE TORTURED POETS DEPARTMENT: THE ANTHOLOGY  -  2024-04-19
Midnights (The Til Dawn Edition)  -------------  2023-05-26
evermore (deluxe version)  --------------------  2021-01-07
folklore (deluxe version)  --------------------  2020-08-18
Lover  ----------------------------------------  2019-08-23
reputation  -----------------------------------  2017-11-10
1989 (Taylor's Version) [Deluxe]  -------------  2023-10-27
Red (Taylor's Version)  -----------------------  2021-11-12
Speak Now (Taylor's Version)  -----------------  2023-07-07
Fearless (Taylor's Version)  ------------------  2021-04-09
Taylor Swift  ---------------------------------  2006-10-24
"""

##################################################################################
### ------------ Get track information from albums we're interested -----------
##################################################################################
"""
1. Iterate albums
2. Iterate tracks from albums
3. Get info from tracks and save it
4. Create dataframe with saved info
5. Export dataframe to csv to use it later.
"""

data = []
track_trimmed_list = [] # to keep track of duplicates

response = requests.get(BASE_URL + 'artists/' + ARTIST_ID + '/albums', 
                 headers=headers, 
                 params={'include_groups': 'album', 'limit': 50})
json_response = response.json()


for album in json_response['items']:
    album_name = album['name']
    album_date = album['release_date']
    if album_name in ALBUM_LIST:
        print('Processing ', album_name, ' --- ', album_date)
        track_response = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=headers)
        tracks = track_response.json()['items']
        for track in tracks:
            # print(track)
            track_response = requests.get(BASE_URL + 'audio-features/' + track['id'], headers=headers)
            track_response = track_response.json()
            # print(track_response)
            track_name = track['name']
            track_trimmed = track_name.split("(")[0]
            # Do not include duplicate tracks
            if track_trimmed not in track_trimmed_list:
                track_trimmed_list.append(track_trimmed)
                # print(track_response)
                # print(track)
                # combine with album info
                taylor_track_info = {
                    'track_name': track_name,
                    'album_name': album_name,
                    'key': KEY_DICT[track_response['key']],
                    'mode': MODE_DICT[track_response['mode']],
                    'tempo': track_response['tempo'], # BPM
                    'energy': track_response['energy']*100, # Percentage
                    'danceability': track_response['danceability']*100, # Percentage,
                    'duration_min': track_response['duration_ms']/60000,
                    'time_signature': TSIGNATURE_DICT[track_response['time_signature']],
                    'valence': track_response['valence']*100, # Percentage
                    'acousticness': track_response['acousticness']*100, # Percentage
                    'instrumentalness': track_response['instrumentalness']*100, # Percentage
                    'liveness': track_response['liveness']*100, # Percentage
                    'loudness': track_response['loudness'], # Decibel
                    'speechiness': track_response['speechiness']*100, # Percentage
                    'release_date': album_date,
                    'album_id': album['id']
                }
                data.append(taylor_track_info)

"""
We'll need to add single tracks like:

* You're losing me ------------------------- Midnights
* Carolina - From The Motion Picture ------- Other
* The Joker And The Queen ------------------ Other
* Safe & Sound ----------------------------- Red TV
* Eyes Open -------------------------------- Red TV
* Renegade --------------------------------- Other
* If This Was A Movie (Taylor's Version) --- Fearless TV
* Only The Young --------------------------- Other
* Christmas Tree Farm ---------------------- Other
* All Of The Girls You Loved Before -------- Lover
* Sweeter Than Fiction --------------------- Other
* Remixes, Live Performances, I Don't Wanna Live Forever, and The Taylor Swift Holiday Collection were excluded from this analysis.
"""

for track_id in additional_tracks_ids:
    general_track_response = requests.get(BASE_URL + 'tracks/' + track_id, headers=headers)
    general_track_response = general_track_response.json()

    track_name = general_track_response['name']
    print(track_name)
    album_id = general_track_response['album']["id"]
    release_date = general_track_response['album']['release_date']

    track_response = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
    track_response = track_response.json()
    taylor_track_info = {
            'track_name': track_name,
            'album_name': additional_tracks_ids[track_id],
            'key': KEY_DICT[track_response['key']],
            'mode': MODE_DICT[track_response['mode']],
            'tempo': track_response['tempo'], # BPM
            'energy': track_response['energy']*100, # Percentage
            'danceability': track_response['danceability']*100, # Percentage,
            'duration_min': track_response['duration_ms']/60000,
            'time_signature': TSIGNATURE_DICT[track_response['time_signature']],
            'valence': track_response['valence']*100, # Percentage
            'acousticness': track_response['acousticness']*100, # Percentage
            'instrumentalness': track_response['instrumentalness']*100, # Percentage
            'liveness': track_response['liveness']*100, # Percentage
            'loudness': track_response['loudness'], # Decibel
            'speechiness': track_response['speechiness']*100, # Percentage
            'release_date': release_date,
            'album_id': album_id
        }
    data.append(taylor_track_info)


df = pd.DataFrame(data)
df['release_date'] = pd.to_datetime(df['release_date'])
df.to_csv("taylor_swift_songs_2024-06-01.csv", index=False)
print(df.head())

##################################################################################







