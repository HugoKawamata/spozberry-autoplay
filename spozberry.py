import subprocess
import time
from mpd import MPDClient

# My phone's mac address = 9c:b2:b2:90:ef:1e


if __name__ == '__main__':

  MyMAC = "9c:b2:b2:90:ef:1e"
  phoneMAC = MyMAC

  client = MPDClient()
  client.timeout = 10
  client.connect("localhost", 6600)

  # Make a list of all the playlists with $ at the start

  # Randomly order them


  while True:
    phoneIsConnected = False
    time.sleep(5)
    # TODO: remove sudo from the following command:
    p = subprocess.Popen("sudo arp-scan -l | grep " + phoneMAC, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if output:
      print(client.listplaylists())
      print("It's on the network!")
      if !phoneIsConnected: # The phone just connected
        phoneIsConnected = True
        client.load() # Load the first playlist in the queue
      else:
        # Check if playlist is almost run out
        # Randomly pick another playlist with a different name
        # Load that playlist
    else:
      print("It's not on the network")
