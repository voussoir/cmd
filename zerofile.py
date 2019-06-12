import argparse
import os
import sys

from voussoirkit import bytestring


filename = os.path.abspath(sys.argv[1])


def zerofile(filename, length):
    if os.path.exists(filename):
        raise ValueError(f'{filename} already exists.')

    with open(filename, 'wb') as handle:
        handle.seek(length - 1)
        handle.write(bytes([0]))

def zerofile_argparse(args):
    return zerofile(
        filename=args.filename,
        length=bytestring.parsebytes(args.length),
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('filename')
    parser.add_argument('length')
    parser.set_defaults(func=zerofile_argparse)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
