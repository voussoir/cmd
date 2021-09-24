import os
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def windows():
    paths = os.getenv('PATH').strip(' ;').split(';')
    paths = (pathclass.Path(p) for p in paths)
    paths = (p for p in paths if p.is_dir)

    extensions = os.getenv('PATHEXT').split(';')

    files = (file for path in paths for file in path.listdir())
    executables = (file for file in files if file.extension in extensions)
    yield from executables

def linux():
    paths = os.getenv('PATH').strip(' :').split(':')
    paths = (pathclass.Path(p) for p in paths)
    paths = (p for p in paths if p.is_dir)

    files = (file for path in paths for file in path.listdir())
    executables = (file for file in files if os.access(file.absolute_path, os.X_OK))
    yield from executables

def main(argv):
    if os.name == 'nt':
        executables = windows()
    else:
        executables = linux()

    for executable in executables:
        pipeable.stdout(executable.absolute_path)

    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
