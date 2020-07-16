'''
Find time, filesize, or bitrate, given two of the three.

For example:

kbps.py --time 1:00:00 --size 2g
kbps.py --time 1:00:00 --kbps 4660
kbps.py --size 2g --kpbps 4660
'''
import argparse
import sys

from voussoirkit import bytestring
from voussoirkit import hms

def kbps(time=None, size=None, kbps=None):
    if [time, size, kbps].count(None) != 1:
        raise ValueError('Incorrect number of unknowns.')

    if time is None:
        size = bytestring.parsebytes(size)
        kilobits = size / 128
        time = kilobits / int(kbps)
        return time

    if size is None:
        seconds = hms.hms_to_seconds(time)
        kibs = int(kbps) / 8
        size = kibs * 1024
        size *= seconds
        return size

    if kbps is None:
        seconds = hms.hms_to_seconds(time)
        size = bytestring.parsebytes(size)
        kibs = size / 1024
        kilobits = kibs * 8
        kbps = kilobits / seconds
        return kbps

def kbps_argparse(args):
    result = kbps(time=args.time, size=args.size, kbps=args.kbps)
    if args.time is None:
        print(hms.seconds_to_hms(time))
    if args.size is None:
        print(bytestring.bytestring(size))
    if args.kbps is None:
        print('%d kbps' % round(result))

def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--time', dest='time', default=None)
    parser.add_argument('-s', '--size', dest='size', default=None)
    parser.add_argument('-k', '--kbps', dest='kbps', default=None)
    parser.set_defaults(func=kbps_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
