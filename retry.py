import argparse
import subprocess
import sys
import time

class NoMoreRetries(Exception):
    pass

def normalize_limit(limit):
    if limit is not None:
        limit = int(limit)
        if limit < 1:
            raise ValueError('Limit must be >= 1, or None.')
    return limit

def normalize_sleepy(sleepy):
    if sleepy is not None:
        sleepy = float(sleepy)
        if sleepy <= 0:
            raise ValueError('Sleep must be > 0, or None.')
    return sleepy

def retry(command, limit, sleepy):
    limit = normalize_limit(limit)
    sleepy = normalize_sleepy(sleepy)
    status = 1
    while limit is None or limit > 0:
        status = subprocess.run(command, shell=True).returncode
        if status == 0:
            return
        print(f'{command} failed with status {status}.')
        if limit is not None:
            limit -= 1
        if sleepy is not None:
            time.sleep(sleepy)
    raise NoMoreRetries()

def retry_argparse(args):
    return retry(
        command=args.command,
        limit=args.limit,
        sleepy=args.sleep,
    )

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('command', nargs='+')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--sleep', type=float, default=None)
    parser.set_defaults(func=retry_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
