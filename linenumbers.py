import argparse
import sys

from voussoirkit import pipeable

def linenumbers_argparse(args):
    lines = pipeable.input(args.source, read_files=True)
    if args.lazy:
        form = '{no} | {line}'
    else:
        lines = list(lines)
        digits = len(str(len(lines)))
        form = '{no:>0%d} | {line}' % digits
    for (index, line) in enumerate(lines):
        pipeable.stdout(form.format(no=index+1, line=line))

    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source')
    parser.add_argument('--lazy', action='store_true')
    parser.set_defaults(func=linenumbers_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
