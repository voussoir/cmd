'''
directory_discrepancy
=====================

This program compares two directory and shows which files exist in each
directory that do not exist in the other.

> directory_discrepancy dir1 dir2

flags:
--recurse:
    Also check subdirectories.
'''
import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import operatornotify
from voussoirkit import spinal
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'directory_discrepancy')

def helper(root, recurse):
    root = pathclass.Path(root)
    walk = spinal.walk(root, recurse=recurse, yield_directories=True, yield_files=True)
    for path in walk:
        relative = path.relative_to(root)
        yield relative

def directory_discrepancy_argparse(args):
    files1 = set(helper(args.dir1, recurse=args.recurse))
    files2 = set(helper(args.dir2, recurse=args.recurse))

    print(f'In "{args.dir1}" but not in "{args.dir2}":')
    print('=============================')
    for discrepancy in sorted(files1.difference(files2)):
        print(discrepancy)

    print()

    print(f'In "{args.dir2}" but not in "{args.dir1}":')
    print('=============================')
    for discrepancy in sorted(files2.difference(files1)):
        print(discrepancy)


def main(argv):
    argv = vlogging.set_level_by_argv(log, argv)

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('dir1')
    parser.add_argument('dir2')
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=directory_discrepancy_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
