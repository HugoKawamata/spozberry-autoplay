import subprocess
import time
import random
import sys
from mpd import MPDClient, ProtocolError
from threading import Thread, Lock
from termios import tcflush, TCIOFLUSH
import datetime


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
    if i == 0:
      client.play(i)
    else:
      if playlistInfo[i-1]["album"] != currentAlbum: # At the first song of album, want to go to prev album
        currentAlbum = playlistInfo[i-1]["album"]
        i -= 1
      while i >= 0:
        if playlistInfo[i]["album"] == currentAlbum:
          i -= 1
        else:
          break
      client.play(i+1)

def sleep_mode(client, stringOfHours):
  try: 
    sleepHours = float(stringOfHours)
    # Playing 15 minutes of music to aid sleep
    rockabyeTime = datetime.datetime.now() + datetime.timedelta(minutes=15)
    print("entering rockabye mode for 15 minutes")
    while (datetime.datetime.now() < rockabyeTime):
      client.status() # Ping the client to prevent timeouts
      time.sleep(50) # Default mpd timeout is 60 seconds
    # Going into sleep mode for reals
    wakeup = datetime.datetime.now() + datetime.timedelta(hours=sleepHours)
    print("sleeping for " + str(sleepHours) + " hours")
    client.pause()
    while (datetime.datetime.now() < wakeup):
      client.status();
      time.sleep(50) # Default mpd timeout is 60 seconds
    client.play()
  except ValueError:
    print("not a number of hours")

def wait_for_input(L, client, playlistList):
  paused = False

  while(1):
    tcflush(sys.stdin, TCIOFLUSH) # Flush all the crap entered while it wasn't listening.
    print("listening...") # We're listening
    L.append(input()) # Get an input

    clientLock.acquire() # "Hold my beer, ConnectionCheckingThread"
    if len(L) > 0:
      if "zzz" in L[0] and len(L[0].split()) > 1: # Sleep mode
        sleep_mode(client, L[0].split()[1])
      elif "r" in L[0]: # Reload Playlist
        client.clear()
        play_random_playlist(playlistList)
      elif "n" in L[0]: # N for next
        client.next()
      elif "p" in L[0]: # P for pause/play
        if paused == True:
          client.play()
        else:
          client.pause()
      elif "l" in L[0]: # Last album
        prev_album(client)
      elif "a" in L[0]: # A for skip to next album
        skip_album(client)
      elif "b" in L[0]: # B for back
        if int(client.status()["song"]) != 0:
          client.previous()
        else:
          client.play(0)

    while L != []: # Empty L so that new commands can be given
      L.remove(L[0])
    clientLock.release()

def play_random_playlist(playlistList):
  playlistNum = random.randint(0, len(playlistList) - 1)
  playlistName = playlistList[playlistNum]["playlist"] 
  # Playlistlist is a list of dicts representing playlists, the name of a 
  # playlist is under key "playlist"
  print("Playing playlist " + playlistName)
  client.clear()
  if playlistName[1] == "@": # @ indicates an album collection
    client.load(playlistName)
    randomise_by_album(client) # Shuffle but keep albums together
  else:
    client.load(playlistName) # Load a random playlist, plays in order
  client.play(0)
  return playlistName


if __name__ == '__main__':

  phoneIsConnected = False
  failedTicks = 0

  MyMAC = "9c:b2:b2:90:ef:1e"
  phoneMAC = MyMAC

  client = MPDClient()
  client.timeout = None # This doesn't stop the 60 second default mpd timeout.
  client.connect("localhost", 6600) # Connect to mopidy

  unfilteredPlaylists = client.listplaylists()
  # Only get playlists with second character "@" (yes this is fucked)
  playlistList = list(filter(lambda plDict: plDict["playlist"][1] == "@", unfilteredPlaylists))

  clientLock = Lock()

  L = []
  inputThread = Thread(target = wait_for_input, args = (L, client, playlistList))
  # Begin the input checking loop
  inputThread.start()

  # Begin the connection checking loop
  while True:
    if playlistList == []:
      break
    time.sleep(5)
    # Check whether the specified MAC address is on the network (thanks stack overflow)
    p = subprocess.Popen("sudo arp-scan -l | grep " + phoneMAC, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    
    clientLock.acquire()
    if output: # If the phone is connected
      failedTicks = 0
      print("It's on the network!")

      if phoneIsConnected == False: # The phone just connected
        phoneIsConnected = True
        play_random_playlist(playlistList)
      else: # The phone was already connected
        status = client.status()
        # Play a new playlist if the last one finished.
        if "state" in status and status["state"] == "stop":
          play_random_playlist(playlistList)


    else: # The phone is not connected
      print("It's not on the network")
      failedTicks += 1
      status = client.status()
      # If we got more than 7 failed pings, and the music is playing
      # (don't disconnect if paused, someone might want to come back to that spot in the playlist)
      if failedTicks > 7 and phoneIsConnected and "state" in status and status["state"] == "play":
        client.clear() # Empty playlist
        phoneIsConnected = False # Allow phone to reconnect if it is found again
    clientLock.release()