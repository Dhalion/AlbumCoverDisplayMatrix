# Spotify Album Cover Art Display

## About

Python Script that fetches the track currently playing on your Spotify account, downloads the Cover Art and displays it on the RGB Matrix. Built to run on a Raypberry PI 1.

Downloaded Cover Arts are cached in `/covers`.  
`/gifs` stores GIFS that are dispalyed while IDLE.

### Built with:
* [Spotipy Spotify Library](https://github.com/spotipy-dev/spotipy)
* [rpi-rgb-led-matrix by hzeller](https://github.com/hzeller/rpi-rgb-led-matrix)


## Usage
The Script expects a `.env` file containing Spotify API credentials:  

    SPOTIPY_CLIENT_ID='[CLIENT ID]'
    SPOTIPY_CLIENT_SECRET='[CLIENT_SECRET]'
    SPOTIPY_REDIRECT_URI='[CALLBACK_URL]'

As provided in [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard)

On first launch the script will promt a Link to log in with your Spotify Account. Session tokens will be saved in `.cache` for later authentication. Details in [Spotipy Documentaion](http://spotipy.readthedocs.org/)