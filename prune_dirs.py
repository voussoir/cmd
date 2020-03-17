'''
This program deletes all empty directories which are children of the given
starting directory. The starting directory itself will not be deleted even
if it is empty.

> prune_dirs .
> prune_dirs C:\\somepath
'''
import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import spinal
from voussoirkit import pathclass


def prune_dirs(starting):
    starting = pathclass.Path(starting)
    walker = spinal.walk_generator(starting, yield_directories=True, yield_files=False)

    double_check = set()

    def pruneme(directory):
        if directory == starting or directory not in starting:
            return
        if len(directory.listdir()) == 0:
            print(directory.absolute_path)
            os.rmdir(directory.absolute_path)
            double_check.add(directory.parent)

    for directory in walker:
        pruneme(directory)

    while double_check:
        directory = double_check.pop()
        pruneme(directory)


def prune_dirs_argparse(args):
    return prune_dirs(args.starting)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('starting')
    parser.set_defaults(func=prune_dirs_argparse)

    return betterhelp.single_main(argv, parser, docstring=__doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
