'''
Drag a file on top of this .py file, and it will have its
filename scrambled into a combination of 12 digits.
'''

import os
import random
import string
import sys

from voussoirkit import pathclass
from voussoirkit import winglob

argv = sys.argv[1:]

for pattern in argv:
    for path in winglob.glob(pattern):
        path = pathclass.Path(path)
        newname = [random.choice(string.digits) for x in range(12)]
        newname = ''.join(newname) + path.dot_extension
        newname = path.parent.with_child(newname)
        os.rename(path.absolute_path, newname.absolute_path)
        print('%s -> %s' % (path.absolute_path, newname.basename))
