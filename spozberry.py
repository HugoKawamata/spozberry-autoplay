import subprocess
import time
import random
from mpd import MPDClient
from threading import Thread

# My phone's mac address = 9c:b2:b2:90:ef:1e

def wait_for_input(L, client):
  paused = False

  while(1):
    print("listening...")
    print("L is " + str(L))
    L.append(input())

    if len(L) > 0:
      if " " in L[0]: # Reload Playlist
        client.clear()
        play_random_playlist(playlistList, currentPlaylist)
      if "n" in L[0]: # N for next
        client.next()
      if "p" in L[0]: # P for pause/play
        if paused == True:
          client.play()
        else:
          client.pause()

      while L != []: # Make sure L is always empty at the start of a listen
        L.remove(L[0])


def play_random_playlist(playlistList, lastPlaylistName = None):
  playlistName = lastPlaylistName
  while playlistName == lastPlaylistName:
    playlistNum = random.randint(0, len(playlistList) - 1)
    playlistName = playlistList[playlistNum]["playlist"]
  print("Playing playlist " + playlistName)
  client.clear()
  client.load(playlistName) # Load a random playlist
  client.play(0)
  return playlistName


if __name__ == '__main__':

  phoneIsConnected = False
  failedTicks = 0

  MyMAC = "9c:b2:b2:90:ef:1e"
  phoneMAC = MyMAC

  client = MPDClient()
  client.timeout = 20
  client.connect("localhost", 6600)

  unfilteredPlaylists = client.listplaylists()
  playlistList = list(filter(lambda plDict: plDict["playlist"][0] == "$", unfilteredPlaylists))

  currentPlaylist = ""

  L = []
  inputThread = Thread(target = wait_for_input, args = (L, client))
  inputThread.start()

  while True:
    if playlistList == []:
      break
    time.sleep(5)
    p = subprocess.Popen("sudo arp-scan -l | grep " + phoneMAC, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    
    if output: # If the phone is connected
      failedTicks = 0
      print("It's on the network!")

      if phoneIsConnected == False: # The phone just connected
        phoneIsConnected = True
        currentPlaylist = play_random_playlist(playlistList)
      else:
        if len(client.playlistinfo()) == 0:
          print(client.playlist())
          play_random_playlist(playlistList, currentPlaylist)


    else:
      print("It's not on the network")
      failedTicks += 1
      if failedTicks > 5:
        client.clear()
        phoneIsConnected = False
