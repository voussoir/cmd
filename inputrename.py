'''
Given a target string to replace, rename files by prompting the user for input.
'''
import argparse
import os
import sys

from voussoirkit import pipeable

@pipeable.ctrlc_return1
def inputrename_argparse(args):
    files = (file for file in os.listdir() if args.keyword in file)
    prev = None
    for file in files:
        print(file)
        this = input('> ')
        if this == '' and prev is not None:
            this = prev
        if this:
            os.rename(file, file.replace(args.keyword, this))
        prev = this

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('keyword')
    parser.set_defaults(func=inputrename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
