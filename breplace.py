'''
Batch rename files by replacing the first argument with the second.
'''
import argparse
import brename
import sys

def breplace_argparse(args):
    command = f'x.replace("{args.replace_from}", "{args.replace_to}")'
    brename.brename(command, autoyes=args.autoyes, recurse=args.recurse)

def main(argv):
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('replace_from')
    parser.add_argument('replace_to')
    parser.add_argument('-y', '--yes', dest='autoyes', action='store_true', help='accept results without confirming')
    parser.add_argument('--recurse', dest='recurse', action='store_true', help='operate on subdirectories also')
    parser.set_defaults(func=breplace_argparse)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
