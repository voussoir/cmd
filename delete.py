import os
import shutil
import sys

from voussoirkit import pipeable
from voussoirkit import winglob

for pattern in pipeable.go(skip_blank=True):
    for name in winglob.glob(pattern):
        if os.path.isfile(name):
            pipeable.output(name)
            os.remove(name)
        elif os.path.isdir(name):
            pipeable.output(name)
            shutil.rmtree(name)
