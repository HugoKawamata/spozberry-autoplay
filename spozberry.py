import subprocess
import time
import random
import sys
from mpd import MPDClient
from threading import Thread

# My phone's mac address = 9c:b2:b2:90:ef:1e

def randomise_by_album(client):
  currentPlaylist = client.playlistinfo()
  shuffledPlaylist = []
  i = 0
  #while client.playlistinfo()[i]["album"]
  while i < len(currentPlaylist):
    album = []
    album.append(currentPlaylist[i])
    i += 1
    while i < len(currentPlaylist) and currentPlaylist[i]["album"] == album[0]["album"]:
      album.append(currentPlaylist[i])
      i += 1

    shuffledPlaylist.append(album)

  client.clear()
  random.shuffle(shuffledPlaylist)
  for album in shuffledPlaylist:
    for song in album:
      client.add(song["file"])
  


def wait_for_input(L, client):
  paused = False

  while(1):
    print("listening...")
    L.append(input())

    if len(L) > 0:
      if " " in L[0]: # Reload Playlist
        client.clear()
        play_random_playlist(playlistList)
      else:
        if "n" in L[0]: # N for next
          client.next()
        if "p" in L[0]: # P for pause/play
          if paused == True:
            client.play()
          else:
            client.pause()
        if "a" in L[0]: # A for skip to next album
          currentAlbum = client.currentsong()["album"]
          playlistInfo = client.playlistinfo()
          print(currentAlbum)
          i = int(client.status()["song"])
          while i < len(client.playlistinfo()): 
            if playlistInfo[i]["album"] == currentAlbum:
              i += 1
            else:
              break

          if i < len(client.playlistinfo()):
            client.play(i)
          else:
            client.stop()

      while L != []: # Make sure L is always empty at the start of a listen
        L.remove(L[0])


def play_random_playlist(playlistList):
  playlistNum = random.randint(0, len(playlistList) - 1)
  playlistName = playlistList[playlistNum]["playlist"]
  print("Playing playlist " + playlistName)
  client.clear()
  if playlistName[1] == "@":
    client.load(playlistName)
    randomise_by_album(client) # Shuffle but keep albums together
  else:
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
  playlistList = list(filter(lambda plDict: plDict["playlist"][1] == "@", unfilteredPlaylists))


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
        play_random_playlist(playlistList)
      else:
        print(client.status()["state"])
        if client.status()["state"] == "stop":
          play_random_playlist(playlistList)


    else:
      print("It's not on the network")
      failedTicks += 1
      if failedTicks > 5:
        client.clear()
        phoneIsConnected = False
