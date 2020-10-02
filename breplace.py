'''
Batch rename files by replacing the first argument with the second.

Note: If one of your arguments begins with a hyphen, it will confuse argparse
and it will say "the following arguments are required". You have to add "--"
before your from/to arguments, like this:

breplace -- " - Copy" "-copy"
'''
import argparse
import brename
import sys

def breplace_argparse(args):
    if args.regex:
        command = f're.sub(r"{args.replace_from}", r"{args.replace_to}", x)'
    else:
        command = f'x.replace("{args.replace_from}", "{args.replace_to}")'
    brename.brename(command, autoyes=args.autoyes, recurse=args.recurse)

def main(argv):
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('replace_from')
    parser.add_argument('replace_to')
    parser.add_argument('-y', '--yes', dest='autoyes', action='store_true', help='accept results without confirming')
    parser.add_argument('--recurse', dest='recurse', action='store_true', help='operate on subdirectories also')
    parser.add_argument('--regex', dest='regex', action='store_true', help='treat arguments as regular expressions')
    parser.set_defaults(func=breplace_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
