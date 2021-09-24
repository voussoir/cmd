'''
Convert LF line endings to CRLF.
'''
import argparse
import sys

from voussoirkit import pathclass
from voussoirkit import pipeable

CR = b'\x0D'
LF = b'\x0A'
CRLF = CR + LF

def crlf(file):
    with file.open('rb') as handle:
        content = handle.read()

    original = content
    content = content.replace(CRLF, LF)
    content = content.replace(LF, CRLF)
    if content == original:
        return

    with file.open('wb') as handle:
        handle.write(content)

def crlf_argparse(args):
    patterns = pipeable.input_many(args.patterns, skip_blank=True, strip=True)
    files = pathclass.glob_many(patterns)
    for file in files:
        crlf(file)
        pipeable.stdout(file)

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('patterns')
    parser.set_defaults(func=crlf_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
