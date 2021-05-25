import os
import shutil

from voussoirkit import pipeable
from voussoirkit import winglob

for pattern in pipeable.go(skip_blank=True):
    for name in winglob.glob(pattern):
        if os.path.isfile(name):
            pipeable.stdout(name)
            os.remove(name)
        elif os.path.isdir(name):
            pipeable.stdout(name)
            shutil.rmtree(name)
