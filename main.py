import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

inject = "spotify:track:"
scope = "user-library-read playlist-modify-private playlist-read-private user-read-recently-played"
# removed my ids and passwords, couldn't get environmental variables to work
SPOTIPY_CLIENT_ID = "XXX"
SPOTIPY_CLIENT_SECRET = "XXX"
SPOTIPY_REDIRECT_URL = "XXX"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                               client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URL))
spotify_site = f"https://api.spotify.com/v1/users/{sp.current_user()['id']}/playlists/"
search_api = "https://api.spotify.com/v1/search"
song_id = ""
ids = []

site = "https://www.billboard.com/charts/hot-100/"
date = input("Welcome to the playlist generator. Enter the date using the following format: 'YYYY-MM-DD': ")
# date = "2000-01-01"

response = requests.get(url=site+date)
soup = BeautifulSoup(response.text, "html.parser")
list_of_100 = soup.find_all(class_="chart-element__information__song text--truncate color--primary")

# NO IDEA BUT THIS LINE MIGHT BE REFRESHING THE BEARER TOKEN SO I'M LEAVING IT IN __EDIT: might be redundant
# since I call this method in spotify_site, but I'm leaving it for sanity's sake.

sp.current_user()
# .cache file wasn't uploaded since it contains my token but it should be created by authorisation process above.
with open(".cache") as file:
    data = file.readline()
    token = data.split()[1].split('"')[1]

header = {
    "Authorization": "Bearer " + token
}

print("Looking for song IDs, please wait...")

for song in list_of_100:
    song.getText()
    query = {
        "query": f"track: {song.getText()} year: {int(date.split('-')[0]) - 1}-{date.split('-')[0]}",
        "type": "track",
        "limit": 1,
    }
    result = requests.get(url="https://api.spotify.com/v1/search", headers=header, params=query)
    try:
        song_id = result.json()["tracks"]["items"][0]["id"]
    except IndexError:
        song_id = ""
        pass
    if song_id != "":
        song_id = inject + song_id
        ids.append(song_id)
print("Finished the search! Preparing the playlist, please wait...")


# I COULDN'T GET THE POST REQUEST TO WORK, ALWAYS GAVE OFF 403 - INSUFFICIENT SCOPE
# query_playlist = {
#     "user": sp.current_user()["id"],
#     "name": f"{date} Billboard top 100",
#     "public": False,
#     "collaborative": False,
#     "description": f"Top 100 Billboard songs from {date}"
# }
# playlist_response = requests.post(url=spotify_site, headers=header, params=query_playlist)
#
# print(playlist_response.json())


playlist_id = sp.user_playlist_create(
    user=sp.current_user()["id"],
    name=f"{date} Billboard top 100",
    public=False,
    collaborative=False,
    description=f"Top 100 Billboard songs from {date}")["id"]

header_add_tracks = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
}

query_add_tracks = {
    "uris": ids
}

add_track_endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
add_track = requests.post(url=add_track_endpoint, headers=header_add_tracks, json=query_add_tracks)
if add_track.status_code <= 201:
    print("Playlist is ready!")
else:
    print("Oops, something went wrong. ;( See the below for further information:")
    print(add_track.text)

