import os

from voussoirkit import pipeable

for line in pipeable.go():
    if os.path.isfile(line):
        print('Deleting', line)
        os.remove(line)
    else:
        print('Not a file', line)
