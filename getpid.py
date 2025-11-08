import argparse
import psutil
import sys

from voussoirkit import betterhelp
from voussoirkit import subproctools
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'getpid')

def getpid_argparse(args):
    pids = subproctools.getpid(args.process_name)
    status = 0 if len(pids) > 0 else 1
    for pid in pids:
        print(pid)
    return status

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        Get PIDs for running processes that match the given process name.

        Error level will be 0 if any processes are found, 1 if none are found.
        ''',
    )

    parser.add_argument(
        'process_name',
        type=str,
        help='''
        Name like "python.exe" or "chrome" as it appears in your task manager / ps.
        ''',
    )
    parser.set_defaults(func=getpid_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
