'''
Given a target string to replace, rename files by prompting the user for input.
'''
import argparse
import os
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal

@pipeable.ctrlc_return1
def inputrename_argparse(args):
    if args.recurse:
        files = (file for file in spinal.walk('.') if args.keyword in file.basename)
    else:
        files = (file for file in pathclass.cwd().listdir() if args.keyword in file.basename)
    prev = None
    for file in files:
        print(file.relative_path)
        this = input('> ')
        if this == '' and prev is not None:
            this = prev
        if this:
            new_name = file.basename.replace(args.keyword, this)
            new_name = file.parent.with_child(new_name)
            os.rename(file.absolute_path, new_name.absolute_path)
        prev = this

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('keyword')
    parser.add_argument('--recurse', action='store_true')
    parser.set_defaults(func=inputrename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
