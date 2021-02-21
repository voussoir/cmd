import argparse
import sys

from voussoirkit import gentools
from voussoirkit import pipeable

def groupsof_argparse(args):
    lines = pipeable.input(args.source, read_files=True, strip=True, skip_blank=True)
    
    chunks = gentools.chunk_generator(lines, args.chunk_size)
    for chunk in chunks:
        chunk = args.separator.join(chunk)
        pipeable.output(chunk)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('chunk_size', type=int)
    parser.add_argument('--separator', default=',')
    parser.set_defaults(func=groupsof_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
