'''
getpid
======

Get PIDs for running processes that match the given process name.

Error level will be 0 if any processes are found, 1 if none are found.

> getpid process_name

Examples:
> getpid python.exe
> getpid chrome.exe
'''
import argparse
import psutil
import sys

from voussoirkit import betterhelp
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'getpid')

def getpid_argparse(args):
    status = 1
    target = args.process_name.lower()
    for process in psutil.process_iter():
        if process.name().lower() == target:
            print(process.pid)
            status = 0
    return status

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('process_name')
    parser.set_defaults(func=getpid_argparse)

    return betterhelp.single_main(argv, parser, __doc__)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
