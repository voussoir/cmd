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

from voussoirkit import getpermission
from voussoirkit import safeprint
from voussoirkit import spinal

apostrophe = "'"
dot = '.'
hyphen = '-'
quote = '"'
space = ' '
underscore = '_'
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

        new = eval(transformation)
        new = os.path.join(directory, new)
        if new == old:
            continue
        pairs.append((old, new))

    if not pairs:
        print('Nothing to replace')
        return

    loop(pairs, dry=True)

    if autoyes or getpermission.getpermission('Is this correct?'):
        # Sort in reverse so that renaming a file inside a directory always
        # occurs before renaming the directory itself. If you rename the
        # directory first, then the path to the file is invalid by the time
        # you want to rename it.
        pairs = sorted(pairs, reverse=True)
        loop(pairs, dry=False)

def excise(s, mark_left, mark_right):
    '''
    Remove the text between the left and right landmarks, inclusive, returning
    the rest of the text.

    excise('What a wonderful day [soundtrack].mp3', ' [', ']') ->
    returns 'What a wonderful day.mp3'
    '''
    if mark_left in s and mark_right in s:
        return s.split(mark_left)[0] + s.split(mark_right)[-1]
    return s

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

def title(text):
    (text, extension) = os.path.splitext(text)
    text = text.title()
    if ' ' in text:
        (first, rest) = text.split(' ', 1)
    else:
        (first, rest) = (text, '')
    rest = ' %s ' % rest
    for article in ['The', 'A', 'An', 'At', 'To', 'In', 'Of', 'From', 'And']:
        article = ' %s ' % article
        rest = rest.replace(article, article.lower())
    rest = rest.strip()
    if rest != '':
        rest = ' ' + rest
    text = first + rest + extension
    return text

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
