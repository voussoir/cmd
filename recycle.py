import send2trash
import sys

from voussoirkit import winglob

for pattern in sys.argv[1:]:
    for file in winglob.glob(pattern):
        print(file)
        send2trash.send2trash(file)
