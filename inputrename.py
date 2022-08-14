'''
Given a target string to replace, rename files by prompting the user for input.
'''
import argparse
import os
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

@pipeable.ctrlc_return1
def inputrename_argparse(args):
    cwd = pathclass.cwd()
    if args.recurse:
        files = cwd.walk_files()
    else:
        files = cwd.listdir_files()
    files = (file for file in files if args.keyword in file.basename)
    files = sorted(files)

    prev = None
    for file in files:
        pipeable.stderr(file.relative_path)
        this = input('> ')
        if this == '' and prev is not None:
            this = prev
        if this:
            new_name = file.basename.replace(args.keyword, this)
            new_name = file.parent.with_child(new_name)
            os.rename(file, new_name)
        prev = this

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('keyword')
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=inputrename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
