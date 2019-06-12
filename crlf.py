'''
Convert LF line endings to CRLF.
'''

import glob
import sys

from voussoirkit import pipeable


CR = b'\x0D'
LF = b'\x0A'
CRLF = CR + LF

def crlf(filename):
    with open(filename, 'rb') as handle:
        content = handle.read()
    content = content.replace(CRLF, LF)
    content = content.replace(LF, CRLF)
    with open(filename, 'wb') as handle:
        handle.write(content)

def main(args):
    for line in pipeable.go(args, strip=True, skip_blank=True):
        for filename in glob.glob(line):
            pipeable.output(filename)
            crlf(filename)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

