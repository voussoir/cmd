import os
import send2trash

from voussoirkit import pipeable

for line in pipeable.go():
    if os.path.isfile(line):
        print('Recycling', line)
        send2trash.send2trash(line)
    else:
        print('Not a file', line)
