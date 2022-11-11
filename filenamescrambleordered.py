'''
Drag multiple files on top of this .py file. The first file will have its
name randomly scrambled into 12 digits. The others will increment that number
by 1.
'''

import argparse
import os
import random
import string
import sys

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'filenamescrambleordered')

def filenamescrambleordered_argparse(args):
    length = int(args.length)
    randname = [random.choice(string.digits) for x in range(length)]
    randname = int(''.join(randname))

    for path in sorted(pathclass.glob_many(args.patterns), key=pathclass.natural_sorter):
        newname = str(randname).rjust(length, '0') + path.dot_extension
        randname += 1
        newname = path.parent.with_child(newname)
        os.rename(path, newname)
        print('%s -> %s' % (path.absolute_path, newname.basename))

    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('patterns', nargs='+')
    parser.add_argument('--length', default=12)
    parser.set_defaults(func=filenamescrambleordered_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
