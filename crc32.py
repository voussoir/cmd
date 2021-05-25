import argparse
import os
import sys
import zlib

from voussoirkit import pipeable
from voussoirkit import winglob

def crc32_argparse(args):
    files = (
        file
        for pattern in pipeable.input_many(args.patterns)
        for file in winglob.glob(pattern)
        if os.path.isfile(file)
    )
    for file in files:
        try:
            with open(file, 'rb') as handle:
                crc = zlib.crc32(handle.read())
            print(hex(crc)[2:].rjust(8, '0'), file)
        except Exception as e:
            print(file, e)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns', nargs='+')
    parser.set_defaults(func=crc32_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
