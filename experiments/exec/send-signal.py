import socket
import sys

slaves = [
  ("10.0.0.1",  9201), # worker1
  ("10.0.0.2", 9202), # worker2
  # ("10.0.0.3",  9203), # worker3
  # ("10.0.0.4",  9204), # worker4
]

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

if len(sys.argv) < 2:
  print("usage: ./send-signal [start|stop]")
  exit(0)

for s in slaves:
  sock.sendto(str.encode(sys.argv[1]), s)

