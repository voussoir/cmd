import sys

from voussoirkit import pipeable

for line in pipeable.go():
    line = ''.join('&#%d;' % ord(c) for c in line)
    print(line)
