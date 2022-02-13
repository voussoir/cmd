import argparse
import os
import sys

from voussoirkit import interactive
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import spinal
from voussoirkit import winglob

def filepull(pull_from='.', globs=None, autoyes=False):
    start = pathclass.Path(pull_from)
    files = [
        file
        for d in start.listdir_directories()
        for file in spinal.walk(d, glob_filenames=globs)
    ]

    if len(files) == 0:
        pipeable.stderr('No files to move')
        return 1

    duplicate_count = {}
    for f in files:
        basename = f.basename
        duplicate_count.setdefault(basename, [])
        duplicate_count[basename].append(f.absolute_path)

    duplicates = [
        '\n'.join(sorted(copies))
        for (basename, copies) in duplicate_count.items()
        if len(copies) > 1
    ]
    duplicates = sorted(duplicates)
    if len(duplicates) > 0:
        raise Exception('duplicate names:\n' + '\n'.join(duplicates))

    for f in files:
        pipeable.stdout(f.basename)

    if autoyes or interactive.getpermission(f'Move {len(files)} files?'):
        for f in files:
            local = os.path.join('.', f.basename)
            os.rename(f, local)
        return 0
    else:
        return 1

def filepull_argparse(args):
    return filepull(pull_from=args.pull_from, globs=args.glob, autoyes=args.autoyes)

def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Pull all of the files in nested directories into the current directory.
        ''',
    )

    parser.add_argument('pull_from', nargs='?', default='.')
    parser.add_argument(
        '--glob',
        nargs='+',
        help='''
        Only pull files whose basename matches any of these glob patterns.
        ''',
    )
    parser.add_argument('-y', '--yes', dest='autoyes', action='store_true')
    parser.set_defaults(func=filepull_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
