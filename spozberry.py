import subprocess
import time
import random
import sys
from mpd import MPDClient, ProtocolError
from threading import Thread, Lock
from termios import tcflush, TCIOFLUSH


# My phone's mac address = 9c:b2:b2:90:ef:1e

def randomise_by_album(client):
  currentPlaylist = client.playlistinfo()
  while(len(currentPlaylist) == 0):
    print("Oops, got an empty playlistinfo()")
    time.sleep(4)
    currentPlaylist = client.playlistinfo()
  client.clear()
  shuffledPlaylist = []
  i = 0
  #while client.playlistinfo()[i]["album"]
  print("currentPlaylist should contain songs, owo what's this? " + str(currentPlaylist[0]))
  while i < len(currentPlaylist):
    album = []
    album.append(currentPlaylist[i])
    i += 1
    while i < len(currentPlaylist) and currentPlaylist[i]["album"] == album[0]["album"]:
      album.append(currentPlaylist[i])
      i += 1

    shuffledPlaylist.append(album)

  random.shuffle(shuffledPlaylist)
  for album in shuffledPlaylist:
    for song in album:
      #print(song["file"] + " " + song["title"])
      client.add(song["file"])
        
def skip_album(client):
  currentSong = client.currentsong()
  if "album" in currentSong:
    currentAlbum = client.currentsong()["album"]
    playlistInfo = client.playlistinfo()
    i = int(client.status()["song"])
    while i < len(client.playlistinfo()): 
      if playlistInfo[i]["album"] == currentAlbum:
        i += 1
      else:
        break

    if i < len(playlistInfo):
      client.play(i)
    else:
      client.stop()

def prev_album(client):
  currentSong = client.currentsong()
  if "album" in currentSong:
    currentAlbum = client.currentsong()["album"]
    playlistInfo = client.playlistinfo()
    i = int(client.status()["song"])
    if i > 0 and playlistInfo[i-1]["album"] != currentAlbum: # At the first song of album, want to go to prev album
      currentAlbum = playlistInfo[i-1]["album"]
      i -= 1
    while i > 0:
      if playlistInfo[i]["album"] == currentAlbum:
        i -= 1
      else:
        break
    client.play(i+1)

def wait_for_input(L, client, playlistList):
  paused = False

  while(1):
    tcflush(sys.stdin, TCIOFLUSH) # Flush all the crap entered while it wasn't listening.
    print("listening...")
    L.append(input())

    clientLock.acquire()
    if len(L) > 0:
      if " " in L[0]: # Reload Playlist
        client.clear()
        play_random_playlist(playlistList)
      elif "n" in L[0]: # N for next
        client.next()
      elif "p" in L[0]: # P for pause/play
        if paused == True:
          client.play()
        else:
          client.pause()
      elif "z" in L[0]: # Z because I'm running out of letters
        prev_album(client)
      elif "a" in L[0]: # A for skip to next album
        skip_album(client)
      elif "b" in L[0]: # B for back
        client.previous()

    while L != []: # Make sure L is always empty at the start of a listen
      L.remove(L[0])
    clientLock.release()



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
  client.timeout = 100
  client.connect("localhost", 6600)

  unfilteredPlaylists = client.listplaylists()
  playlistList = list(filter(lambda plDict: plDict["playlist"][1] == "@", unfilteredPlaylists))

  clientLock = Lock()

  L = []
  inputThread = Thread(target = wait_for_input, args = (L, client, playlistList))
  inputThread.start()

  while True:
    if playlistList == []:
      break
    time.sleep(5)
    clientLock.acquire()
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
        status = client.status()
        if "state" in status and status["state"] == "stop":
          play_random_playlist(playlistList)


    else:
      print("It's not on the network")
      failedTicks += 1
      if failedTicks > 5:
        client.clear()
        phoneIsConnected = False
    clientLock.release()