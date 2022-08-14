import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass

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
    parser = argparse.ArgumentParser(
        description='''
        Because Python is interpreted, when you look at the task manager / process list
        you'll see that every running python instance has the same name, python.exe.
        This script helps you name the executables so they stand out.

        For the time being this script doesn't automatically call your new exe, you
        have to write a second command to actually run it. I tried using
        subprocess.Popen to spawn the new python with the rest of argv but the behavior
        was different on Linux and Windows and neither was really clean.
        ''',
    )
    parser.add_argument(
        'name',
        type=str,
        help='''
        If you invoke this script with python.exe, a hardlink python-{name}.exe
        will be created. Also works with pythonw.
        ''',
    )
    parser.set_defaults(func=namedpython_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
