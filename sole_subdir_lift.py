'''
This program takes a directory and does the following: If that directory
contains nothing but a single child directory, then the contents of that child
will be moved to the parent, and the empty child will be deleted.
'''
import argparse
import os
import shutil
import sys

from voussoirkit import passwordy
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import winglob

def sole_lift(starting):
    starting = pathclass.Path(starting)
    children = starting.listdir()
    if len(children) != 1:
        return

    child = children[0]

    if not child.is_dir:
        return

    temp_dir = starting.with_child(passwordy.urandom_hex(32))
    os.rename(child.absolute_path, temp_dir.absolute_path)
    for grandchild in temp_dir.listdir():
        shutil.move(grandchild.absolute_path, starting.absolute_path)

    if temp_dir.listdir():
        raise Exception()

    os.rmdir(temp_dir.absolute_path)

def sole_lift_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    directories = (pathclass.Path(d) for pattern in patterns for d in winglob.glob(pattern))
    directories = (d for d in directories if d.is_dir)
    for directory in directories:
        sole_lift(directory)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+', default='.')
    parser.set_defaults(func=sole_lift_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
