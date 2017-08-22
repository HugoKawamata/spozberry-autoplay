import subprocess
import time

# My phone's mac address = 9c:b2:b2:90:ef:1e


if __name__ == '__main__':

  MyMAC = "9c:b2:b2:90:ef:1e"
  phoneMAC = MyMAC

  while True:
    time.sleep(5)
    # TODO: remove sudo from the following command:
    p = subprocess.Popen("sudo arp-scan -l | grep " + phoneMAC, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    if output:
      print("It's on the network!")
    else:
      print("It's not on the network")