import os
import send2trash

from voussoirkit import pipeable

for line in pipeable.go():
    if os.path.isfile(line):
        pipeable.stdout(line)
        send2trash.send2trash(line)
    else:
        pipeable.stderr(f'Not a file {line}')
