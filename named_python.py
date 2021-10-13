'''
named_python
============

Because Python is interpreted, when you look at the task manager / process list
you'll see that every running python instance has the same name, python.exe.
This script helps you name the executables so they stand out.

For the time being this script doesn't automatically call your new exe, you
have to write a second command to actually run it. I tried using
subprocess.Popen to spawn the new python with the rest of argv but the behavior
was different on Linux and Windows and neither was really clean.

> named_python name

Examples:
> named_python myserver && python-myserver server.py --port 8080
> named_python hnarchive && python-hnarchive hnarchive.py livestream
'''
import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import winwhich

def namedpython_argparse(args):
    this_python = pathclass.Path(sys.executable)

    base = this_python.replace_extension('').basename.split('-', 1)[0]
    name = args.name.strip()
    extension = this_python.extension.with_dot
    named_python = this_python.parent.with_child(f'{base}-{name}{extension}')
    if named_python.exists:
        return 0

    os.link(this_python.absolute_path, named_python.absolute_path)
    print(named_python.absolute_path)
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('name')
    parser.set_defaults(func=namedpython_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
