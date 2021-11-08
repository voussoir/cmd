import argparse
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable

def inodes_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = pathclass.glob_many_files(patterns)
    for file in files:
        pipeable.stdout(f'{file.stat.st_dev} {file.stat.st_ino} {file.relative_path}')
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.set_defaults(func=inodes_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
