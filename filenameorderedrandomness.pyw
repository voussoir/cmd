'''
Drag multiple files on top of this .py file. The first file will have its
name randomly scrambled into 12 digits. The others will increment that number b
1.
'''

import os
import random
import string
import sys

from voussoirkit import pathclass
from voussoirkit import winglob

argv = sys.argv[1:]

randname = [random.choice(string.digits) for x in range(12)]
randname = int(''.join(randname))
for pattern in argv:
    for path in winglob.glob(pattern):
        path = pathclass.Path(path)
        newname = str(randname).rjust(12, '0') + path.dot_extension
        randname += 1
        newname = path.parent.with_child(newname)
        os.rename(path.absolute_path, newname.absolute_path)
        print('%s -> %s' % (path.absolute_path, newname.basename))
