'''
Drag a file on top of this .py file, and it will have its
filename scrambled into a combination of upper and lowercase letters.
'''

import os
import random
import string
import sys

from voussoirkit import pathclass

argv = sys.argv[1:]

for path in pathclass.glob_many(argv):
    newname = [random.choice(string.ascii_lowercase) for x in range(9)]
    newname = ''.join(newname) + path.dot_extension
    newname = path.parent.with_child(newname)
    os.rename(path.absolute_path, newname.absolute_path)
    print('%s -> %s' % (path.absolute_path, newname.basename))
