'''
Repeat the input as many times as you want.

> repeat "hello" 8
> echo hi | repeat !i 4
'''
import argparse
import sys

from voussoirkit import pipeable

def repeat_argparse(args):
    text = pipeable.input(args.text, split_lines=False)
    if args.times == 'inf':
        try:
            while True:
                print(text)
        except KeyboardInterrupt:
            return 0
    else:
        try:
            times = int(args.times)
        except ValueError:
            pipeable.stderr('times should be an integer >= 1.')
            return 1

        if times < 1:
            pipeable.stderr('times should be >= 1.')
            return 1

        try:
            for t in range(times):
                print(text)
        except KeyboardInterrupt:
            return 1

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('text')
    parser.add_argument('times')
    parser.set_defaults(func=repeat_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
