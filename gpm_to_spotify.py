import json
import getpass
import os
import re
import spotipy
import spotipy.util
import sys

from gmusicapi import Mobileclient

def gpm_login():
    gpm_api = Mobileclient()
    username = raw_input("Enter your Google Play Music email address: ")
    password = getpass.getpass("Enter your password: ")

    if (not gpm_api.login(username, password, Mobileclient.FROM_MAC_ADDRESS, 'en_US')):
        print("Unable to login to Google Play Music.")
        sys.exit(-1)

    return gpm_api

def spotify_login():
    scope = 'user-library-modify'
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
    REDIRECT_URL = "http://localhost"

    spotify_username = raw_input("Enter your Spotify username: ")

    token = spotipy.util.prompt_for_user_token(spotify_username, scope, 
            SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URL)

    if (not token):
        print("Unable to get Spotify login token.")
        sys.exit(-1)

    return token

def sanitize(string):
    return re.sub('[-!@#$%^&*=+_;:,.<>?/|]', ' ', string)

def get_track_id(spotify, query):
    results = spotify.search(query, type='track', limit=1)
    json.dump(results, result_file, indent=4, sort_keys=True)
    if (results['tracks']['total'] > 0):
        track_id = results['tracks']['items'][0]['id']
        for result in results['tracks']['items']:
            if (result['album']['name'] == album):
                track_id = result['id']
    else:
        raise Exception('Not found')

gpm_api = gpm_login()

token = spotify_login()

out_file = open('out.txt', 'w')
result_file = open('results.txt', 'w')

print("Loading all songs from Google Play Music, this might take some time...")
songs = gpm_api.get_all_songs()

# dump file for debugging
json.dump(songs, out_file, indent=4, sort_keys=True)

spotify = spotipy.Spotify(auth=token)
ids = []

print("Couldn't add:")
for track in songs:
    album = track[u'album']
    artist = track[u'artist']
    title = track[u'title']

    query = u"track:{0} artist:{1}".format(sanitize(title), sanitize(artist))
    try:
        track_id = get_track_id(spotify, query)
        ids.append(track_id)
        if (len(ids) >= 50):
            print('Adding tracks (not really)')
            # spotify.current_user_saved_tracks_add(ids)
            ids = []
    except Exception:
        query = u"track{0} artist:{1}".format(sanitize(title.split('(')[0]), sanitize(artist.split('&')[0]))
        try:
            track_id = get_track_id(spotify, query)
            ids.append(track_id)
            if (len(ids) >= 50):
                print('Adding tracks (not really)')
                # spotify.current_user_saved_tracks_add(ids)
                ids = []
        except Exception:
            print(u"{0} - {1} - {2}".format(title, artist, album))
