import argparse
import os
import random
import re
import sys
import unicodedata

from voussoirkit import betterhelp
from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import safeprint
from voussoirkit import spinal
from voussoirkit import stringtools

# These constants are provided for use in your eval string
cwd = pathclass.cwd()

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

def natural_sorter(x):
    '''
    Thank you Mark Byers
    http://stackoverflow.com/a/11150413
    '''
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split(r'([0-9]+)', key)]
    return alphanum_key(x)

def unicode_normalize(s):
    return unicodedata.normalize('NFC', s)

def brename(transformation, autoyes=False, do_naturalsort=False, recurse=False):
    if recurse:
        walker = spinal.walk('.', yield_files=True, yield_directories=True)
        olds = list(walker)
    else:
        olds = cwd.listdir()

    if do_naturalsort:
        olds.sort(key=lambda x: natural_sorter(x.absolute_path))
    else:
        olds.sort()

    pairs = []
    for (index, old) in enumerate(olds):
        # These variables are assigned so that you can use them in your
        # transformation string.
        x = old.basename
        parent = old.parent
        noext = old.replace_extension('').basename
        ext = old.extension.no_dot
        dot_ext = old.extension.with_dot
        index1 = index + 1

        new = eval(transformation)
        new = parent.with_child(new)
        if new.basename == old.basename:
            continue
        pairs.append((old, new))

    if not pairs:
        print('Nothing to replace')
        return

    loop(pairs, dry=True)

    if not (autoyes or interactive.getpermission('Is this correct?')):
        return

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
            line = f'{old.absolute_path}\n{new.absolute_path}\n'
            safeprint.safeprint(line)
        else:
            os.rename(old, new)

def brename_argparse(args):
    return brename(
        args.transformation,
        autoyes=args.autoyes,
        do_naturalsort=args.naturalsort,
        recurse=args.recurse,
    )

def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Batch rename files by providing a string to be `eval`ed, using variable `x` as
        the current filename. Yes I know this is weird, but for certain tasks it's just
        too quick and easy to pass up.
        ''',
    )
    parser.examples = [
        {'args': ['f\'Test_{x}\''], 'comment': 'Prefix all the files'},
        {'args': ['f\'{index1:>03}{dot_ext}\''], 'comment': 'Rename files to their index with 0 padding'},
        {'args': ['(x.split(space)[0] + dot_ext) if space in x else x'], 'comment': 'Keep the first word and extension'},
    ]
    parser.add_argument(
        'transformation',
        help='''
        A string which will be evaluated by Python's eval. The name of the file or
        folder will be in the variable `x`. In addition, many other variables are
        provided for your convenience:
        `quote` ("), `apostrophe` (') so you don't have to escape command quotes.
        `hyphen` (-) because leading hyphens often cause problems with argparse.
        `stringtools` entire stringtools module. See voussoirkit/stringtools.py.
        `space` ( ), `dot` (.), `underscore` (_) so you don't have to add quotes to
        your command while using these common characters.
        `index` the file's index within the loop.
        `index1` the file's index+1, in case you want your names to start from 1.
        `parent` a pathclass.Path object for the directory containing the file.
        `cwd` a pathclass.Path object for the cwd of this program session.
        `noext` the name of the file, but without its extension.
        `ext` the file's extension, with no dot.
        `dot_ext` the file's extension, with dot.
        ''',
    )
    parser.add_argument(
        '-y',
        '--yes',
        dest='autoyes',
        action='store_true',
        help='''
        Accept the results without confirming.
        ''',
    )
    parser.add_argument(
        '--recurse',
        action='store_true',
        help='''
        Recurse into subfolders and rename those files too.
        ''',
    )
    parser.add_argument(
        '--naturalsort',
        action='store_true',
        help='''
        Before renaming, the files will be sorted using natural sort instead of the
        default lexicographic sort. Natural sort means that "My file 20" will come
        before "My file 100" because 20<100. Lexicographic sort means 100 will come
        first because 1 is before 2.
        The purpose of this flag is so your index and index1 variables are applied
        in the order you desire.
        ''',
    )
    parser.set_defaults(func=brename_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
