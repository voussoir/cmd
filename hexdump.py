import argparse
import sys

DEFAULT_WIDTH = 16

def hexy(i, width=0):
    return hex(i)[2:].upper().rjust(width, '0')

def hexdump(handle, width=DEFAULT_WIDTH, ellipse=False, start=None, end=None):
    if start is not None:
        start = int(start, 16)
        handle.seek(start)
        address = start
    else:
        address = 0
    if end is not None:
        end = int(end, 16)

    did_ellipse = False
    previous_line = None
    while True:
        if end is not None:
            if address > end:
                break
            this_width = min(width, end - address)
        else:
            this_width = width
        line = handle.read(this_width)
        if not line:
            break
        line = [hexy(x, 2) for x in line]
        line = ' '.join(line)
        if ellipse:
            if line == previous_line:
                if not did_ellipse:
                    print('...')
                    did_ellipse = True
                address += width
                continue
            previous_line = line
        print('%s | ' % hexy(address, 8), end='', flush=False)
        print(line)
        address += width

def hexdump_argparse(args):
    handle = open(args.filename, 'rb')
    return hexdump(handle, width=args.width, ellipse=args.ellipse, start=args.start, end=args.end)

def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('filename')
    parser.add_argument('--width', default=DEFAULT_WIDTH, type=int)
    parser.add_argument('--start', default=None)
    parser.add_argument('--end', default=None)
    parser.add_argument('--ellipse', action='store_true')
    parser.set_defaults(func=hexdump_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
