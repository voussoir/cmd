import argparse
import os
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.get_logger(__name__, 'prune_dirs')

def prune_dirs(starting):
    starting = pathclass.Path(starting)
    walker = spinal.walk(starting, yield_directories=True, yield_files=False)
    directories = list(walker)

    double_check = set()

    def pruneme(directory):
        log.debug('Checking %s.', directory.absolute_path)
        if directory == starting or directory not in starting:
            return
        if len(directory.listdir()) == 0:
            pipeable.stdout(directory.absolute_path)
            os.rmdir(directory)
            double_check.add(directory.parent)

    for directory in directories:
        pruneme(directory)

    while double_check:
        directory = double_check.pop()
        pruneme(directory)

def prune_dirs_argparse(args):
    return prune_dirs(args.starting)

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        This program deletes all empty directories which are children of the given
        starting directory. The starting directory itself will not be deleted even
        if it is empty.
        ''',
    )
    parser.add_argument('starting')
    parser.set_defaults(func=prune_dirs_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
