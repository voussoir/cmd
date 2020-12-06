import os
import send2trash
import sys

from voussoirkit import pipeable
from voussoirkit import winglob

for pattern in pipeable.go(skip_blank=True):
    for name in winglob.glob(pattern):
        name = os.path.abspath(name)
        pipeable.output(name)
        send2trash.send2trash(name)
