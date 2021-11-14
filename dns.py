import socket
import sys
domain = sys.argv[1]

print(socket.gethostbyname(domain))
