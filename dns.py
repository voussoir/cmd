import socket
import sys
domain = sys.argv[1]

print(socket.getaddrinfo(domain, 53)[0][4][0])
