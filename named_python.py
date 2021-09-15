'''
Because Python is interpreted, when you look at the task manager process list
you'll see that every running python instance has the same name, python.exe.
This scripts helps you name the executables so they stand out.

For the time being this script doesn't automatically call your new exe, you
have to write a second command to actually run it. I tried using
subprocess.Popen to spawn the new python with the rest of argv but the behavior
was different on Linux and Windows and neither was really clean.
'''
import os
import sys

from voussoirkit import pathclass
from voussoirkit import winwhich

def main(argv):
    python = pathclass.Path(winwhich.which('python'))

    name = argv[0].strip()

    named_python = python.parent.with_child(f'python-{name}{python.extension.with_dot}')
    if named_python.exists:
        return 0

    os.link(python.absolute_path, named_python.absolute_path)
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
