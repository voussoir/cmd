'''
Batch rename files by providing a string to be `eval`ed, using variable `x` as
the current filename.
Yes I know this is weird, but for certain tasks it's just too quick and easy to pass up.

For example:

Prefix all the files:
brename.py "'Test_' + x"

Keep the first word and extension:
brename.py "(x.split(' ')[0] + '.' + x.split('.')[-1]) if ' ' in x else x"
'''
import argparse
import os
import random
import re
import sys
import unicodedata

from voussoirkit import interactive
from voussoirkit import safeprint
from voussoirkit import spinal
from voussoirkit import stringtools

# These variables are provided so that if you have any difficulty typing
# literal quotes etc into your command line, you can just use these variable
# names in your eval string.
apostrophe = "'"
dot = '.'
hyphen = '-'
quote = '"'
space = ' '
underscore = '_'

# For backwards compatibility, these names which were once locally defined
# functions are now just references to stringtools.
excise = stringtools.excise
title = stringtools.title_capitalize

def unicode_normalize(s):
    return unicodedata.normalize('NFC', s)

def brename(transformation, autoyes=False, recurse=False):
    if recurse:
        walker = spinal.walk_generator('.', yield_files=True, yield_directories=True)
        olds = [x.absolute_path for x in walker]
    else:
        olds = [os.path.join(os.getcwd(), x) for x in os.listdir('.')]

    pairs = []
    for (index, old) in enumerate(olds):
        new = old
        directory = os.path.dirname(new)
        basename = os.path.basename(new)
        new = basename

        # These variables are assigned so that you can use them in your
        # transformation string.
        (noext, ext) = os.path.splitext(basename)
        x = new
        extension = ext
        index1 = index + 1

        new = eval(transformation)
        new = os.path.join(directory, new)
        if new == old:
            continue
        pairs.append((old, new))

    if not pairs:
        print('Nothing to replace')
        return

    loop(pairs, dry=True)

    if autoyes or interactive.getpermission('Is this correct?'):
        # Sort in reverse so that renaming a file inside a directory always
        # occurs before renaming the directory itself. If you rename the
        # directory first, then the path to the file is invalid by the time
        # you want to rename it.
        pairs = sorted(pairs, reverse=True)
        loop(pairs, dry=False)

def longest_length(li):
    longest = 0
    for item in li:
        longest = max(longest, len(item))
    return longest

def loop(pairs, dry=False):
    for (old, new) in pairs:
        if dry:
            line = f'{old}\n{new}\n'
            safeprint.safeprint(line)
        else:
            os.rename(old, new)

def brename_argparse(args):
    brename(args.transformation, autoyes=args.autoyes, recurse=args.recurse)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('transformation', help='python command using x as variable name')
    parser.add_argument('-y', '--yes', dest='autoyes', action='store_true', help='accept results without confirming')
    parser.add_argument('--recurse', dest='recurse', action='store_true', help='operate on subdirectories also')
    parser.set_defaults(func=brename_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
