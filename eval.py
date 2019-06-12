import glob
import math
import os
import random
import re
import sys

from voussoirkit import pipeable


lines = pipeable.input(sys.argv[1])
pattern = sys.argv[2]

def quote(s):
    return '"%s"' % s

def apostrophe(s):
    return "'%s'" % s

def random_hex(length=12):
    randbytes = os.urandom(math.ceil(length / 2))
    token = ''.join('{:02x}'.format(x) for x in randbytes)
    token = token[:length]
    return token

for line in lines:
    x = line
    pipeable.output(eval(pattern))
