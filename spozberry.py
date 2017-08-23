import subprocess
import time
import random
from mpd import MPDClient
from threading import Thread

# My phone's mac address = 9c:b2:b2:90:ef:1e

def play_random_playlist(playlistList, lastPlaylistName = None):
  playlistName = lastPlaylistName
  while playlistName == lastPlaylistName:
    playlistNum = random.randint(0, len(playlistList) - 1)
    playlistName = playlistList[playlistNum]["playlist"]
  print("Playing playlist " + playlistName)
  client.load(playlistName) # Load a random playlist
  client.play(0)
  return playlistName


if __name__ == '__main__':

  phoneIsConnected = False
  failedTicks = 0

  MyMAC = "9c:b2:b2:90:ef:1e"
  phoneMAC = MyMAC

  client = MPDClient()
  client.timeout = 10
  client.connect("localhost", 6600)

  unfilteredPlaylists = client.listplaylists()
  playlistList = list(filter(lambda plDict: plDict["playlist"][0] == "$", unfilteredPlaylists))

  currentPlaylist = ""

  while True:
    if playlistList == []:
      break
    time.sleep(10)
    p = subprocess.Popen("sudo arp-scan -l | grep " + phoneMAC, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if output:
      failedTicks = 0
      print("It's on the network!")

      if phoneIsConnected == False: # The phone just connected
        phoneIsConnected = True
        currentPlaylist = play_random_playlist(playlistList)
      else:
        if len(client.playlistinfo()) == 0:
          print(client.playlist())
          play_random_playlist(playlistList, currentPlaylist)

        # Check if playlist is almost run out
        # Randomly pick another playlist with a different name
        # Load that playlist
    else:
      print("It's not on the network")
      failedTicks += 1
      if failedTicks > 7:
        phoneIsConnected = False
        client.clear()