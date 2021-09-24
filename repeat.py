'''
Repeat the input as many times as you want.

> repeat "hello" 8

> repeat "yowza" inf

> echo hi | repeat !i 4
'''
import argparse
import sys

from voussoirkit import pipeable

def repeat_inf(text):
    try:
        while True:
            pipeable.stdout(text)
    except KeyboardInterrupt:
        return 0

def repeat_times(text, times):
    try:
        times = int(times)
    except ValueError:
        pipeable.stderr('times should be an integer >= 1.')
        return 1

    if times < 1:
        pipeable.stderr('times should be >= 1.')
        return 1

    try:
        for t in range(times):
            pipeable.stdout(text)
    except KeyboardInterrupt:
        return 1

def repeat_argparse(args):
    text = pipeable.input(args.text, split_lines=False)
    if args.times == 'inf':
        return repeat_inf(text)
    else:
        return repeat_times(text, args.times)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('text')
    parser.add_argument('times')
    parser.set_defaults(func=repeat_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
