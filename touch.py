'''
Create the file, or update the last modified timestamp.
'''
import os
import sys

from voussoirkit import clipext
from voussoirkit import safeprint
from voussoirkit import winglob

def touch(glob_pattern):
    filenames = winglob.glob(glob_pattern)
    if len(filenames) == 0:
        safeprint.safeprint(glob_pattern)
        open(glob_pattern, 'a').close()
    else:
        for filename in filenames:
            safeprint.safeprint(filename)
            os.utime(filename)

if __name__ == '__main__':
    glob_patterns = [clipext.resolve(x).strip() for x in sys.argv[1:]]
    for glob_pattern in glob_patterns:
        touch(glob_pattern)
