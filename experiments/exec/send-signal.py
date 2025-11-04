import socket
import sys

slaves = [
  ("172.20.20.11",  9201), # worker1
  ("172.20.20.12", 9202), # worker2
  ("172.20.20.13",  9203), # worker3
  ("172.20.20.14",  9204), # worker4
]

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

if len(sys.argv) < 2:
  print("usage: ./send-signal [start|stop]")
  exit(0)

for s in slaves:
  sock.sendto(str.encode(sys.argv[1]), s)

