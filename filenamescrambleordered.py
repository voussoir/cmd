'''
Drag multiple files on top of this .py file. The first file will have its
name randomly scrambled into 12 digits. The others will increment that number
by 1.
'''

import os
import random
import string
import sys

from voussoirkit import pathclass

argv = sys.argv[1:]

randname = [random.choice(string.digits) for x in range(12)]
randname = int(''.join(randname))

for path in sorted(pathclass.glob_many(argv), key=pathclass.natural_sorter):
    newname = str(randname).rjust(12, '0') + path.dot_extension
    randname += 1
    newname = path.parent.with_child(newname)
    os.rename(path, newname)
    print('%s -> %s' % (path.absolute_path, newname.basename))
