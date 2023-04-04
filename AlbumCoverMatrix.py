#!/usr/bin/env python

import platform
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from pprint import pprint
import time, sys
from PIL import Image
import urllib.request
import os.path
import glob
from enum import Enum
from dataclasses import dataclass


# Do not use Matrix Lib for Debugging on Windows
if platform.system() == "Windows":
    DEBUG = True
    print("## Debug Mode enabled ##")
    import PIL
else:
    DEBUG = False
    from rgbmatrix import RGBMatrix, RGBMatrixOptions



load_dotenv()

#*** STATES CLASS ***#
class State(Enum):
    ERROR = 0
    IDLE = 1
    STOPPED = 2
    PLAYING = 3

#*** Class holding Spotify Track ***#
@dataclass
class Track:
    title: str
    artist: str
    cover_url: str
    track_id: str
    album_id: str

class CoverArtDisplay():
    #*** CONSTANTS ***#
    SPOTIPY_CLIENT_ID       = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET   = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI    = os.getenv('SPOTIPY_REDIRECT_URI')

    COVER_IMAGE_PATH        = os.path.join(os.path.abspath(os.getcwd()) + "/covers/")
    POLLING_INTERVAL        = 2    # Poll Current Song every 2 Seconds
    IDLE_TIME_LIMIT         = 10

    CACHED_ALBUM_COVERS = []    #? Album cover Cache
    SCOPE = "user-read-currently-playing"

    SP = None                   #? SpotifyAPI Object
    state = None
    currentDisplayedTrack = None
    matrix = None
    idleTimer = None
    
    #***** CONSTRUCTOR *****#
    def __init__(self):
        #* LOAD CACHED COVER ARTS
        if self.loadCache():
            print("{} Cache Items Loaded".format(len(self.CACHED_ALBUM_COVERS)))
        else:
            print("Error Loading Cache")
            self.state = State.ERROR


        #* AUTHENTICATE WITH SPOTIFY API
        if self.authenticate():
            print("Authenticated sucessfully")
        else:
            print("Error while Authenticating with Spotify API")
            self.state = State.ERROR

        # Go to IDLE STATE now
        self.state = State.IDLE
        print("Stilus fidibus styler")

        #* INIT MATRIX
        self.initMatrix()

        self.loop()
        print("Stilus fidibus geiler")


    def loadCache(self):
        try:
            for file in glob.glob(self.COVER_IMAGE_PATH + "*.jpg"):
                self.CACHED_ALBUM_COVERS.append(os.path.basename(file).split(".")[0])
        except Exception as e:
            print(e)
            return False
        return True

    def authenticate(self):
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth( 
                    client_id=self.SPOTIPY_CLIENT_ID,
                    client_secret=self.SPOTIPY_CLIENT_SECRET,
                    redirect_uri=self.SPOTIPY_REDIRECT_URI,
                    scope=self.SCOPE,
                    open_browser=False
                ))
        except Exception as e:
            print(e)
            return False
        if sp:
            self.SP = sp
            return True
        else:
            return False


    def initMatrix(self):
        #* MATRIX CONFIG *#
        if not DEBUG:
            options = RGBMatrixOptions()
            options.rows = 64
            options.cols = 64
            options.chain_length = 1
            options.parallel = 1
            options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
            options.pixel_mapper_config = 'Rotate:90'
            options.pwm_lsb_nanoseconds = 90
            options.pwm_bits = 5
            options.brightness = 80
            options.scan_mode = 1
            options.show_refresh_rate = 0
            options.limit_refresh_rate_hz = 100

            self.matrix = RGBMatrix(options = options)

    def getCurrentPlayingTrack(self):
        res = self.SP.currently_playing()

        if not res:
            # Error while fetching currently Playing
            self.state = State.ERROR
            return False
        
        if not res["is_playing"]:
            # Nothing playing atm
            if self.state != State.STOPPED:
                # Dont refresh when already stopped
                print
                self.state = State.STOPPED
                self.idleTimer = time.time()
            return False
        # So a track is playing then
        self.state = State.PLAYING
        

        try:
            track = Track(
                    res["item"]["name"],
                    res["item"]["artists"][0]["name"],
                    res["item"]["album"]["images"][2]["url"],
                    res["item"]["id"],
                    res["item"]["album"]["id"]
                )
        except Exception as e:
            print("Error parsing track information", e)
            self.state = State.ERROR
            return False
        
        # Everything went well, return fetched track
        return track
        
    def downloadAlbumCover(self):
        id = self.currentDisplayedTrack.album_id
        url = self.currentDisplayedTrack.cover_url

        pwd = os.path.abspath(os.getcwd())
        filename = id + ".jpg"
        path = os.path.join(pwd + "/covers/" + filename)
        try:
            print("Downloading {} to {}".format(url, path))
            urllib.request.urlretrieve(url, path)

        except Exception as e:
            pprint("Error downloading cover Image." + e)
        
        self.CACHED_ALBUM_COVERS.append(id) # Add Cover to Cached List
        return

    def dispayCoverImageOnMatrix(self):
        if not self.currentDisplayedTrack.album_id in self.CACHED_ALBUM_COVERS:
            # Cover image is not already in chache -> Download it
            self.downloadAlbumCover()

        pwd = os.path.abspath(os.getcwd())
        filename = self.currentDisplayedTrack.album_id + ".jpg"
        path = os.path.join(pwd + "/covers/" + filename)
        print("Displaying {}".format(path))
        img = Image.open(path)
        # img.show()
        if not DEBUG:
            self.matrix.SetImage(img.convert('RGB'))   # Display Image on Matrix
        else:
            print("[DEBUG] Displaying Cover {}".format(self.currentDisplayedTrack.album_id))

    def displayIDLE(self):
        file = os.path.join(os.path.abspath(os.getcwd()), "unicorn.jpg")
        img = Image.open(file)
        img.thumbnail((64,64), resample=Image.LANCZOS)
        if not DEBUG:
            self.matrix.SetImage(img.convert('RGB'))   # Display Image on Matrix
        else:
            img.show()
            print("[DEBUG] Displaying IDLE")
        pass

    def loop(self):
        while True:
            if self.state == State.PLAYING:
                    time.sleep(self.POLLING_INTERVAL)
            
            if self.state == State.STOPPED:
                if time.time() - self.idleTimer > self.IDLE_TIME_LIMIT:
                    self.displayIDLE()
                    time.sleep(5)

            if self.state == State.ERROR:
                self.authenticate()
                # Try to recover from Erro
                pass
            
            if self.state == State.IDLE:
                pass

            track = self.getCurrentPlayingTrack()
            if track:
                if track != self.currentDisplayedTrack:
                    print("New Track playing.")
                    pprint(track)
                    # Push Cover Image to Display
                    self.currentDisplayedTrack = track
                    self.dispayCoverImageOnMatrix()
                time.sleep(1)   # Wait 1sec before next check


    

if __name__ == "__main__":
    cad = CoverArtDisplay()
