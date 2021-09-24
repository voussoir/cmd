'''
Move all of the files into the destination directory, aborting the operation if
even a single file collides with a file in the destination.
'''
import argparse
import shutil
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

def moveall_argparse(args):
    patterns = pipeable.input(args.source, skip_blank=True, strip=True)
    files = pathclass.glob_many(patterns)

    destination = pathclass.Path(args.destination)
    try:
        destination.assert_is_directory()
    except pathclass.NotDirectory:
        pipeable.stderr('destination must be a directory.')
        return 1

    pairs = []
    fail = False
    for file in files:
        new_path = destination.with_child(file.basename)
        if new_path.exists:
            pipeable.stderr(f'{file.basename} cannot be moved.')
            fail = True
            continue
        pairs.append((file, new_path))

    if fail:
        return 1

    for (file, new_path) in pairs:
        pipeable.stdout(new_path.absolute_path)
        shutil.move(file.absolute_path, new_path.absolute_path)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('destination')
    parser.set_defaults(func=moveall_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
