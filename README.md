# spozberry-autoplay
A spotify autoplayer for raspberry pi (or other unix systems).
Spozberry is only compatible with Spotify Premium accounts.

## Setup
- Ensure all playlists you want spozberry to play are named with a "$" at the front
- Ensure all playlists you want spozberry to "shuffle by album" are named with a "@" after the "$". These will likely be album collections.
- Ensure you have permission to access /dev/bp* files, or add the following to your `sudo visudo` file: `<yourusername> ALL=NOPASSWD: arp-scan`.
- Install mopidy
- Install ncmpcpp (optional: allows you to visualise playlists and have finer control over playback)
- Go to `~/.config/mopidy/mopidy.conf`
- Ensure your conf file has at least the following:
```
[mpd]
hostname = ::

[spotify]
enabled = true
username = YOURUSERNAME
password = YOURPASSWORD
allow_playlists = true

[local]
media_dir = ~/Music
```
- Launch mopidy so that spozberry has something to connect to (`mopidy`)
- Open a new terminal
- Within a venv (or not if you're fast and loose), `pip3 install -r requirements.txt`
- `python3 spozberry.py`
- When spozberry detects your phone, it will automatically play a compatible playlist.
- (Optional) Open another terminal and run `ncmpcpp` to view your song queue and use their extensive command control.

## Usage
While spozberry is running, it will accept user input.
- `PLAYLISTNAME`: Play the playlist called PLAYLISTNAME. Full name must be typed out, including any symbols.
- `zzz [number]`: Sleep mode (Spozberry enters rockabye mode for 15 minutes and will continue to play music. Once 15 minutes is up, it will go into real sleep mode and wait the number of hours specified in the arguments. Once the time has elapsed, spozberry will resume music automatically again, from where it left off)
- `r`: Reload playlist (Spozberry picks a new random playlist from your compatible playlists and plays it.)
- `p`: Pause/play. Keep in mind that pausing before leaving the house is unnecessary, as Spozberry will automatically stop when it realises your phone is no longer connected to the network.
- `b`: Back one song.
- `n`: Next song.
- `l`: Last album (Skips back to the first song in the current album, or the previous album if already on the first song)
- `a`: Next album (Skips forward to the first song in the next album)

