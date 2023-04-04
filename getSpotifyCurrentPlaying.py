import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from pprint import pprint
import time 
from PIL import Image
import urllib.request
import os.path
import glob

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

POLLING_INTERVAL = 2 # Poll Current Song every 2 Seconds
COVER_IMAGE_PATH = os.path.join(os.path.abspath(os.getcwd()) + "/covers/")

CACHED_ALBUM_COVERS = []

DEBUG_SHOW_IMAGE = False


scope = "user-read-currently-playing"
sp = spotipy.Spotify()


def authenticate(sp):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth( client_id="YOUR_APP_CLIENT_ID",
                                                    client_secret="YOUR_APP_CLIENT_SECRET",
                                                    redirect_uri="YOUR_APP_REDIRECT_URI",
                                                    open_browser=False,
                                                    scope=scope
                                                    ))
    return sp


def getCurrentlyPlaying(sp):
    res = (sp.currently_playing())

    track = {}

    if res["is_playing"]:
        track["name"] = res["item"]["name"]
        track["artist"] = res["item"]["artists"][0]["name"]
        track["img_url"] = res["item"]["album"]["images"][2]["url"]
        track["track_id"] = res["item"]["id"]
        track["album_id"] = res["item"]["album"]["id"]
    # pprint(track)

    return track


def downloadAlbumCover(url, id):

    if id in CACHED_ALBUM_COVERS:
        print("Image already in Cache")
        return # Image already cached
    
    pwd = os.path.abspath(os.getcwd())
    filename = id + ".jpg"
    path = os.path.join(pwd + "/covers/" + filename)
    try:
        print("Downloading {} to {}".format(url, path))
        urllib.request.urlretrieve(url, path)

    except Exception as e:
        pprint(e)
    
    CACHED_ALBUM_COVERS.append(id) # Add Cover to Cached List

def loadCachedCoverImageIDs():
    for file in glob.glob(COVER_IMAGE_PATH + "*.jpg"):
        CACHED_ALBUM_COVERS.append(os.path.basename(file).split(".")[0])
    pprint(CACHED_ALBUM_COVERS)

def showAlbumCoverImage(id):
    if not DEBUG_SHOW_IMAGE:
        return
    pwd = os.path.abspath(os.getcwd())
    filename = id + ".jpg"
    path = os.path.join(pwd + "/covers/" + filename)
    img = Image.open(path)
    img.show()

if __name__ == "__main__":
    # pprint(SPOTIPY_CLIENT_ID)
    loadCachedCoverImageIDs()
    sp = authenticate(sp)
    currentTrack = getCurrentlyPlaying(sp)
    downloadAlbumCover(currentTrack["img_url"],currentTrack["album_id"])
    showAlbumCoverImage(currentTrack["album_id"])
    pprint(currentTrack)

    
    while True:
        track = getCurrentlyPlaying(sp)
        if track["track_id"] != currentTrack["track_id"]:
            currentTrack = track
            pprint("New Track Playing:")
            pprint(currentTrack)
            downloadAlbumCover(currentTrack["img_url"],currentTrack["album_id"])
            showAlbumCoverImage(currentTrack["album_id"])
        time.sleep(POLLING_INTERVAL)




