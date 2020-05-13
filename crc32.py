import sys
import zlib

from voussoirkit import winglob

patterns = sys.argv[1:]
files = [file for pattern in patterns for file in winglob.glob(pattern)]
for file in files:
    with open(file, 'rb') as handle:
        crc = zlib.crc32(handle.read())
    print(hex(crc)[2:].rjust(8, '0'), file)
